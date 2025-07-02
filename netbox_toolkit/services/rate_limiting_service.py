from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User, Group
from ..models import CommandLog


class RateLimitingService:
    """Service for managing command execution rate limiting"""
    
    def __init__(self):
        """Initialize the rate limiting service with plugin settings"""
        self.plugin_settings = getattr(settings, 'PLUGINS_CONFIG', {}).get('netbox_toolkit', {})
    
    def is_rate_limiting_enabled(self):
        """Check if rate limiting is enabled in plugin settings"""
        return self.plugin_settings.get('rate_limiting_enabled', False)
    
    def get_device_command_limit(self):
        """Get the maximum number of commands allowed per device within the time window"""
        return self.plugin_settings.get('device_command_limit', 10)
    
    def get_time_window_minutes(self):
        """Get the time window in minutes for rate limiting"""
        return self.plugin_settings.get('time_window_minutes', 5)
    
    def get_bypass_users(self):
        """Get list of usernames that bypass rate limiting"""
        return self.plugin_settings.get('bypass_users', [])
    
    def get_bypass_groups(self):
        """Get list of group names that bypass rate limiting"""
        return self.plugin_settings.get('bypass_groups', [])
    
    def user_bypasses_rate_limiting(self, user):
        """
        Check if a user bypasses rate limiting based on username or group membership
        
        Args:
            user: Django User object
            
        Returns:
            bool: True if user bypasses rate limiting, False otherwise
        """
        # Check if user is in bypass users list
        bypass_users = self.get_bypass_users()
        if user.username in bypass_users:
            return True
        
        # Check if user is in any bypass groups
        bypass_groups = self.get_bypass_groups()
        if bypass_groups:
            user_groups = user.groups.values_list('name', flat=True)
            if any(group in bypass_groups for group in user_groups):
                return True
        
        return False
    
    def get_recent_command_count(self, device, user=None):
        """
        Get the number of successful commands executed on a device within the time window
        
        Args:
            device: Device object
            user: Optional User object to count only commands by this user
            
        Returns:
            int: Number of recent successful commands
        """
        time_window = self.get_time_window_minutes()
        cutoff_time = timezone.now() - timedelta(minutes=time_window)
        
        query = CommandLog.objects.filter(
            device=device,
            execution_time__gte=cutoff_time,
            success=True  # Only count successful commands
        )
        
        if user:
            query = query.filter(username=user.username)
        
        return query.count()
    
    def check_rate_limit(self, device, user):
        """
        Check if a command execution would exceed rate limits
        
        Args:
            device: Device object to check rate limits for
            user: User object attempting to execute the command
            
        Returns:
            dict: {
                'allowed': bool,
                'current_count': int,
                'limit': int,
                'time_window_minutes': int,
                'reason': str (if not allowed)
            }
        """
        # If rate limiting is disabled, always allow
        if not self.is_rate_limiting_enabled():
            return {
                'allowed': True,
                'current_count': 0,
                'limit': self.get_device_command_limit(),
                'time_window_minutes': self.get_time_window_minutes(),
                'reason': 'Rate limiting disabled'
            }
        
        # If user bypasses rate limiting, always allow
        if self.user_bypasses_rate_limiting(user):
            return {
                'allowed': True,
                'current_count': 0,
                'limit': self.get_device_command_limit(),
                'time_window_minutes': self.get_time_window_minutes(),
                'reason': 'User bypasses rate limiting'
            }
        
        # Check current command count
        current_count = self.get_recent_command_count(device)
        limit = self.get_device_command_limit()
        time_window = self.get_time_window_minutes()
        
        if current_count >= limit:
            return {
                'allowed': False,
                'current_count': current_count,
                'limit': limit,
                'time_window_minutes': time_window,
                'reason': f'Rate limit exceeded: {current_count}/{limit} successful commands in last {time_window} minutes'
            }
        
        return {
            'allowed': True,
            'current_count': current_count,
            'limit': limit,
            'time_window_minutes': time_window,
            'reason': 'Within rate limits'
        }
    
    def get_rate_limit_status(self, device, user):
        """
        Get rate limit status for display in UI
        
        Args:
            device: Device object
            user: User object
            
        Returns:
            dict: Rate limit status information for UI display
        """
        if not self.is_rate_limiting_enabled():
            return {
                'enabled': False,
                'message': 'Rate limiting is disabled'
            }
        
        if self.user_bypasses_rate_limiting(user):
            return {
                'enabled': True,
                'bypassed': True,
                'message': 'You have unlimited command execution (bypass enabled)'
            }
        
        current_count = self.get_recent_command_count(device)
        limit = self.get_device_command_limit()
        time_window = self.get_time_window_minutes()
        remaining = max(0, limit - current_count)
        
        # Determine status and appropriate message
        if current_count >= limit:
            status = 'exceeded'
            # Get time until reset for exceeded status
            time_until_reset = self.get_time_until_reset(device)
            if time_until_reset:
                minutes_until_reset = int(time_until_reset.total_seconds() / 60) + 1
                message = f'Rate limit exceeded! ({current_count}/{limit} successful commands) - Try again in {minutes_until_reset} minutes'
            else:
                message = f'Rate limit exceeded! ({current_count}/{limit} successful commands in last {time_window} minutes)'
        elif remaining <= 2 and current_count < limit:  # Only warning if we haven't exceeded the limit
            status = 'warning'
            message = f'{remaining} commands remaining ({current_count}/{limit} successful commands in last {time_window} minutes)'
        else:
            status = 'normal'
            message = f'{remaining} commands remaining ({current_count}/{limit} successful commands in last {time_window} minutes)'
        
        return {
            'enabled': True,
            'bypassed': False,
            'current_count': current_count,
            'limit': limit,
            'remaining': remaining,
            'time_window_minutes': time_window,
            'status': status,
            'message': message,
            'is_exceeded': current_count >= limit,
            'is_warning': remaining <= 2 and current_count < limit,
            'time_until_reset': self.get_time_until_reset(device) if current_count >= limit else None,
        }
    
    def get_time_until_reset(self, device):
        """
        Get the time until the rate limit resets (oldest successful command in window expires)
        
        Args:
            device: Device object
            
        Returns:
            timedelta or None: Time until oldest successful command expires, None if no recent successful commands
        """
        time_window = self.get_time_window_minutes()
        cutoff_time = timezone.now() - timedelta(minutes=time_window)
        
        oldest_command = CommandLog.objects.filter(
            device=device,
            execution_time__gte=cutoff_time,
            success=True  # Only consider successful commands
        ).order_by('execution_time').first()
        
        if not oldest_command:
            return None
        
        reset_time = oldest_command.execution_time + timedelta(minutes=time_window)
        time_until_reset = reset_time - timezone.now()
        
        return time_until_reset if time_until_reset > timedelta(0) else None

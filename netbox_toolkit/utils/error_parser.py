"""Utility for parsing and detecting vendor-specific error messages in command output."""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ErrorType(Enum):
    """Types of errors that can be detected in command output."""
    SYNTAX_ERROR = "syntax_error"
    PERMISSION_ERROR = "permission_error"
    COMMAND_NOT_FOUND = "command_not_found"
    CONFIGURATION_ERROR = "configuration_error"
    TIMEOUT_ERROR = "timeout_error"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class ErrorPattern:
    """Represents an error pattern for a specific vendor."""
    pattern: str
    error_type: ErrorType
    vendor: str
    case_sensitive: bool = False
    description: str = ""

@dataclass
class ParsedError:
    """Result of error parsing."""
    error_type: ErrorType
    vendor: str
    original_message: str
    enhanced_message: str
    guidance: str
    confidence: float  # 0.0 to 1.0, how confident we are this is an error

class VendorErrorParser:
    """Parser for detecting vendor-specific error messages."""
    
    def __init__(self):
        self.error_patterns = self._initialize_error_patterns()
    
    def _initialize_error_patterns(self) -> List[ErrorPattern]:
        """Initialize patterns for various vendor error messages."""
        patterns = [
            # Cisco IOS/IOS-XE Syntax Errors
            ErrorPattern(
                pattern=r"% Invalid input detected at '\^' marker\.",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="cisco_ios",
                description="Invalid command syntax - caret indicates error position"
            ),
            ErrorPattern(
                pattern=r"% Ambiguous command:",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="cisco_ios",
                description="Command is ambiguous - need more specific input"
            ),
            ErrorPattern(
                pattern=r"% Incomplete command\.",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="cisco_ios",
                description="Command is incomplete - missing parameters"
            ),
            ErrorPattern(
                pattern=r"% Unknown command or computer name, or unable to find computer address",
                error_type=ErrorType.COMMAND_NOT_FOUND,
                vendor="cisco_ios",
                description="Command not recognized"
            ),
            
            # Cisco NX-OS Syntax Errors
            ErrorPattern(
                pattern=r"% Invalid command at '\^' marker\.",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="cisco_nxos",
                description="Invalid command syntax"
            ),
            ErrorPattern(
                pattern=r"% Invalid parameter detected at '\^' marker\.",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="cisco_nxos",
                description="Invalid parameter in command"
            ),
            ErrorPattern(
                pattern=r"% Command incomplete\.",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="cisco_nxos",
                description="Command requires additional parameters"
            ),
            
            # Cisco IOS-XR Syntax Errors
            ErrorPattern(
                pattern=r"% Invalid input detected at '\^' marker\.",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="cisco_iosxr",
                description="Invalid command syntax"
            ),
            ErrorPattern(
                pattern=r"% Incomplete command\.",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="cisco_iosxr",
                description="Command is incomplete"
            ),
            
            # Juniper Junos Syntax Errors
            ErrorPattern(
                pattern=r"syntax error, expecting <[\w\-]+>",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="juniper_junos",
                description="Syntax error - expected different keyword"
            ),
            ErrorPattern(
                pattern=r"syntax error\.",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="juniper_junos",
                description="General syntax error"
            ),
            ErrorPattern(
                pattern=r"unknown command\.",
                error_type=ErrorType.COMMAND_NOT_FOUND,
                vendor="juniper_junos",
                description="Command not recognized"
            ),
            ErrorPattern(
                pattern=r"error: .*",
                error_type=ErrorType.UNKNOWN_ERROR,
                vendor="juniper_junos",
                description="General error from device"
            ),
            
            # Arista EOS Syntax Errors
            ErrorPattern(
                pattern=r"% Invalid input",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="arista_eos",
                description="Invalid command input"
            ),
            ErrorPattern(
                pattern=r"% Incomplete command",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="arista_eos",
                description="Command requires additional parameters"
            ),
            ErrorPattern(
                pattern=r"% Ambiguous command",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="arista_eos",
                description="Command is ambiguous"
            ),
            
            # HPE/Aruba Syntax Errors
            ErrorPattern(
                pattern=r"Invalid input:",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="aruba",
                description="Invalid command syntax"
            ),
            ErrorPattern(
                pattern=r"Unknown command\.",
                error_type=ErrorType.COMMAND_NOT_FOUND,
                vendor="aruba",
                description="Command not recognized"
            ),
            
            # Huawei Syntax Errors
            ErrorPattern(
                pattern=r"Error: Unrecognized command found at '\^' position\.",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="huawei",
                description="Unrecognized command syntax"
            ),
            ErrorPattern(
                pattern=r"Error: Incomplete command found at '\^' position\.",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="huawei",
                description="Incomplete command"
            ),
            
            # Fortinet FortiOS Syntax Errors
            ErrorPattern(
                pattern=r"command parse error before",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="fortinet",
                description="Command parsing error"
            ),
            ErrorPattern(
                pattern=r"Unknown action",
                error_type=ErrorType.COMMAND_NOT_FOUND,
                vendor="fortinet",
                description="Unknown command or action"
            ),
            
            # Palo Alto PAN-OS Syntax Errors
            ErrorPattern(
                pattern=r"Invalid syntax\.",
                error_type=ErrorType.SYNTAX_ERROR,
                vendor="paloalto",
                description="Invalid command syntax"
            ),
            ErrorPattern(
                pattern=r"Unknown command:",
                error_type=ErrorType.COMMAND_NOT_FOUND,
                vendor="paloalto",
                description="Command not recognized"
            ),
            
            # Generic Permission Errors (across vendors)
            ErrorPattern(
                pattern=r"Permission denied",
                error_type=ErrorType.PERMISSION_ERROR,
                vendor="generic",
                description="Insufficient permissions for command"
            ),
            ErrorPattern(
                pattern=r"Access denied",
                error_type=ErrorType.PERMISSION_ERROR,
                vendor="generic",
                description="Access denied for command"
            ),
            ErrorPattern(
                pattern=r"Insufficient privileges",
                error_type=ErrorType.PERMISSION_ERROR,
                vendor="generic",
                description="User lacks required privileges"
            ),
            
            # Generic Command Not Found Errors
            ErrorPattern(
                pattern=r"command not found",
                error_type=ErrorType.COMMAND_NOT_FOUND,
                vendor="generic",
                case_sensitive=False,
                description="Command not found on system"
            ),
            ErrorPattern(
                pattern=r"bad command or file name",
                error_type=ErrorType.COMMAND_NOT_FOUND,
                vendor="generic",
                case_sensitive=False,
                description="Command not recognized"
            ),
        ]
        
        return patterns
    
    def parse_command_output(self, output: str, device_platform: Optional[str] = None) -> Optional[ParsedError]:
        """
        Parse command output to detect vendor-specific errors.
        
        Args:
            output: The command output to analyze
            device_platform: Optional platform hint to prioritize certain patterns
            
        Returns:
            ParsedError if an error is detected, None otherwise
        """
        if not output or not output.strip():
            return None
        
        # Normalize the output for consistent parsing
        output_lines = output.strip().split('\n')
        
        # Check each line for error patterns
        best_match = None
        highest_confidence = 0.0
        
        for line in output_lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in self.error_patterns:
                match = self._match_pattern(line, pattern, device_platform)
                if match and match.confidence > highest_confidence:
                    best_match = match
                    highest_confidence = match.confidence
        
        return best_match
    
    def _match_pattern(self, line: str, pattern: ErrorPattern, device_platform: Optional[str] = None) -> Optional[ParsedError]:
        """Check if a line matches an error pattern."""
        flags = 0 if pattern.case_sensitive else re.IGNORECASE
        
        if re.search(pattern.pattern, line, flags):
            # Calculate confidence based on vendor match and pattern specificity
            confidence = 0.7  # Base confidence
            
            # Boost confidence if vendor matches device platform
            if device_platform and self._platforms_match(pattern.vendor, device_platform):
                confidence += 0.2
            
            # Boost confidence for more specific patterns
            if len(pattern.pattern) > 20:  # Longer patterns are typically more specific
                confidence += 0.1
            
            # Cap confidence at 1.0
            confidence = min(confidence, 1.0)
            
            enhanced_message = self._enhance_error_message(line, pattern)
            guidance = self._get_error_guidance(pattern, line)
            
            return ParsedError(
                error_type=pattern.error_type,
                vendor=pattern.vendor,
                original_message=line,
                enhanced_message=enhanced_message,
                guidance=guidance,
                confidence=confidence
            )
        
        return None
    
    def _platforms_match(self, pattern_vendor: str, device_platform: str) -> bool:
        """Check if pattern vendor matches device platform."""
        if not device_platform:
            return False
        
        device_platform = device_platform.lower().strip()
        pattern_vendor = pattern_vendor.lower().strip()
        
        # Direct match
        if pattern_vendor == device_platform:
            return True
        
        # Check for platform family matches
        cisco_platforms = ['cisco_ios', 'cisco_nxos', 'cisco_iosxr', 'ios', 'nxos', 'iosxr']
        juniper_platforms = ['juniper_junos', 'junos']
        arista_platforms = ['arista_eos', 'eos']
        
        if pattern_vendor in cisco_platforms and device_platform in cisco_platforms:
            return True
        if pattern_vendor in juniper_platforms and device_platform in juniper_platforms:
            return True
        if pattern_vendor in arista_platforms and device_platform in arista_platforms:
            return True
        
        return False
    
    def _enhance_error_message(self, original_message: str, pattern: ErrorPattern) -> str:
        """Enhance the original error message with additional context."""
        vendor_name = self._get_vendor_display_name(pattern.vendor)
        
        enhanced = f"[{vendor_name}] {original_message}"
        
        if pattern.description:
            enhanced += f"\n\nDescription: {pattern.description}"
        
        return enhanced
    
    def _get_vendor_display_name(self, vendor: str) -> str:
        """Get a human-readable vendor name."""
        vendor_map = {
            'cisco_ios': 'Cisco IOS/IOS-XE',
            'cisco_nxos': 'Cisco NX-OS',
            'cisco_iosxr': 'Cisco IOS-XR',
            'juniper_junos': 'Juniper Junos',
            'arista_eos': 'Arista EOS',
            'aruba': 'HPE Aruba',
            'huawei': 'Huawei',
            'fortinet': 'Fortinet FortiOS',
            'paloalto': 'Palo Alto PAN-OS',
            'generic': 'Generic'
        }
        
        return vendor_map.get(vendor, vendor.title())
    
    def _get_error_guidance(self, pattern: ErrorPattern, original_message: str) -> str:
        """Get vendor-specific guidance for resolving the error."""
        base_guidance = {
            ErrorType.SYNTAX_ERROR: self._get_syntax_error_guidance(pattern.vendor, original_message),
            ErrorType.PERMISSION_ERROR: self._get_permission_error_guidance(pattern.vendor),
            ErrorType.COMMAND_NOT_FOUND: self._get_command_not_found_guidance(pattern.vendor),
            ErrorType.CONFIGURATION_ERROR: self._get_configuration_error_guidance(pattern.vendor),
            ErrorType.TIMEOUT_ERROR: self._get_timeout_error_guidance(pattern.vendor),
            ErrorType.UNKNOWN_ERROR: self._get_unknown_error_guidance(pattern.vendor)
        }
        
        return base_guidance.get(pattern.error_type, "Check device documentation for error details.")
    
    def _get_syntax_error_guidance(self, vendor: str, message: str) -> str:
        """Get syntax error guidance based on vendor."""
        common_guidance = (
            "Command Syntax Error Troubleshooting:\n"
            "• Verify the command syntax is correct for this device platform\n"
            "• Ensure command has correct mode set (e.g., show or config)\n"
        )
        
        return common_guidance
    
    def _get_permission_error_guidance(self, vendor: str) -> str:
        """Get permission error guidance."""
        return (
            "Permission Error Troubleshooting:\n"
            "• Verify your user account has the necessary privileges\n"
            "• Review device AAA configuration for command authorization\n"
        )
    
    def _get_command_not_found_guidance(self, vendor: str) -> str:
        """Get command not found guidance."""
        return (
            "Command Not Found Troubleshooting:\n"
            "• Verify the command exists on this device/platform\n"
            "• Check the command spelling and syntax\n"
            "• Try the command manually on device\n"
        )
    
    def _get_configuration_error_guidance(self, vendor: str) -> str:
        """Get configuration error guidance."""
        return (
            "Configuration Error Troubleshooting:\n"
            "• Review the configuration syntax for this platform\n"
        )
    
    def _get_timeout_error_guidance(self, vendor: str) -> str:
        """Get timeout error guidance."""
        return (
            "Timeout Error Troubleshooting:\n"
            "• The command may be taking longer than expected\n"
        )
    
    def _get_unknown_error_guidance(self, vendor: str) -> str:
        """Get unknown error guidance."""
        return (
            "General Error Troubleshooting:\n"
            "• Check device logs for more details\n"
            "• Verify device configuration and status\n"
            "• Review command syntax and parameters\n"
            "• Try the command manually on device\n"
        )

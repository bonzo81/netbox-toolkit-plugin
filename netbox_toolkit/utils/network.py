"""Network utility functions."""
import socket
import time
from typing import Tuple, Optional

from ..exceptions import DeviceReachabilityError, SSHBannerError
from .logging import get_toolkit_logger

logger = get_toolkit_logger(__name__)


def check_device_reachability(hostname: str, port: int = 22, timeout: int = 3) -> Tuple[bool, bool, Optional[bytes]]:
    """
    Check if a device is reachable and if it's running SSH.
    
    Args:
        hostname: The hostname or IP address to check
        port: The port to check (default: 22 for SSH)
        timeout: Connection timeout in seconds
        
    Returns:
        Tuple of (is_reachable, is_ssh_server, ssh_banner)
        
    Raises:
        DeviceReachabilityError: If device is not reachable
        SSHBannerError: If SSH banner cannot be read
    """
    logger.debug(f"Checking device reachability for {hostname}:{port} with timeout {timeout}s")
    
    is_reachable = False
    is_ssh_server = False
    ssh_banner = None
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock.settimeout(timeout)
        
        # Attempt connection
        logger.debug(f"Attempting TCP connection to {hostname}:{port}")
        sock.connect((hostname, port))
        is_reachable = True
        logger.debug(f"TCP connection successful to {hostname}:{port}")
        
        # Try to read SSH banner
        ssh_banner, is_ssh_server = _read_ssh_banner(sock, hostname)
        logger.debug(f"SSH banner check: is_ssh_server={is_ssh_server}, banner_length={len(ssh_banner) if ssh_banner else 0}")
        
    except socket.timeout:
        logger.warning(f"Connection to {hostname}:{port} timed out after {timeout}s")
        raise DeviceReachabilityError(f"Connection to {hostname}:{port} timed out")
    except ConnectionRefusedError:
        logger.warning(f"Connection to {hostname}:{port} refused")
        raise DeviceReachabilityError(f"Connection to {hostname}:{port} refused")
    except socket.gaierror as e:
        logger.error(f"Could not resolve hostname: {hostname} - {str(e)}")
        raise DeviceReachabilityError(f"Could not resolve hostname: {hostname}")
    except Exception as e:
        logger.error(f"Socket error when connecting to {hostname}: {str(e)}")
        raise DeviceReachabilityError(f"Socket error when connecting to {hostname}: {str(e)}")
    finally:
        try:
            sock.close()
        except:
            pass
    
    return is_reachable, is_ssh_server, ssh_banner


def _read_ssh_banner(sock: socket.socket, hostname: str, attempts: int = 3) -> Tuple[Optional[bytes], bool]:
    """
    Try to read SSH banner from socket.
    
    Args:
        sock: Connected socket
        hostname: Hostname for logging
        attempts: Number of attempts to read banner
        
    Returns:
        Tuple of (banner, is_ssh_server)
    """
    logger.debug(f"Attempting to read SSH banner from {hostname} with {attempts} attempts")
    
    ssh_banner = None
    is_ssh_server = False
    
    for i in range(attempts):
        try:
            logger.debug(f"SSH banner read attempt {i + 1}/{attempts}")
            sock.settimeout(1)
            banner = sock.recv(1024)
            if banner:
                ssh_banner = banner
                logger.debug(f"Received banner: {banner[:50]}..." if len(banner) > 50 else f"Received banner: {banner}")
                if banner.startswith(b'SSH-'):
                    is_ssh_server = True
                    logger.debug("Banner indicates SSH server")
                    break
                else:
                    logger.debug("Banner received but not SSH protocol")
                    pass  # Non-SSH banner received
            else:
                logger.debug("No banner data received")
            
            # If no banner received but still connected, pause briefly and try again
            if i < attempts - 1:
                logger.debug("Waiting 0.5s before next banner read attempt")
                time.sleep(0.5)
        except socket.timeout:
            logger.debug(f"Banner read attempt {i + 1} timed out")
            if i < attempts - 1:
                continue
        except Exception as e:
            logger.warning(f"Error reading SSH banner: {str(e)}")
            break
    
    logger.debug(f"SSH banner read completed: is_ssh_server={is_ssh_server}")
    return ssh_banner, is_ssh_server


def validate_device_connectivity(hostname: str, port: int = 22) -> None:
    """
    Validate that a device is reachable and has SSH available.
    
    Args:
        hostname: The hostname or IP address to validate
        port: The port to check (default: 22)
        
    Raises:
        DeviceReachabilityError: If device is not reachable
        SSHBannerError: If SSH service issues are detected
    """
    logger.debug(f"Validating device connectivity for {hostname}:{port}")
    
    try:
        is_reachable, is_ssh_server, ssh_banner = check_device_reachability(hostname, port)
        
        if not is_reachable:
            logger.error(f"Device {hostname}:{port} is not reachable")
            raise DeviceReachabilityError(
                f"Cannot connect to {hostname} on port {port}. "
                f"Please verify the device is reachable and SSH is enabled."
            )
        
        if is_reachable and not is_ssh_server:
            banner_msg = f" (received banner: {ssh_banner})" if ssh_banner else ""
            logger.warning(f"Device {hostname}:{port} is reachable but SSH banner not detected{banner_msg}")
            # Device is reachable but didn't provide SSH banner - connection might fail
            pass
        elif is_ssh_server:
            logger.debug(f"Device {hostname}:{port} is reachable and SSH server detected")
            
    except (DeviceReachabilityError, SSHBannerError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error validating connectivity to {hostname}: {str(e)}")
        raise DeviceReachabilityError(f"Unexpected error validating connectivity to {hostname}: {str(e)}")

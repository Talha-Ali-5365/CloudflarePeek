"""Cloudflare detection utilities."""
import socket
import requests
import ipaddress
import logging
from typing import Set

logger = logging.getLogger(__name__)

CLOUDFLARE_IP_RANGES: Set[str] = {
    "104.16.0.0/12", "108.162.192.0/18", "131.0.72.0/22",
    "141.101.64.0/18", "162.158.0.0/15", "172.64.0.0/13",
    "198.41.128.0/17"
}


def _ip_in_cidr(ip: str, networks: Set[str]) -> bool:
    """Check if IP address is within any of the given CIDR ranges."""
    try:
        addr = ipaddress.ip_address(ip)
        return any(addr in ipaddress.ip_network(net) for net in networks)
    except ValueError:
        return False


def behind_cloudflare(url: str) -> bool:
    """
    Check if a URL is behind Cloudflare protection.
    
    Args:
        url: The URL to check
        
    Returns:
        True if the site is behind Cloudflare, False otherwise
    """
    # Extract hostname from URL
    try:
        host = url.split("//")[-1].split("/")[0]
    except (IndexError, AttributeError):
        return False
    
    # DNS lookup check
    try:
        for addr in socket.gethostbyname_ex(host)[2]:
            if _ip_in_cidr(addr, CLOUDFLARE_IP_RANGES):
                return True
    except (socket.gaierror, OSError):
        pass
    
    # Header check as secondary verification
    try:
        resp = requests.head(url, timeout=5, allow_redirects=True)
        server_header = resp.headers.get("server", "").lower()
        if "cloudflare" in server_header:
            return True
    except (requests.RequestException, Exception):
        pass
    
    return False
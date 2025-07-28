import aiohttp
import ipaddress
from abc import ABC, abstractmethod

class DNSProvider(ABC):
    def __init__(self, api_key: str, session: aiohttp.ClientSession):
        self.api_key = api_key
        self.session = session
    
    @abstractmethod
    async def validate_domain(self, domain: str) -> None:
        """Validate the domain exists with the provider"""
        pass
    
    @abstractmethod
    async def get_current_ip(self, ip_version: int) -> str:
        """Get the current public IP address"""
        pass
    
    @abstractmethod
    async def update_dns_record(
        self, 
        domain: str, 
        record: str, 
        record_type: str, 
        new_ip: str
    ) -> None:
        """Update the DNS record with the new IP"""
        pass
    
    def get_ip_version(self) -> int:
        """Get the IP version based on provider configuration"""
        # Default implementation, can be overridden by providers
        return 4
import aiohttp
import ipaddress
from providers import get_provider

class DNSUpdater:
    def __init__(self, provider: str, api_key: str, domain: str, record: str, session: aiohttp.ClientSession):
        self.provider = get_provider(provider)(api_key, session)
        self.domain = domain
        self.record = record
        self.session = session
    
    async def validate_domain(self) -> None:
        """Validate the domain exists with the provider"""
        await self.provider.validate_domain(self.domain)
    
    async def get_current_ip(self) -> str:
        """Get the current public IP address"""
        ip_version = self.provider.get_ip_version()
        return await self.provider.get_current_ip(ip_version)
    
    async def update_dns_record(self, new_ip: str) -> None:
        """Update the DNS record with the new IP"""
        # Determine record type based on IP version
        ip_version = ipaddress.ip_address(new_ip).version
        record_type = 'a' if ip_version == 4 else 'aaaa'
        
        await self.provider.update_dns_record(
            domain=self.domain,
            record=self.record,
            record_type=record_type,
            new_ip=new_ip
        )
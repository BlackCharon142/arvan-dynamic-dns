import aiohttp
from .base_provider import DNSProvider

class ArvanProvider(DNSProvider):
    BASE_URL = "https://napi.arvancloud.ir/cdn/4.0"
    
    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Apikey {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def validate_domain(self, domain: str) -> None:
        """Validate domain exists in ArvanCloud account"""
        url = f"{self.BASE_URL}/domains/{domain}"
        async with self.session.get(url, headers=self._get_headers()) as response:
            if response.status == 404:
                raise ValueError(f"Domain '{domain}' not found in your ArvanCloud account")
            response.raise_for_status()
    
    async def get_current_ip(self, ip_version: int) -> str:
        """Get current public IP using Arvan's preferred method"""
        # For IPv4
        if ip_version == 4:
            url = "https://v4.ident.me"
        # For IPv6
        elif ip_version == 6:
            url = "https://v6.ident.me"
        else:
            raise ValueError("Invalid IP version")
        
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    
    async def update_dns_record(
        self, 
        domain: str, 
        record: str, 
        record_type: str, 
        new_ip: str
    ) -> None:
        """Update or create DNS record in ArvanCloud"""
        # Prepare record data
        record_data = {
            "type": record_type,
            "name": record,
            "value": [{"ip": new_ip}],
            "ttl": 120,
            "cloud": False,
            "upstream_https": "default",
            "ip_filter_mode": {
                "count": "single",
                "order": "none",
                "geo_filter": "none"
            }
        }
        
        # Get existing records
        records_url = f"{self.BASE_URL}/domains/{domain}/dns-records"
        async with self.session.get(records_url, headers=self._get_headers()) as response:
            response.raise_for_status()
            records = await response.json()
        
        record_id = None
        
        # Find matching record
        for r in records["data"]:
            if r["name"] == record and r["type"] == record_type:
                record_id = r["id"]
                break
        
        # Update or create record
        if record_id:
            update_url = f"{self.BASE_URL}/domains/{domain}/dns-records/{record_id}"
            async with self.session.put(
                update_url, 
                headers=self._get_headers(), 
                json=record_data
            ) as response:
                response.raise_for_status()
        else:
            async with self.session.post(
                records_url, 
                headers=self._get_headers(), 
                json=record_data
            ) as response:
                response.raise_for_status()
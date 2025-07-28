import aiohttp

class ArvanAPI:
    BASE_URL = "https://napi.arvancloud.ir/cdn/4.0"
    
    def __init__(self, key: str, session: aiohttp.ClientSession):
        self.key = key.strip()
        self.session = session
    
    async def get_domain_info(self, domain: str) -> dict:
        """Get information about a domain"""
        url = f"{self.BASE_URL}/domains/{domain}"
        headers = self._get_headers()
        async with self.session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_dns_records(self, domain: str) -> dict:
        """Get all DNS records for a domain"""
        url = f"{self.BASE_URL}/domains/{domain}/dns-records"
        headers = self._get_headers()
        async with self.session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    
    async def create_dns_record(self, domain: str, record_data: dict) -> dict:
        """Create a new DNS record"""
        url = f"{self.BASE_URL}/domains/{domain}/dns-records"
        headers = self._get_headers()
        async with self.session.post(url, headers=headers, json=record_data) as response:
            response.raise_for_status()
            return await response.json()
    
    async def update_dns_record(self, domain: str, record_id: str, record_data: dict) -> dict:
        """Update an existing DNS record"""
        url = f"{self.BASE_URL}/domains/{domain}/dns-records/{record_id}"
        headers = self._get_headers()
        async with self.session.put(url, headers=headers, json=record_data) as response:
            response.raise_for_status()
            return await response.json()
    
    def _get_headers(self) -> dict:
        """Get common headers for API requests"""
        return {
            "Authorization": f"Apikey {self.key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
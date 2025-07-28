import argparse
import asyncio
import socket
import aiohttp
import ipaddress
import logging
from apis import ArvanAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def get_current_ip(session: aiohttp.ClientSession, family: socket.AddressFamily) -> str:
    """Get the current public IP address using the specified family"""
    # For IPv4
    if family == socket.AF_INET:
        url = "https://v4.ident.me"
    # For IPv6
    elif family == socket.AF_INET6:
        url = "https://v6.ident.me"
    else:
        raise ValueError("Invalid address family")
    
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()

async def update_dns_record(
    api: ArvanAPI, 
    domain: str, 
    record: str, 
    new_ip: str
) -> None:
    """Update or create DNS record with the new IP address"""
    # Determine record type based on IP version
    ip_version = ipaddress.ip_address(new_ip).version
    record_type = 'a' if ip_version == 4 else 'aaaa'
    
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
    records = await api.get_dns_records(domain)
    record_id = None
    
    # Find matching record
    for r in records["data"]:
        if r["name"] == record and r["type"] == record_type:
            record_id = r["id"]
            break
    
    # Update or create record
    if record_id:
        await api.update_dns_record(domain, record_id, record_data)
        logger.info(f"Updated DNS record {record}.{domain} with IP {new_ip}")
    else:
        await api.create_dns_record(domain, record_data)
        logger.info(f"Created DNS record {record}.{domain} with IP {new_ip}")

async def main():
    parser = argparse.ArgumentParser(description='ArvanCloud Dynamic DNS Client')
    parser.add_argument('--key', required=True, help='ArvanCloud API key')
    parser.add_argument('--domain', required=True, help='Domain name')
    parser.add_argument('--record', required=True, help='Record name (subdomain)')
    parser.add_argument('--interval', type=int, default=3, 
                        help='Interval in seconds between checks')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-4', '--ipv4', action='store_true', help='Use IPv4')
    group.add_argument('-6', '--ipv6', action='store_true', help='Use IPv6')
    
    args = parser.parse_args()
    
    # Determine IP version
    if args.ipv4:
        family = socket.AF_INET
    elif args.ipv6:
        family = socket.AF_INET6
    else:
        # Default to IPv4
        family = socket.AF_INET
    
    # Create TCP connector with the specified family
    connector = aiohttp.TCPConnector(family=family)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        api = ArvanAPI(key=args.key, session=session)
        
        # Validate domain exists
        try:
            domain_info = await api.get_domain_info(args.domain)
            logger.info(f"Domain {args.domain} validated")
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                logger.error(f"Domain {args.domain} not found in your account")
                return
            raise
        
        current_ip = None
        
        while True:
            try:
                # Get current public IP
                new_ip = await get_current_ip(session, family)
                
                # Update DNS if IP changed
                if new_ip != current_ip:
                    logger.info(f"IP changed from {current_ip} to {new_ip}")
                    current_ip = new_ip
                    await update_dns_record(api, args.domain, args.record, new_ip)
                else:
                    logger.info(f"IP unchanged: {current_ip}")
                
                # Wait for next check
                await asyncio.sleep(args.interval)
                
            except Exception as e:
                logger.error(f"Error occurred: {e}")
                # Wait before retrying
                await asyncio.sleep(min(args.interval, 60))

if __name__ == "__main__":
    asyncio.run(main())
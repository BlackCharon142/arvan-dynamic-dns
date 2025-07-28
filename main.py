import argparse
import asyncio
import socket
import aiohttp
import logging
from dns_updater import DNSUpdater

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(description='Dynamic DNS Client')
    parser.add_argument('--provider', required=True, choices=['arvan', 'cloudflare'], 
                        help='DNS provider')
    parser.add_argument('--key', required=True, help='API key')
    parser.add_argument('--domain', required=True, help='Domain name')
    parser.add_argument('--records', required=True, 
                        help='Comma-separated list of record names (subdomains)')
    parser.add_argument('--interval', type=int, default=600, 
                        help='Interval in seconds between checks')
    parser.add_argument('--timeout', type=int, default=30,
                        help='Request timeout in seconds')
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
        family = socket.AF_INET  # Default to IPv4
    
    # Parse records
    records = [r.strip() for r in args.records.split(',')]
    
    # Create TCP connector with timeout
    connector = aiohttp.TCPConnector(family=family)
    timeout = aiohttp.ClientTimeout(total=args.timeout)
    
    async with aiohttp.ClientSession(
        connector=connector, 
        timeout=timeout
    ) as session:
        # Create DNS updater with selected provider
        updater = DNSUpdater(
            provider=args.provider,
            api_key=args.key,
            domain=args.domain,
            records=records,
            session=session
        )
        
        # Validate provider configuration
        try:
            await updater.validate_domain()
            logger.info(f"Domain {args.domain} validated with {args.provider} provider")
        except Exception as e:
            logger.error(f"Domain validation failed: {e}")
            return
        
        current_ip = None
        
        while True:
            try:
                # Get current public IP
                new_ip = await updater.get_current_ip()
                
                # Update DNS if IP changed
                if new_ip != current_ip:
                    logger.info(f"IP changed from {current_ip or 'none'} to {new_ip}")
                    current_ip = new_ip
                    await updater.update_dns_records(new_ip)
                else:
                    logger.info(f"IP unchanged: {current_ip}")
                
                # Wait for next check
                await asyncio.sleep(args.interval)
                
            except asyncio.TimeoutError:
                logger.error("Request timed out. Retrying after delay.")
                await asyncio.sleep(min(args.interval, 30))
            except aiohttp.ClientError as e:
                logger.error(f"Network error: {e}. Retrying after delay.")
                await asyncio.sleep(min(args.interval, 30))
            except Exception as e:
                logger.error(f"Error occurred: {e}. Retrying after delay.")
                await asyncio.sleep(min(args.interval, 60))

if __name__ == "__main__":
    asyncio.run(main())
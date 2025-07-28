# Dynamic DNS Updater(ArvanCloud)

A robust Python-based solution for automatically updating DNS records with your current public IP address. Designed to work with ArvanCloud DNS services and easily extendable to support other providers.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [Running as a Service](#running-as-a-service)
5. [Extending to Other Providers](#extending-to-other-providers)
6. [Troubleshooting](#troubleshooting)
7. [License](#license)

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Step-by-Step Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/BlackCharon142/arvan-dynamic-dns.git
   cd arvan-dynamic-dns
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create configuration file**:
   ```bash
   cp .env.example .env
   ```

## Configuration

Edit the `.env` file with your credentials and settings:

```ini
# Required settings
PROVIDER=arvan
API_KEY=your_arvan_api_key
DOMAIN=yourdomain.com
RECORDS=www,api,app  # Comma-separated list of subdomains

# Optional settings
INTERVAL=600  # Update interval in seconds (default: 600 = 10 minutes)
TIMEOUT=30    # Request timeout in seconds (default: 30)
IP_VERSION=4  # 4 for IPv4, 6 for IPv6 (default: 4)
```

### Obtaining ArvanCloud API Key

1. Log in to your [ArvanCloud account](https://panel.arvancloud.ir)
2. Go to **Profile** → **Machine Users**
3. Click **Create New Machine User**
4. Copy the generated API key into your `.env` file
5. Go to **Resource Management**
6. Name your key (e.g., "ddns-updater")
7. Give Premission to modify domain DNS

## Usage

### Basic Command

```bash
python main.py
```

This will use the settings from your `.env` file.

### Command Line Options

You can override `.env` settings with command line arguments:

```bash
python main.py \
  --provider arvan \
  --key YOUR_API_KEY \
  --domain yourdomain.com \
  --records www,api \
  --interval 300 \
  --timeout 20 \
  --ipv6
```

### Command Line Arguments

| Argument         | Description                                  | Default     |
|------------------|----------------------------------------------|-------------|
| `--provider`     | DNS provider (`arvan`, `cloudflare`, etc.)   | `arvan`     |
| `--key`          | API key for the DNS provider                 | -           |
| `--domain`       | Domain name to update                        | -           |
| `--records`      | Comma-separated list of subdomains to update | -           |
| `--interval`     | Update interval in seconds                   | 600         |
| `--timeout`      | Request timeout in seconds                   | 30          |
| `--ipv4`         | Use IPv4                                     | Default     |
| `--ipv6`         | Use IPv6                                     | -           |

### Example Output

```
2023-07-26 12:00:00,000 - INFO - Domain yourdomain.com validated with arvan provider
2023-07-26 12:00:00,100 - INFO - IP changed from none to 192.0.2.1
2023-07-26 12:00:00,200 - INFO - Updated DNS record www.yourdomain.com with IP 192.0.2.1
2023-07-26 12:00:00,210 - INFO - Updated DNS record api.yourdomain.com with IP 192.0.2.1
2023-07-26 12:05:00,000 - INFO - IP unchanged: 192.0.2.1
```


## Extending to Other Providers

The architecture makes it easy to add support for new DNS providers:

1. Create a new provider file in the `providers` directory (e.g., `cloudflare_provider.py`)
   
2. Implement the provider class:
   ```python
   from .base_provider import DNSProvider
   
   class CloudflareProvider(DNSProvider):
       BASE_URL = "https://api.cloudflare.com/client/v4"
       
       def _get_headers(self) -> dict:
           return {
               "Authorization": f"Bearer {self.api_key}",
               "Content-Type": "application/json"
           }
       
       async def validate_domain(self, domain: str) -> None:
           # Implementation here
           pass
       
       async def get_current_ip(self, ip_version: int) -> str:
           # Implementation here
           pass
       
       async def update_dns_record(self, domain: str, record: str, 
                                 record_type: str, new_ip: str) -> None:
           # Implementation here
           pass
   ```

3. Register the provider in `providers/__init__.py`:
   ```python
   from .arvan_provider import ArvanProvider
   from .cloudflare_provider import CloudflareProvider
   
   PROVIDERS = {
       'arvan': ArvanProvider,
       'cloudflare': CloudflareProvider
   }
   ```

4. Add the provider to choices in `main.py`

4. Use your new provider with `--provider cloudflare`

## Troubleshooting

### Common Issues

1. **401 Unauthorized Error**
   - Verify your API key is correct
   - Ensure the key has DNS management permissions
   - Check for extra spaces in the key

2. **Domain Not Found**
   - Verify the domain exists in your provider account
   - Check for typos in the domain name
   - Ensure your API key has access to the domain

3. **Timeout Errors**
   - Increase the `--timeout` value
   - Check your network connection
   - Verify the provider's API status

4. **Record Not Updating**
   - Check DNS propagation time (changes may take minutes to hours)
   - Verify you're updating the correct record type (A for IPv4, AAAA for IPv6)
   - Ensure your record names match exactly

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
python main.py --debug
```

Or set logging level in code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any:
- New DNS providers
- Bug fixes
- Feature requests
- Documentation improvements
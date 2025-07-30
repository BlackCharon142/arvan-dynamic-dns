# Cloud DNS Updater

Cloud DNS Updater is a modular, robust Python-based solution for automatically updating DNS records with your current public IP address. Designed to work with ArvanCloud DNS services out-of-the-box, its provider-based architecture makes it easily extendable to support additional DNS providers like Cloudflare, DigitalOcean, and others. The solution features both Docker and traditional Python deployments, with security-focused distroless containers and rootless execution options.



## Table of Contents

- [Cloud DNS Updater](#cloud-dns-updater)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Docker Installation](#docker-installation)
    - [Virtual Environment Installation](#virtual-environment-installation)
  - [Usage](#usage)
    - [Docker Usage](#docker-usage)
      - [Basic Command](#basic-command)
      - [Using Environment File](#using-environment-file)
      - [Distroless Container (Enhanced Security)](#distroless-container-enhanced-security)
      - [Docker Compose](#docker-compose)
    - [Virtual Environment Usage](#virtual-environment-usage)
  - [Extending to Other Providers](#extending-to-other-providers)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
    - [Debug Mode](#debug-mode)
  - [License](#license)
  - [Contributing](#contributing)

## Installation

### Docker Installation

**Prerequisites**: Docker installed on your system

1. **Pull the Docker image**:
2. *You can see the list of images in [Packages](https://github.com/users/BlackCharon142/packages/container/package/cloud-dns-updater%2Fdynamic-dns)*
   ```bash
   # Slim image (recommended for most users)
   docker pull ghcr.io/blackcharon142/cloud-dns-updater/dynamic-dns:slim
   
   # Distroless image (for maximum security)
   docker pull ghcr.io/blackcharon142/cloud-dns-updater/dynamic-dns:distroless
   ```

3. **Create a `.env` file** (optional but recommended):
   ```ini
   PROVIDER=arvan
   API_KEY=your_arvan_api_key
   DOMAIN=yourdomain.com
   RECORDS=www,api,app
   INTERVAL=600
   TIMEOUT=30
   IP_VERSION=4
   ```

### Virtual Environment Installation

**Prerequisites**: Python 3.7+ and pip

1. **Clone the repository**:
   ```bash
   git clone https://github.com/BlackCharon142/Cloud-DNS-Updater.git
   cd cloud-dns-updater
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate    # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Docker Usage

#### Basic Command
```bash
docker run -d \
  -e PROVIDER=arvan \
  -e API_KEY="your_api_key" \
  -e DOMAIN="yourdomain.com" \
  -e RECORDS="www,api" \
  -e INTERVAL=300 \
  ghcr.io/blackcharon142/cloud-dns-updater/dynamic-dns:slim
```

#### Using Environment File
```bash
docker run -d \
  --env-file .env \
  ghcr.io/blackcharon142/cloud-dns-updater/dynamic-dns:slim
```

#### Distroless Container (Enhanced Security)
```bash
docker run -d \
  -e PROVIDER=arvan \
  -e API_KEY="your_api_key" \
  -e DOMAIN="yourdomain.com" \
  -e RECORDS="www" \
  --read-only \
  ghcr.io/blackcharon142/cloud-dns-updater/dynamic-dns:distroless
```

#### Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  dns-updater:
    image: ghcr.io/blackcharon142/cloud-dns-updater/dynamic-dns:slim
    container_name: cloud-dns-updater
    restart: unless-stopped
    environment:
      PROVIDER: arvan
      API_KEY: ${API_KEY}
      DOMAIN: ${DOMAIN}
      RECORDS: www,api
      INTERVAL: 300
      TIMEOUT: 20
      IP_VERSION: 4
    volumes:
      - ./logs:/app/logs
```

Start the service:
```bash
docker compose up -d
```

### Virtual Environment Usage

1. **Create configuration file**:
   ```bash
   cp .env.example .env
   nano .env
   ```

2. **Edit the `.env` file**:
   ```ini
   PROVIDER=arvan
   API_KEY=your_arvan_api_key
   DOMAIN=yourdomain.com
   RECORDS=www,api,app
   INTERVAL=600
   TIMEOUT=30
   IP_VERSION=4
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Override settings via command line**:
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
# For Docker
docker run -e DEBUG=1 ... 

# For virtual environment
python main.py --debug
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for:
- New DNS providers
- Bug fixes
- Security improvements
- Documentation enhancements
- Performance optimizations
#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    # Required parameters
    required_params = {
        '--provider': os.getenv('PROVIDER'),
        '--key': os.getenv('API_KEY'),
        '--domain': os.getenv('DOMAIN'),
        '--records': os.getenv('RECORDS')
    }
    
    # Check for missing required parameters
    missing = [param for param, value in required_params.items() if not value]
    if missing:
        print(f"Error: Missing required parameters: {', '.join(missing)}")
        sys.exit(1)
    
    # Build command
    cmd = [
        "python", "main.py",
        "--provider", required_params['--provider'],
        "--key", required_params['--key'],
        "--domain", required_params['--domain'],
        "--records", required_params['--records']
    ]
    
    # Add IP version
    if os.getenv('IP_VERSION') == '6':
        cmd.append('--ipv6')
    else:
        cmd.append('--ipv4')
    
    # Add optional parameters
    if interval := os.getenv('INTERVAL'):
        cmd.extend(['--interval', interval])
    
    if timeout := os.getenv('TIMEOUT'):
        cmd.extend(['--timeout', timeout])
    
    # Execute command
    try:
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
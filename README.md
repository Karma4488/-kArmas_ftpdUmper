# kArmas_ftpdUmper

🐍 **kArmas_ftpdUmper** - Multi-Purpose Security Testing Tool

## Features

### FTP Recursive Downloader
- ✅ Recursive FTP crawl
- ✅ Global progress bar (all files)
- ✅ Per-file progress bar
- ✅ Resume support
- ✅ Retry logic with exponential backoff
- ✅ Comprehensive logging (file + console)

### HTTP Brute-forcer with 403 Bypass
- ✅ Multiple HTTP methods support (GET, POST, PUT, DELETE, etc.)
- ✅ 403 Forbidden bypass techniques
- ✅ Dictionary-based payload generation
- ✅ Authentication brute-forcing
- ✅ Endpoint discovery and scanning
- ✅ Configurable headers and proxies
- ✅ Progress tracking and detailed logging
- ✅ JSON output support

## Installation

```bash
# Clone the repository
git clone https://github.com/Karma4488/-kArmas_ftpdUmper.git
cd -kArmas_ftpdUmper

# Install dependencies
pip install -r requirements.txt
```

## Usage

### FTP Mode (Default)

Edit the configuration in `kArmas_ftpdUmper.py`:

```python
FTP_HOST = "ftp.example.com"
FTP_USER = "username"
FTP_PASS = "password"
REMOTE_ROOT = "/"
LOCAL_ROOT = "ftp_dump"
```

Run the FTP dumper:

```bash
python kArmas_ftpdUmper.py
```

### HTTP Brute-force Mode

#### Endpoint Scanning

Scan for accessible endpoints:

```bash
python kArmas_ftpdUmper.py --http --url http://example.com --wordlist wordlist.txt
```

With verbose output and 403 bypass enabled:

```bash
python kArmas_ftpdUmper.py --http --url http://example.com/admin --wordlist wordlist.txt --verbose
```

#### Authentication Brute-forcing

Brute-force login credentials:

```bash
python kArmas_ftpdUmper.py --http --mode auth --url http://example.com/login \
    --username admin --wordlist passwords.txt
```

#### Advanced Options

Using custom headers and proxy:

```bash
python kArmas_ftpdUmper.py --http --url http://example.com \
    --wordlist wordlist.txt \
    --headers "User-Agent: CustomAgent" "X-Custom: Value" \
    --proxy http://127.0.0.1:8080 \
    --methods GET POST \
    --delay 0.5 \
    --timeout 15
```

Disable 403 bypass techniques:

```bash
python kArmas_ftpdUmper.py --http --url http://example.com \
    --wordlist wordlist.txt --no-bypass
```

Save results to JSON file:

```bash
python kArmas_ftpdUmper.py --http --url http://example.com \
    --wordlist wordlist.txt --output results.json
```

#### Using Configuration File

Create a `config.json` file (see `config.json` template) and run:

```bash
python kArmas_ftpdUmper.py --http --config config.json
```

You can override config file settings with command-line arguments:

```bash
python kArmas_ftpdUmper.py --http --config config.json --url http://different-target.com
```

## 403 Bypass Techniques

The tool implements multiple techniques to bypass 403 Forbidden responses:

### URL Manipulation
- **Apache Dot**: Append `/.` to the URL (e.g., `/admin/.`)
- **Apache Double Slash**: Use double slashes (e.g., `//admin`)
- **Trailing Slash**: Add trailing slash (e.g., `/admin/`)
- **Case Variation**: Try different case combinations
- **URL Encoding**: Apply percent encoding

### Header Manipulation
The tool automatically tries various headers that may bypass access controls:
- `X-Original-URL`
- `X-Rewrite-URL`
- `X-Forwarded-For`
- `X-Forwarded-Host`
- `X-Custom-IP-Authorization`
- `X-Originating-IP`
- `X-Remote-IP`
- `X-Client-IP`
- `X-Host`
- `X-Remote-Addr`

### HTTP Method Variation
Attempts alternative HTTP methods when a 403 is encountered:
- POST, PUT, DELETE, PATCH, OPTIONS, HEAD

## Configuration File Format

Example `config.json`:

```json
{
  "http_bruteforce": {
    "target_url": "http://example.com/admin",
    "methods": ["GET", "POST"],
    "timeout": 10,
    "max_retries": 3,
    "delay": 0.5,
    "verbose": true,
    "enable_bypass": true,
    "success_codes": [200, 201, 202, 301, 302],
    "headers": {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    "proxies": {
      "http": "http://127.0.0.1:8080",
      "https": "http://127.0.0.1:8080"
    },
    "wordlist_path": "wordlist.txt"
  }
}
```

## Command-Line Arguments

### HTTP Mode Arguments

```
--http              Enable HTTP brute-force mode
--mode {scan,auth}  Mode: scan endpoints or brute-force authentication
--url URL           Target URL
--methods METHOD    HTTP methods to use (e.g., GET POST PUT)
--wordlist FILE     Path to wordlist file
--username USER     Username for authentication brute-force
--headers HEADER    Custom headers (format: "Key: Value")
--proxy PROXY       Proxy URL (e.g., http://127.0.0.1:8080)
--timeout SECONDS   Request timeout in seconds
--retries NUM       Maximum number of retries per request
--delay SECONDS     Delay between requests in seconds
--no-bypass         Disable 403 bypass techniques
--verbose           Enable verbose logging
--config FILE       Path to JSON configuration file
--output FILE       Output file for results (JSON format)
```

## Examples

### Example 1: Basic Endpoint Discovery

```bash
python kArmas_ftpdUmper.py --http \
    --url http://target.com \
    --wordlist wordlist.txt \
    --verbose
```

### Example 2: Authentication Brute-force with Delay

```bash
python kArmas_ftpdUmper.py --http \
    --mode auth \
    --url http://target.com/api/login \
    --username admin \
    --wordlist passwords.txt \
    --delay 1.0 \
    --methods POST
```

### Example 3: Scanning with Proxy and Custom Headers

```bash
python kArmas_ftpdUmper.py --http \
    --url http://target.com \
    --wordlist endpoints.txt \
    --proxy http://127.0.0.1:8080 \
    --headers "Authorization: Bearer token123" \
    --output scan_results.json
```

### Example 4: Aggressive 403 Bypass Testing

```bash
python kArmas_ftpdUmper.py --http \
    --url http://target.com/admin \
    --wordlist wordlist.txt \
    --methods GET POST PUT DELETE OPTIONS \
    --verbose \
    --output bypass_results.json
```

## Output

The tool provides detailed output including:

- Real-time progress bars
- Successful requests with status codes
- 403 bypass attempts and successes
- Failed requests (when verbose mode enabled)
- Summary statistics
- Optional JSON export of all results

Example output:

```
============================================================
HTTP BRUTE-FORCE RESULTS SUMMARY
============================================================

Target: http://example.com/admin
Methods tested: GET, POST
403 Bypass: Enabled

Successful requests: 3
Bypassed 403: 2
Failed requests: 15

SUCCESSFUL REQUESTS:
------------------------------------------------------------
  [200] GET http://example.com/admin/dashboard
  [200] GET http://example.com/admin/config
  [301] POST http://example.com/admin/api

403 BYPASSED:
------------------------------------------------------------
  [200] GET http://example.com/admin/secure/.
    Technique: apache_dot
  [200] POST http://example.com/admin/hidden
    Technique: method_POST

============================================================
```

## Testing

Run the unit tests:

```bash
python -m pytest test_http_bruteforce.py -v
```

Or with unittest:

```bash
python -m unittest test_http_bruteforce.py -v
```

## Security & Legal Disclaimer

⚠️ **IMPORTANT**: This tool is provided for educational and authorized security testing purposes only.

### Ethical Use Guidelines

- **Authorization Required**: Only use this tool on systems you own or have explicit written permission to test
- **Responsible Disclosure**: Report any vulnerabilities found through proper channels
- **Rate Limiting**: Use appropriate delays to avoid overwhelming target systems
- **Legal Compliance**: Ensure compliance with local laws and regulations regarding security testing

### Prohibited Uses

❌ Unauthorized access to computer systems  
❌ Malicious attacks or exploitation  
❌ Testing systems without permission  
❌ Any illegal activities

**The authors and contributors are not responsible for misuse of this tool. Users are solely responsible for their actions and must ensure they have proper authorization before conducting any security testing.**

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

**kArmasec** 🚀+🦝+🏴‍☠️=🎩

Knowledge is power 🛸👽

## License

See [LICENSE](LICENSE) file for details.

---

**4TheLulz | LulzURLife | Made In l0v3 bY kArmasec**

# kArmas_ftpdUmper 🚀

**FTP Recursive Downloader & Brute Force Tool**

A powerful Python tool for FTP operations including recursive file downloading and credential brute-forcing with built-in wordlists.

## Features

### FTP Dump Mode
- 🔄 Recursive directory crawling
- 📊 Global progress bar tracking total bytes
- 📈 Per-file progress bars
- ⏸️ Resume support for interrupted downloads
- 🔁 Automatic retry logic with exponential backoff
- 📝 Comprehensive logging (file + console)

### Brute Force Mode
- 🔐 FTP credential brute-forcing
- 🌐 HTTP Basic Authentication brute-forcing
- 📚 Built-in common wordlists
- 🎯 Custom wordlist support
- ⚡ Multi-threaded attacks (configurable)
- 🕒 Rate limiting to prevent service overload
- 📊 Real-time progress tracking

## Installation

### Requirements
- Python 3.6+
- Required packages: `tqdm`, `requests`

### Install Dependencies
```bash
pip install tqdm requests
```

## Usage

### Mode 1: FTP Dump (Original Functionality)

Download entire FTP directory structure:

```bash
# Basic usage with command-line arguments
python3 kArmas_ftpdUmper.py --mode dump --host ftp.example.com --user john --pass secret

# With custom paths
python3 kArmas_ftpdUmper.py --mode dump --host ftp.example.com --user john --pass secret \
    --remote-root /data --local-root ./downloads
```

### Mode 2: FTP Brute-Force

Test FTP credentials using built-in or custom wordlists:

```bash
# Using built-in FTP credential pairs
python3 kArmas_ftpdUmper.py --mode ftp-bruteforce --host ftp.example.com \
    --wordlist ftp-credentials

# Using separate username and password lists
python3 kArmas_ftpdUmper.py --mode ftp-bruteforce --host ftp.example.com \
    --username-list common-usernames --password-list common-passwords

# Using custom wordlist
python3 kArmas_ftpdUmper.py --mode ftp-bruteforce --host ftp.example.com \
    --custom-wordlist /path/to/custom-creds.txt

# With performance tuning
python3 kArmas_ftpdUmper.py --mode ftp-bruteforce --host ftp.example.com \
    --wordlist ftp-credentials --threads 5 --delay 1.0 --verbose
```

### Mode 3: HTTP Brute-Force

Test HTTP Basic Authentication:

```bash
# Using built-in HTTP credentials
python3 kArmas_ftpdUmper.py --mode http-bruteforce \
    --url http://example.com/admin --wordlist http-credentials

# Using separate username and password lists
python3 kArmas_ftpdUmper.py --mode http-bruteforce \
    --url http://example.com/admin \
    --username-list common-usernames --password-list common-passwords

# Using custom wordlist
python3 kArmas_ftpdUmper.py --mode http-bruteforce \
    --url http://example.com/admin \
    --custom-wordlist /path/to/custom-creds.txt
```

## Built-in Wordlists

The tool includes optimized wordlists in the `wordlists/` directory:

| Wordlist | Description | Entries |
|----------|-------------|---------|
| `common-usernames.txt` | Common usernames across all services | ~21 |
| `common-passwords.txt` | Common weak passwords and defaults | ~100 |
| `ftp-credentials.txt` | FTP-specific username:password pairs | ~25 |
| `http-credentials.txt` | HTTP Basic Auth credential pairs | ~25 |

For more details, see [wordlists/README.md](wordlists/README.md)

## Command-Line Options

### General Options
- `--mode` - Operation mode: `dump`, `ftp-bruteforce`, `http-bruteforce` (default: dump)
- `--host` - Target FTP host (required for dump and ftp-bruteforce modes)
- `--port` - FTP port (default: 21)
- `--url` - Target HTTP URL (required for http-bruteforce mode)
- `--timeout` - Connection timeout in seconds (default: 30)
- `--verbose`, `-v` - Enable verbose output

### Dump Mode Options
- `--user` - FTP username
- `--pass` - FTP password
- `--remote-root` - Remote directory to dump (default: /)
- `--local-root` - Local directory for dump (default: ftp_dump)

### Brute-Force Wordlist Options
- `--wordlist` - Built-in credential wordlist name (e.g., `ftp-credentials`)
- `--username-list` - Built-in username wordlist name (e.g., `common-usernames`)
- `--password-list` - Built-in password wordlist name (e.g., `common-passwords`)
- `--custom-wordlist` - Path to custom wordlist file (username:password format)

### Brute-Force Performance Options
- `--delay` - Delay between attempts in seconds (default: 0.5)
- `--threads` - Number of concurrent threads (default: 3, max: 10)

## Configuration

Default settings can be modified in the `kArmas_ftpdUmper.py` file:

```python
# ===================== CONFIG =====================
FTP_HOST = "ftp.jar2.org"
FTP_USER = "John"
FTP_PASS = "letmein"

REMOTE_ROOT = "/"
LOCAL_ROOT = "ftp_dump"

CHUNK_SIZE = 1024 * 1024  # 1MB
TIMEOUT = 30

MAX_RETRIES = 3
RETRY_DELAY = 5

LOG_FILE = "kArmas_ftpdUmper.log"
# =================================================
```

## Examples

### Example 1: Complete FTP Dump
```bash
python3 kArmas_ftpdUmper.py --mode dump \
    --host ftp.example.com \
    --user myuser \
    --pass mypassword \
    --remote-root /public \
    --local-root ./ftp_backup
```

### Example 2: Quick FTP Credential Test
```bash
# Test common FTP defaults
python3 kArmas_ftpdUmper.py --mode ftp-bruteforce \
    --host ftp.target.com \
    --wordlist ftp-credentials
```

### Example 3: Comprehensive Password Attack
```bash
# Test all combinations of common usernames and passwords
python3 kArmas_ftpdUmper.py --mode ftp-bruteforce \
    --host ftp.target.com \
    --username-list common-usernames \
    --password-list common-passwords \
    --threads 5 \
    --delay 0.3 \
    --verbose
```

### Example 4: HTTP Admin Panel Test
```bash
python3 kArmas_ftpdUmper.py --mode http-bruteforce \
    --url https://target.com/admin \
    --wordlist http-credentials \
    --threads 3 \
    --delay 1.0
```

## Ethical Use and Legal Disclaimer

⚠️ **IMPORTANT LEGAL NOTICE**

This tool is provided for **educational purposes** and **authorized security testing ONLY**.

### Legal Requirements
- ✅ **Written Authorization Required**: Only use this tool on systems you own or have explicit written permission to test
- ⚠️ **Unauthorized Access is Illegal**: Unauthorized access to computer systems violates laws in most jurisdictions including:
  - Computer Fraud and Abuse Act (CFAA) in the United States
  - Computer Misuse Act in the United Kingdom
  - Similar legislation in other countries
- 📝 **Document Everything**: Keep records of authorization and testing scope

### Ethical Guidelines
1. **Always Get Permission First** - Obtain written authorization before any testing
2. **Respect Rate Limits** - Use appropriate delays to avoid denial of service
3. **Responsible Disclosure** - Report vulnerabilities privately to system owners
4. **No Data Theft** - Do not access, copy, or exfiltrate data without permission
5. **Minimize Impact** - Conduct tests during approved maintenance windows when possible

### Intended Use Cases
✅ Authorized penetration testing engagements  
✅ Security research with explicit permission  
✅ Testing your own systems and infrastructure  
✅ Educational demonstrations in controlled environments  
✅ Red team exercises with proper authorization  

### Prohibited Activities
❌ Unauthorized credential testing  
❌ Attacking systems without permission  
❌ Data theft or exfiltration  
❌ Denial of service attacks  
❌ Privacy violations  

**By using this tool, you accept full responsibility for your actions and any legal consequences. The authors are not responsible for misuse.**

## Performance and Safety

### Rate Limiting
The tool implements built-in rate limiting to prevent overloading target systems:
- Default delay: 0.5 seconds between attempts
- Configurable via `--delay` parameter
- Recommended: 0.5-2.0 seconds for production systems

### Thread Safety
- Default: 3 concurrent threads
- Maximum: 10 threads (enforced)
- Configurable via `--threads` parameter
- Lower thread counts = safer for target systems

### Wordlist Optimization
All built-in wordlists are optimized for:
- ✅ No duplicate entries
- ✅ Focus on most common credentials
- ✅ Reasonable size (not excessive)
- ✅ Categorized by use case

## Logging

All operations are logged to:
- **Console** - Real-time progress and results
- **Log File** - `kArmas_ftpdUmper.log` - Detailed operation history

Log levels:
- `INFO` - Standard operation information
- `DEBUG` - Detailed debugging (use `--verbose`)
- `WARNING` - Non-critical issues
- `ERROR` - Critical failures

## Troubleshooting

### Common Issues

**ImportError: No module named 'tqdm' or 'requests'**
```bash
pip install tqdm requests
```

**"bruteforce module not found"**
- Ensure `bruteforce.py` is in the same directory as `kArmas_ftpdUmper.py`

**"Wordlist not found"**
- Ensure the `wordlists/` directory exists in the same directory as the script
- Check that wordlist names are correct (without .txt extension)

**Connection timeouts**
- Increase timeout: `--timeout 60`
- Check network connectivity
- Verify target host is accessible

**Rate limiting / IP blocks**
- Increase delay: `--delay 2.0`
- Reduce threads: `--threads 1`
- Use proxy/VPN if appropriate (with authorization)

## Contributing

Contributions are welcome! Please:
1. Follow existing code style
2. Test your changes thoroughly
3. Update documentation as needed
4. Ensure wordlists have no duplicates
5. Keep commits focused and atomic

## Author

**kArmasec** 🚀+🦝+🏴‍☠️=🎩

*knowledge is power* 🛸👽

## License

See [LICENSE](LICENSE) file for details.

---

**Remember**: With great power comes great responsibility. Use this tool ethically and legally. 🛡️

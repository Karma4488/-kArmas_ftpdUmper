# kArmas_ftpdUmper 🚀

**FTP Recursive Downloader & Bruteforce Tool**

A powerful Python tool for FTP operations including recursive downloading and authentication testing.

## Features

### Download Mode
- 🔄 Recursive directory crawling
- 📊 Global progress bar (tracks all files)
- 📈 Per-file progress bars
- ⏯️ Resume support for interrupted downloads
- 🔁 Automatic retry logic
- 📝 Comprehensive logging (file + console)

### Bruteforce Mode (NEW!)
- 🔐 FTP authentication brute-forcing
- 📋 Dictionary-based password testing
- ⚙️ Configurable via JSON config file
- 🎯 Stop on first success option
- ⏱️ Configurable timeouts and delays
- 📊 Detailed results reporting
- 🔍 Multiple verbosity levels

## Installation

```bash
# Clone the repository
git clone https://github.com/Karma4488/-kArmas_ftpdUmper.git
cd -kArmas_ftpdUmper

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Download Mode (Default)

Edit the configuration in `kArmas_ftpdUmper.py`:

```python
FTP_HOST = "ftp.example.com"
FTP_USER = "username"
FTP_PASS = "password"
REMOTE_ROOT = "/"
LOCAL_ROOT = "ftp_dump"
```

Then run:

```bash
python kArmas_ftpdUmper.py
```

### Bruteforce Mode

#### Using Configuration File

Create or edit `ftp_config.json`:

```json
{
  "server": {
    "host": "ftp.example.com",
    "port": 21,
    "timeout": 10
  },
  "credentials": {
    "username": "admin",
    "password_list": [
      "admin",
      "password",
      "123456",
      "letmein"
    ]
  },
  "bruteforce": {
    "max_attempts": 100,
    "delay_between_attempts": 1,
    "verbosity": 2,
    "stop_on_success": true
  }
}
```

Run bruteforce with config:

```bash
python kArmas_ftpdUmper.py --mode bruteforce
```

#### Using Password File

Create a password list file (e.g., `passwords.txt`):

```
admin
password123
letmein
qwerty
```

Run bruteforce with password file:

```bash
python kArmas_ftpdUmper.py --mode bruteforce --username admin --password-file passwords.txt
```

#### Using Standalone Module

You can also use the bruteforce module directly:

```bash
# With config file
python ftp_bruteforce.py

# With custom config
python ftp_bruteforce.py --config my_config.json

# With password file
python ftp_bruteforce.py --username admin --password-file passwords.txt
```

## Configuration Options

### Bruteforce Configuration

- **server.host**: FTP server address
- **server.port**: FTP server port (default: 21)
- **server.timeout**: Connection timeout in seconds
- **credentials.username**: Username to test
- **credentials.password_list**: Array of passwords to test
- **bruteforce.max_attempts**: Maximum number of login attempts
- **bruteforce.delay_between_attempts**: Delay in seconds between attempts
- **bruteforce.verbosity**: Logging detail level (0-3)
  - 0: Minimal (only successes and errors)
  - 1: Normal (includes warnings)
  - 2: Verbose (includes debug info)
  - 3: Very verbose (all attempts)
- **bruteforce.stop_on_success**: Stop after finding valid credentials

## Examples

### Example 1: Basic Bruteforce

```bash
python kArmas_ftpdUmper.py --mode bruteforce
```

### Example 2: Custom Configuration

```bash
python kArmas_ftpdUmper.py --mode bruteforce --config prod_config.json
```

### Example 3: Large Password List

```bash
python kArmas_ftpdUmper.py --mode bruteforce --username root --password-file rockyou.txt
```

### Example 4: Download Mode

```bash
python kArmas_ftpdUmper.py --mode download
# or simply:
python kArmas_ftpdUmper.py
```

## Testing

Run the test suite:

```bash
pytest test_ftp_bruteforce.py -v
```

Or with unittest:

```bash
python -m unittest test_ftp_bruteforce.py -v
```

## Output and Logging

### Download Mode
- Logs to `kArmas_ftpdUmper.log`
- Console output with progress bars
- Downloaded files saved to `LOCAL_ROOT` directory

### Bruteforce Mode
- Logs to `ftp_bruteforce.log`
- Console output with attempt status
- Successful credentials highlighted in the final report

### Sample Bruteforce Report

```
============================================================
FTP BRUTEFORCE REPORT
============================================================
Total attempts: 50
Failed attempts: 49
Successful attempts: 1
Elapsed time: 52.34 seconds
Attempts per second: 0.96

------------------------------------------------------------
SUCCESSFUL CREDENTIALS:
------------------------------------------------------------
Host: ftp.example.com:21 | User: admin | Pass: letmein
============================================================
```

## Error Handling

The tool includes comprehensive error handling for:
- Connection timeouts
- Authentication failures
- Server disconnections
- Invalid responses
- File system errors
- Configuration errors

## Security Considerations

⚠️ **IMPORTANT DISCLAIMERS:**

1. **Legal Use Only**: This tool is for authorized security testing and educational purposes only. Unauthorized access to computer systems is illegal.

2. **Authorization Required**: Always obtain explicit written permission before testing any system you don't own.

3. **Rate Limiting**: Be mindful of rate limits and implement appropriate delays to avoid overloading servers.

4. **Logging**: All attempts are logged. Ensure you have proper authorization before running bruteforce operations.

5. **Responsible Disclosure**: If you discover vulnerabilities, follow responsible disclosure practices.

## Requirements

- Python 3.9+
- tqdm (for progress bars)
- Standard library modules (ftplib, logging, json, argparse)

## Author

**kArmasec**

🚀 Made In l0v3  
🦝 4TheLulz  
🏴‍☠️ LulzURLife  
🎩 Knowledge is power

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

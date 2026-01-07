# Built-in Wordlists

This directory contains common wordlists for brute-force attacks on various services.

## Files

### `common-usernames.txt`
- Contains 21 common usernames
- General-purpose username list for any service
- Includes default admin accounts, service accounts, and common user names

### `common-passwords.txt`
- Contains 100+ common passwords
- Includes weak passwords, default passwords, and common patterns
- Suitable for testing password security across all services

### `ftp-credentials.txt`
- FTP-specific username:password combinations
- Format: `username:password` (one per line)
- Contains default FTP credentials for various systems
- Includes anonymous FTP login patterns

### `http-credentials.txt`
- HTTP Basic Authentication credentials
- Format: `username:password` (one per line)
- Common defaults for web admin panels and protected directories
- Suitable for HTTP/HTTPS Basic Auth attacks

## Usage

These wordlists are automatically available when using the brute-force features of kArmas_ftpdUmper.

### Using Built-in Wordlists

```bash
# FTP brute-force with built-in credentials
python3 kArmas_ftpdUmper.py --mode ftp-bruteforce --host target.com --wordlist ftp-credentials

# FTP brute-force with separate username/password lists
python3 kArmas_ftpdUmper.py --mode ftp-bruteforce --host target.com \
    --username-list common-usernames --password-list common-passwords

# HTTP brute-force with built-in credentials
python3 kArmas_ftpdUmper.py --mode http-bruteforce --url http://target.com/admin \
    --wordlist http-credentials
```

## Size and Performance

- All wordlists are optimized for size and performance
- No duplicate entries
- Focused on most common credentials to minimize attack time
- Rate limiting is enforced to prevent overloading target systems

## Ethical Use and Legal Disclaimer

⚠️ **IMPORTANT**: These wordlists are provided for educational and authorized security testing purposes ONLY.

### Legal Requirements
- **Authorization Required**: Only use these tools and wordlists against systems you own or have explicit written permission to test
- **Legal Consequences**: Unauthorized access to computer systems is illegal in most jurisdictions
- **Compliance**: Ensure compliance with local laws and regulations

### Ethical Guidelines
1. **Permission First**: Always obtain written authorization before conducting any security tests
2. **Responsible Disclosure**: Report vulnerabilities to system owners privately
3. **No Harm**: Do not damage, modify, or steal data from target systems
4. **Respect Privacy**: Do not access or collect personal information without consent
5. **Rate Limiting**: Use appropriate delays to avoid denial of service

### Intended Use Cases
✅ Authorized penetration testing
✅ Security research with permission
✅ Testing your own systems
✅ Educational purposes in controlled environments
✅ Red team exercises with authorization

### Prohibited Use Cases
❌ Unauthorized access attempts
❌ Malicious attacks
❌ Data theft
❌ System damage
❌ Privacy violations

**By using these wordlists, you acknowledge that you are solely responsible for your actions and any legal consequences.**

## Adding Custom Wordlists

You can also use your own custom wordlists:

```bash
# Use custom wordlist file
python3 kArmas_ftpdUmper.py --mode ftp-bruteforce --host target.com \
    --custom-wordlist /path/to/your/wordlist.txt
```

## Contributing

If you want to suggest additions to these wordlists:
1. Ensure no duplicates
2. Focus on common/default credentials
3. Keep lists concise and effective
4. Follow existing format conventions

#!/usr/bin/env python3
"""
kArmas_ftpdUmper
----------------
FTP Recursive Downloader & Brute Force Tool
- Recursive crawl
- Global progress bar (all files)
- Per-file progress bar
- Resume support
- Retry logic
- Logging (file + console)
- FTP/HTTP Brute-force with built-in wordlists
- Made In l0v3 bY kArmasec
- 4TheLulz 
- LulzURLife
- Prank
- Author: kArmasec
"""

from ftplib import FTP, error_perm, all_errors
from tqdm import tqdm
import os
import sys
import time
import logging
import argparse

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


# --------------------- LOGGING ---------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("kArmas_ftpdUmper")
# --------------------------------------------------


def ensure_dir(path):
    if path:
        os.makedirs(path, exist_ok=True)


def is_dir_fallback(ftp, name):
    cur = ftp.pwd()
    try:
        ftp.cwd(name)
        ftp.cwd(cur)
        return True
    except error_perm:
        return False


# -------- PRE-SCAN TO CALCULATE TOTAL SIZE --------
def scan_tree(ftp, remote_dir):
    total_size = 0
    ftp.cwd(remote_dir)

    try:
        entries = list(ftp.mlsd())
        use_mlsd = True
    except:
        entries = ftp.nlst()
        use_mlsd = False

    for entry in entries:
        if use_mlsd:
            name, facts = entry
            is_dir = facts.get("type") == "dir"
        else:
            name = entry
            if name in (".", ".."):
                continue
            is_dir = is_dir_fallback(ftp, name)

        if is_dir:
            total_size += scan_tree(ftp, name)
            ftp.cwd("..")
        else:
            try:
                size = ftp.size(name)
                if size:
                    total_size += size
            except:
                pass

    return total_size
# --------------------------------------------------


def download_file(ftp, remote_name, local_path, global_bar):
    ensure_dir(os.path.dirname(local_path))

    try:
        remote_size = ftp.size(remote_name)
    except:
        log.error(f"Cannot get size: {remote_name}")
        return

    resume_pos = 0
    if os.path.exists(local_path):
        resume_pos = os.path.getsize(local_path)
        if resume_pos >= remote_size:
            global_bar.update(0)
            log.info(f"Skipped (complete): {remote_name}")
            return

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with open(local_path, "ab") as f, tqdm(
                total=remote_size,
                initial=resume_pos,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=os.path.basename(remote_name),
                position=1,
                leave=False,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} "
                           "[{elapsed}<{remaining}, {rate_fmt}]",
            ) as file_bar:

                if resume_pos > 0:
                    ftp.sendcmd(f"REST {resume_pos}")

                def callback(data):
                    f.write(data)
                    size = len(data)
                    file_bar.update(size)
                    global_bar.update(size)

                ftp.retrbinary(
                    f"RETR {remote_name}",
                    callback,
                    blocksize=CHUNK_SIZE,
                )

            log.info(f"Downloaded: {remote_name}")
            return

        except all_errors as e:
            log.warning(
                f"Retry {attempt}/{MAX_RETRIES} failed for "
                f"{remote_name}: {e}"
            )
            time.sleep(RETRY_DELAY)
            try:
                resume_pos = os.path.getsize(local_path)
            except:
                resume_pos = 0

    log.error(f"FAILED after retries: {remote_name}")


def crawl(ftp, remote_dir, local_dir, global_bar):
    ensure_dir(local_dir)
    ftp.cwd(remote_dir)

    try:
        entries = list(ftp.mlsd())
        use_mlsd = True
    except:
        entries = ftp.nlst()
        use_mlsd = False

    for entry in entries:
        if use_mlsd:
            name, facts = entry
            is_dir = facts.get("type") == "dir"
        else:
            name = entry
            if name in (".", ".."):
                continue
            is_dir = is_dir_fallback(ftp, name)

        local_path = os.path.join(local_dir, name)

        if is_dir:
            log.info(f"Entering dir: {ftp.pwd()}/{name}")
            crawl(ftp, name, local_path, global_bar)
            ftp.cwd("..")
        else:
            download_file(ftp, name, local_path, global_bar)


def main_dump(host=None, user=None, password=None, remote_root=None, 
              local_root=None, timeout=None):
    """Run FTP dump mode (original functionality)."""
    # Use provided arguments or fall back to config
    host = host or FTP_HOST
    user = user or FTP_USER
    password = password or FTP_PASS
    remote_root = remote_root or REMOTE_ROOT
    local_root = local_root or LOCAL_ROOT
    timeout = timeout or TIMEOUT
    
    log.info("Starting kArmas_ftpdUmper in DUMP mode")

    ftp = FTP(host, timeout=timeout)
    ftp.login(user, password)
    ftp.set_pasv(True)

    log.info("Scanning remote tree for total size...")
    total_bytes = scan_tree(ftp, remote_root)
    log.info(f"Total size: {total_bytes / (1024**2):.2f} MB")

    with tqdm(
        total=total_bytes,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc="TOTAL",
        position=0,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} "
                   "[{elapsed}<{remaining}, {rate_fmt}]",
    ) as global_bar:

        crawl(ftp, remote_root, local_root, global_bar)

    ftp.quit()
    log.info("kArmas_ftpdUmper completed")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="kArmas_ftpdUmper - FTP Dumper & Brute Force Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # FTP Dump mode (original functionality)
  %(prog)s --mode dump --host ftp.example.com --user john --pass secret
  
  # FTP Brute-force with built-in credentials
  %(prog)s --mode ftp-bruteforce --host ftp.example.com --wordlist ftp-credentials
  
  # FTP Brute-force with separate username/password lists
  %(prog)s --mode ftp-bruteforce --host ftp.example.com \\
      --username-list common-usernames --password-list common-passwords
  
  # HTTP Brute-force with built-in credentials
  %(prog)s --mode http-bruteforce --url http://example.com/admin \\
      --wordlist http-credentials
  
  # Use custom wordlist
  %(prog)s --mode ftp-bruteforce --host ftp.example.com \\
      --custom-wordlist /path/to/wordlist.txt

Ethical Use Notice:
  This tool is for authorized security testing only. Unauthorized access
  to systems is illegal. Always obtain written permission before testing.
        """
    )
    
    # Mode selection
    parser.add_argument(
        '--mode',
        choices=['dump', 'ftp-bruteforce', 'http-bruteforce'],
        default='dump',
        help='Operation mode (default: dump)'
    )
    
    # Common options
    parser.add_argument('--host', help='FTP host (for dump and ftp-bruteforce modes)')
    parser.add_argument('--port', type=int, default=21, help='FTP port (default: 21)')
    parser.add_argument('--url', help='HTTP URL (for http-bruteforce mode)')
    parser.add_argument('--timeout', type=int, default=TIMEOUT, 
                       help=f'Connection timeout in seconds (default: {TIMEOUT})')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    # Dump mode options
    parser.add_argument('--user', help='FTP username (for dump mode)')
    parser.add_argument('--pass', dest='password', help='FTP password (for dump mode)')
    parser.add_argument('--remote-root', default=REMOTE_ROOT,
                       help=f'Remote directory to dump (default: {REMOTE_ROOT})')
    parser.add_argument('--local-root', default=LOCAL_ROOT,
                       help=f'Local directory for dump (default: {LOCAL_ROOT})')
    
    # Brute-force wordlist options
    parser.add_argument('--wordlist',
                       help='Built-in credential wordlist name (e.g., ftp-credentials, http-credentials)')
    parser.add_argument('--username-list',
                       help='Built-in username wordlist name (e.g., common-usernames)')
    parser.add_argument('--password-list',
                       help='Built-in password wordlist name (e.g., common-passwords)')
    parser.add_argument('--custom-wordlist',
                       help='Path to custom wordlist file (username:password format)')
    
    # Brute-force performance options
    parser.add_argument('--delay', type=float, default=0.5,
                       help='Delay between attempts in seconds (default: 0.5)')
    parser.add_argument('--threads', type=int, default=3,
                       help='Number of concurrent threads (default: 3, max: 10)')
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Set log level
    if args.verbose:
        log.setLevel(logging.DEBUG)
    
    try:
        if args.mode == 'dump':
            # FTP Dump mode
            if not args.host and not FTP_HOST:
                log.error("Error: --host is required for dump mode")
                sys.exit(1)
            
            main_dump(
                host=args.host,
                user=args.user,
                password=args.password,
                remote_root=args.remote_root,
                local_root=args.local_root,
                timeout=args.timeout
            )
            
        elif args.mode == 'ftp-bruteforce':
            # FTP Brute-force mode
            if not args.host:
                log.error("Error: --host is required for ftp-bruteforce mode")
                sys.exit(1)
            
            # Check wordlist options
            if not (args.wordlist or args.custom_wordlist or 
                   (args.username_list and args.password_list)):
                log.error("Error: Must specify --wordlist, --custom-wordlist, or both --username-list and --password-list")
                sys.exit(1)
            
            # Import brute force module
            try:
                from bruteforce import run_ftp_bruteforce
            except ImportError:
                log.error("Error: bruteforce module not found. Ensure bruteforce.py is in the same directory.")
                sys.exit(1)
            
            result = run_ftp_bruteforce(
                host=args.host,
                port=args.port,
                wordlist=args.wordlist,
                username_list=args.username_list,
                password_list=args.password_list,
                custom_wordlist=args.custom_wordlist,
                timeout=args.timeout,
                delay=args.delay,
                threads=args.threads,
                verbose=args.verbose
            )
            
            if result:
                log.info(f"SUCCESS! Valid username found: {result[0]}")
                sys.exit(0)
            else:
                log.info("No valid credentials found.")
                sys.exit(1)
        
        elif args.mode == 'http-bruteforce':
            # HTTP Brute-force mode
            if not args.url:
                log.error("Error: --url is required for http-bruteforce mode")
                sys.exit(1)
            
            # Check wordlist options
            if not (args.wordlist or args.custom_wordlist or 
                   (args.username_list and args.password_list)):
                log.error("Error: Must specify --wordlist, --custom-wordlist, or both --username-list and --password-list")
                sys.exit(1)
            
            # Import brute force module
            try:
                from bruteforce import run_http_bruteforce
            except ImportError:
                log.error("Error: bruteforce module not found. Ensure bruteforce.py is in the same directory.")
                sys.exit(1)
            
            result = run_http_bruteforce(
                url=args.url,
                wordlist=args.wordlist,
                username_list=args.username_list,
                password_list=args.password_list,
                custom_wordlist=args.custom_wordlist,
                timeout=args.timeout,
                delay=args.delay,
                threads=args.threads,
                verbose=args.verbose
            )
            
            if result:
                log.info(f"SUCCESS! Valid username found: {result[0]}")
                sys.exit(0)
            else:
                log.info("No valid credentials found.")
                sys.exit(1)
    
    except KeyboardInterrupt:
        log.warning("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        log.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

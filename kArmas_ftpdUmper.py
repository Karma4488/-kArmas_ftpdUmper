#!/usr/bin/env python3
"""
kArmas_ftpdUmper
----------------
FTP Recursive Downloader + HTTP Brute-forcer with 403 Bypass
- Recursive FTP crawl
- Global progress bar (all files)
- Per-file progress bar
- Resume support
- Retry logic
- HTTP Brute-forcing with 403 bypass techniques
- Logging (file + console)
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
import json

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


def main_ftp():
    """Main function for FTP mode"""
    log.info("Starting kArmas_ftpdUmper - FTP Mode")

    ftp = FTP(FTP_HOST, timeout=TIMEOUT)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.set_pasv(True)

    log.info("Scanning remote tree for total size...")
    total_bytes = scan_tree(ftp, REMOTE_ROOT)
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

        crawl(ftp, REMOTE_ROOT, LOCAL_ROOT, global_bar)

    ftp.quit()
    log.info("kArmas_ftpdUmper FTP completed")


def main_http(args):
    """Main function for HTTP brute-force mode"""
    try:
        from http_bruteforce import HTTPBruteForcer, load_wordlist
    except ImportError:
        log.error("HTTP bruteforce module not found. Please ensure http_bruteforce.py is present.")
        sys.exit(1)

    log.info("Starting kArmas_ftpdUmper - HTTP Brute-force Mode")

    # Load configuration if provided
    config = {}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f).get('http_bruteforce', {})
            log.info(f"Loaded configuration from {args.config}")
        except Exception as e:
            log.error(f"Failed to load config: {e}")
            sys.exit(1)

    # Override config with command-line arguments
    target_url = args.url or config.get('target_url')
    if not target_url:
        log.error("Target URL is required. Use --url or specify in config file.")
        sys.exit(1)

    methods = args.methods or config.get('methods', ['GET', 'POST'])
    wordlist_path = args.wordlist or config.get('wordlist_path')
    verbose = args.verbose or config.get('verbose', False)
    enable_bypass = not args.no_bypass and config.get('enable_bypass', True)
    delay = args.delay if args.delay is not None else config.get('delay', 0)

    # Load wordlist
    wordlist = []
    if wordlist_path:
        wordlist = load_wordlist(wordlist_path)
        if not wordlist:
            log.warning(f"No wordlist loaded from {wordlist_path}")
    
    # Parse headers
    headers = config.get('headers', {})
    if args.headers:
        for header in args.headers:
            if ':' in header:
                key, value = header.split(':', 1)
                headers[key.strip()] = value.strip()

    # Parse proxies
    proxies = config.get('proxies', {})
    if args.proxy:
        proxies = {'http': args.proxy, 'https': args.proxy}

    # Initialize brute-forcer
    bruteforcer = HTTPBruteForcer(
        target_url=target_url,
        wordlist=wordlist,
        methods=methods,
        headers=headers,
        proxies=proxies if (proxies and proxies.get('http')) else None,
        timeout=args.timeout or config.get('timeout', 10),
        max_retries=args.retries or config.get('max_retries', 3),
        delay=delay,
        verbose=verbose,
        enable_bypass=enable_bypass,
        success_codes=config.get('success_codes', [200, 201, 202, 301, 302]),
    )

    # Run the appropriate mode
    if args.mode == 'scan':
        # Endpoint scanning mode
        if not wordlist:
            log.error("Wordlist is required for endpoint scanning")
            sys.exit(1)
        results = bruteforcer.scan_endpoints(wordlist)
    elif args.mode == 'auth':
        # Authentication brute-force mode
        username = args.username or config.get('authentication', {}).get('username')
        if not username:
            log.error("Username is required for auth mode. Use --username")
            sys.exit(1)
        results = bruteforcer.brute_force(username=username, password_list=wordlist)
    else:
        # Default: endpoint scanning if wordlist provided
        if wordlist:
            results = bruteforcer.scan_endpoints(wordlist)
        else:
            log.error("No wordlist provided. Nothing to brute-force.")
            sys.exit(1)

    # Print summary
    summary = bruteforcer.get_results_summary()
    print(summary)
    log.info(summary)

    # Save results if output file specified
    if args.output:
        try:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            log.info(f"Results saved to {args.output}")
        except Exception as e:
            log.error(f"Failed to save results: {e}")

    log.info("kArmas_ftpdUmper HTTP completed")


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description='kArmas_ftpdUmper - FTP Dumper & HTTP Brute-forcer with 403 Bypass',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  FTP Mode (default):
    %(prog)s
    
  HTTP Endpoint Scanning:
    %(prog)s --http --url http://example.com --wordlist wordlist.txt
    
  HTTP Authentication Brute-force:
    %(prog)s --http --mode auth --url http://example.com/login --username admin --wordlist passwords.txt
    
  HTTP with 403 Bypass:
    %(prog)s --http --url http://example.com/admin --wordlist wordlist.txt --verbose
    
  Using Configuration File:
    %(prog)s --http --config config.json

Author: kArmasec
        """
    )

    parser.add_argument('--http', action='store_true', 
                       help='Enable HTTP brute-force mode (default: FTP mode)')
    parser.add_argument('--mode', choices=['scan', 'auth'], default='scan',
                       help='HTTP mode: scan endpoints or brute-force auth (default: scan)')
    parser.add_argument('--url', type=str,
                       help='Target URL for HTTP brute-force')
    parser.add_argument('--methods', nargs='+', 
                       help='HTTP methods to use (e.g., GET POST PUT)')
    parser.add_argument('--wordlist', type=str,
                       help='Path to wordlist file')
    parser.add_argument('--username', type=str,
                       help='Username for authentication brute-force')
    parser.add_argument('--headers', nargs='+',
                       help='Custom headers (format: "Key: Value")')
    parser.add_argument('--proxy', type=str,
                       help='Proxy URL (e.g., http://127.0.0.1:8080)')
    parser.add_argument('--timeout', type=int,
                       help='Request timeout in seconds')
    parser.add_argument('--retries', type=int,
                       help='Maximum number of retries per request')
    parser.add_argument('--delay', type=float,
                       help='Delay between requests in seconds')
    parser.add_argument('--no-bypass', action='store_true',
                       help='Disable 403 bypass techniques')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--config', type=str,
                       help='Path to JSON configuration file')
    parser.add_argument('--output', type=str,
                       help='Output file for results (JSON format)')

    args = parser.parse_args()

    # Choose mode
    if args.http:
        main_http(args)
    else:
        main_ftp()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Interrupted by user")
        sys.exit(1)

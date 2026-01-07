#!/usr/bin/env python3
"""
Unit tests for HTTP Brute-forcing with 403 Bypass
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from http_bruteforce import HTTPBruteForcer, load_wordlist


class TestHTTPBruteForcer(unittest.TestCase):
    """Test cases for HTTPBruteForcer class"""

    def setUp(self):
        """Set up test fixtures"""
        self.target_url = "http://example.com/admin"
        self.wordlist = ["admin", "test", "root"]
        self.bruteforcer = HTTPBruteForcer(
            target_url=self.target_url,
            wordlist=self.wordlist,
            methods=["GET"],
            timeout=5,
            delay=0,
            enable_bypass=True,
            verbose=False
        )

    def test_initialization(self):
        """Test HTTPBruteForcer initialization"""
        self.assertEqual(self.bruteforcer.target_url, self.target_url)
        self.assertEqual(self.bruteforcer.wordlist, self.wordlist)
        self.assertEqual(self.bruteforcer.methods, ["GET"])
        self.assertTrue(self.bruteforcer.enable_bypass)
        self.assertEqual(self.bruteforcer.timeout, 5)

    def test_apply_bypass_technique_apache_dot(self):
        """Test Apache dot bypass technique"""
        url = "http://example.com/admin"
        result = self.bruteforcer._apply_bypass_technique(url, "apache_dot")
        self.assertEqual(result, "http://example.com/admin/.")

    def test_apply_bypass_technique_trailing_slash(self):
        """Test trailing slash bypass technique"""
        url = "http://example.com/admin"
        result = self.bruteforcer._apply_bypass_technique(url, "trailing_slash")
        self.assertEqual(result, "http://example.com/admin/")

    @patch('http_bruteforce.requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful HTTP request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Success"
        mock_get.return_value = mock_response

        response, error = self.bruteforcer._make_request("http://example.com", "GET")
        
        self.assertIsNotNone(response)
        self.assertIsNone(error)
        self.assertEqual(response.status_code, 200)

    @patch('http_bruteforce.requests.Session.get')
    def test_make_request_failure(self, mock_get):
        """Test failed HTTP request"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        response, error = self.bruteforcer._make_request("http://example.com", "GET")
        
        self.assertIsNone(response)
        self.assertIsNotNone(error)

    @patch('http_bruteforce.requests.Session.post')
    def test_make_request_post_method(self, mock_post):
        """Test POST request method"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        response, error = self.bruteforcer._make_request(
            "http://example.com", "POST", data={"key": "value"}
        )
        
        self.assertIsNotNone(response)
        self.assertIsNone(error)
        mock_post.assert_called_once()

    @patch('http_bruteforce.requests.Session.get')
    def test_try_bypass_403_success(self, mock_get):
        """Test successful 403 bypass"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Bypassed"
        mock_get.return_value = mock_response

        result = self.bruteforcer._try_bypass_403("http://example.com/admin", "GET")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["status_code"], 200)
        self.assertIn("technique", result)

    @patch('http_bruteforce.requests.Session.get')
    def test_try_bypass_403_failure(self, mock_get):
        """Test failed 403 bypass"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.content = b"Forbidden"
        mock_get.return_value = mock_response

        result = self.bruteforcer._try_bypass_403("http://example.com/admin", "GET")
        
        # Should return None if all bypass attempts fail
        self.assertIsNone(result)

    @patch('http_bruteforce.requests.Session.get')
    def test_brute_force_endpoint_scan(self, mock_get):
        """Test endpoint scanning brute-force"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Success"
        mock_get.return_value = mock_response

        results = self.bruteforcer.brute_force()
        
        self.assertIn("successful", results)
        self.assertIn("failed", results)
        self.assertIn("bypassed_403", results)
        self.assertGreater(len(results["successful"]), 0)

    @patch('http_bruteforce.requests.Session.get')
    def test_brute_force_with_403_response(self, mock_get):
        """Test brute-force with 403 response triggering bypass"""
        mock_403_response = Mock()
        mock_403_response.status_code = 403
        mock_403_response.content = b"Forbidden"
        
        mock_200_response = Mock()
        mock_200_response.status_code = 200
        mock_200_response.content = b"Bypassed"
        
        # First call returns 403, subsequent calls return 200 (bypass success)
        mock_get.side_effect = [mock_403_response, mock_200_response] * 10

        results = self.bruteforcer.brute_force()
        
        # Check if bypass attempts were made
        self.assertIn("bypassed_403", results)

    @patch('http_bruteforce.requests.Session.get')
    def test_scan_endpoints(self, mock_get):
        """Test endpoint scanning functionality"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Success"
        mock_get.return_value = mock_response

        endpoint_list = ["/admin", "/config", "/debug"]
        results = self.bruteforcer.scan_endpoints(endpoint_list)
        
        self.assertIn("successful", results)
        self.assertGreater(len(results["successful"]), 0)

    @patch('http_bruteforce.requests.Session.post')
    def test_brute_force_authentication(self, mock_post):
        """Test authentication brute-force"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Login successful"
        mock_post.return_value = mock_response

        bruteforcer = HTTPBruteForcer(
            target_url="http://example.com/login",
            wordlist=["password123", "admin123"],
            methods=["POST"],
            timeout=5,
            delay=0,
            verbose=False
        )

        results = bruteforcer.brute_force(username="admin", password_list=["password123", "admin123"])
        
        self.assertIn("successful", results)

    def test_get_results_summary(self):
        """Test results summary generation"""
        self.bruteforcer.results["successful"] = [
            {"url": "http://example.com/admin", "method": "GET", "status_code": 200}
        ]
        self.bruteforcer.results["bypassed_403"] = [
            {"url": "http://example.com/config", "method": "GET", "status_code": 200, "technique": "apache_dot"}
        ]

        summary = self.bruteforcer.get_results_summary()
        
        self.assertIn("RESULTS SUMMARY", summary)
        self.assertIn("Successful requests: 1", summary)
        self.assertIn("Bypassed 403: 1", summary)

    def test_bypass_methods_exist(self):
        """Test that all bypass methods are defined"""
        expected_methods = ["apache_dot", "apache_double_slash", "trailing_slash", "case_variation", "url_encode"]
        for method in expected_methods:
            self.assertIn(method, HTTPBruteForcer.BYPASS_METHODS)

    def test_bypass_headers_exist(self):
        """Test that bypass headers are defined"""
        self.assertGreater(len(HTTPBruteForcer.BYPASS_HEADERS), 0)
        self.assertIsInstance(HTTPBruteForcer.BYPASS_HEADERS, list)

    def test_http_methods_supported(self):
        """Test that various HTTP methods are supported"""
        methods = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]
        for method in methods:
            bruteforcer = HTTPBruteForcer(
                target_url="http://example.com",
                methods=[method],
                timeout=5
            )
            self.assertIn(method, bruteforcer.methods)


class TestLoadWordlist(unittest.TestCase):
    """Test cases for load_wordlist function"""

    def test_load_wordlist_nonexistent_file(self):
        """Test loading a non-existent wordlist"""
        result = load_wordlist("nonexistent_file.txt")
        self.assertEqual(result, [])

    @patch('builtins.open', create=True)
    def test_load_wordlist_success(self, mock_open):
        """Test successful wordlist loading"""
        mock_open.return_value.__enter__.return_value = ["admin\n", "test\n", "root\n"]
        
        result = load_wordlist("test_wordlist.txt")
        
        self.assertEqual(len(result), 3)
        self.assertIn("admin", result)

    @patch('builtins.open', create=True)
    def test_load_wordlist_empty_lines(self, mock_open):
        """Test wordlist loading with empty lines"""
        mock_open.return_value.__enter__.return_value = ["admin\n", "\n", "test\n", ""]
        
        result = load_wordlist("test_wordlist.txt")
        
        # Empty lines should be filtered out
        self.assertNotIn("", result)


class TestBypassTechniques(unittest.TestCase):
    """Test cases for specific bypass techniques"""

    def setUp(self):
        """Set up test fixtures"""
        self.bruteforcer = HTTPBruteForcer(
            target_url="http://example.com/admin",
            enable_bypass=True
        )

    def test_apache_dot_bypass(self):
        """Test Apache dot bypass technique"""
        url = "http://example.com/admin"
        bypassed = self.bruteforcer.BYPASS_METHODS["apache_dot"](url)
        self.assertTrue(bypassed.endswith("/."))

    def test_trailing_slash_bypass(self):
        """Test trailing slash bypass"""
        url = "http://example.com/admin"
        bypassed = self.bruteforcer.BYPASS_METHODS["trailing_slash"](url)
        self.assertTrue(bypassed.endswith("/"))

    def test_trailing_slash_idempotent(self):
        """Test trailing slash is idempotent"""
        url = "http://example.com/admin/"
        bypassed = self.bruteforcer.BYPASS_METHODS["trailing_slash"](url)
        self.assertEqual(url, bypassed)

    @patch('http_bruteforce.requests.Session.get')
    def test_header_bypass_attempt(self, mock_get):
        """Test header-based bypass attempts"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Success"
        mock_get.return_value = mock_response

        result = self.bruteforcer._try_bypass_403("http://example.com/admin", "GET")
        
        # Should return a result with header information if successful
        if result:
            self.assertIn("status_code", result)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""
Unit tests for FTP Bruteforce module
"""

import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from ftp_bruteforce import FTPBruteforcer


class TestFTPBruteforcer(unittest.TestCase):
    """Test cases for FTPBruteforcer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        )
        
        config_data = {
            "server": {
                "host": "test.example.com",
                "port": 21,
                "timeout": 5
            },
            "credentials": {
                "username": "testuser",
                "password_list": ["pass1", "pass2", "pass3"]
            },
            "bruteforce": {
                "max_attempts": 10,
                "delay_between_attempts": 0,
                "verbosity": 1,
                "stop_on_success": True
            }
        }
        
        json.dump(config_data, self.temp_config)
        self.temp_config.close()
        
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_load_config(self):
        """Test configuration loading"""
        bruteforcer = FTPBruteforcer(config_path=self.temp_config.name)
        
        self.assertEqual(bruteforcer.config['server']['host'], 'test.example.com')
        self.assertEqual(bruteforcer.config['server']['port'], 21)
        self.assertEqual(bruteforcer.config['credentials']['username'], 'testuser')
        self.assertEqual(len(bruteforcer.config['credentials']['password_list']), 3)
    
    def test_load_config_file_not_found(self):
        """Test configuration loading with non-existent file"""
        with self.assertRaises(FileNotFoundError):
            FTPBruteforcer(config_path='nonexistent.json')
    
    def test_load_config_invalid_json(self):
        """Test configuration loading with invalid JSON"""
        bad_config = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        )
        bad_config.write("{ invalid json }")
        bad_config.close()
        
        try:
            with self.assertRaises(ValueError):
                FTPBruteforcer(config_path=bad_config.name)
        finally:
            os.unlink(bad_config.name)
    
    @patch('ftp_bruteforce.FTP')
    def test_successful_credentials(self, mock_ftp_class):
        """Test successful credential authentication"""
        # Mock FTP connection
        mock_ftp = MagicMock()
        mock_ftp.getwelcome.return_value = "Welcome to Test FTP"
        mock_ftp_class.return_value = mock_ftp
        
        bruteforcer = FTPBruteforcer(config_path=self.temp_config.name)
        success, error = bruteforcer.test_credentials('testuser', 'correctpass')
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(len(bruteforcer.successful_credentials), 1)
        self.assertEqual(bruteforcer.successful_credentials[0]['username'], 'testuser')
        self.assertEqual(bruteforcer.successful_credentials[0]['password'], 'correctpass')
    
    @patch('ftp_bruteforce.FTP')
    def test_failed_credentials(self, mock_ftp_class):
        """Test failed credential authentication"""
        from ftplib import error_perm
        
        # Mock FTP connection to raise error_perm
        mock_ftp = MagicMock()
        mock_ftp.login.side_effect = error_perm("530 Login incorrect")
        mock_ftp_class.return_value = mock_ftp
        
        bruteforcer = FTPBruteforcer(config_path=self.temp_config.name)
        success, error = bruteforcer.test_credentials('testuser', 'wrongpass')
        
        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertEqual(bruteforcer.failed_attempts, 1)
    
    @patch('ftp_bruteforce.FTP')
    def test_connection_timeout(self, mock_ftp_class):
        """Test connection timeout handling"""
        import socket

        # Mock FTP connection to raise timeout error
        mock_ftp_class.side_effect = socket.timeout("Connection timeout")

        bruteforcer = FTPBruteforcer(config_path=self.temp_config.name)
        success, error = bruteforcer.test_credentials('testuser', 'anypass')

        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertEqual(bruteforcer.failed_attempts, 1)
    
    @patch('ftp_bruteforce.FTP')
    def test_bruteforce_stop_on_success(self, mock_ftp_class):
        """Test bruteforce stops on first success when configured"""
        # Mock FTP: first two fail, third succeeds
        mock_ftp = MagicMock()
        
        def login_side_effect(user, password):
            if password == "pass2":
                return True  # Success
            else:
                from ftplib import error_perm
                raise error_perm("530 Login incorrect")
        
        mock_ftp.login.side_effect = login_side_effect
        mock_ftp.getwelcome.return_value = "Welcome"
        mock_ftp_class.return_value = mock_ftp
        
        bruteforcer = FTPBruteforcer(config_path=self.temp_config.name)
        results = bruteforcer.bruteforce()
        
        # Should stop after finding "pass2"
        self.assertEqual(results['successful_attempts'], 1)
        self.assertLessEqual(results['total_attempts'], 2)
    
    @patch('ftp_bruteforce.FTP')
    def test_bruteforce_max_attempts(self, mock_ftp_class):
        """Test bruteforce respects max attempts limit"""
        from ftplib import error_perm
        
        # Mock FTP to always fail
        mock_ftp = MagicMock()
        mock_ftp.login.side_effect = error_perm("530 Login incorrect")
        mock_ftp_class.return_value = mock_ftp
        
        bruteforcer = FTPBruteforcer(config_path=self.temp_config.name)
        
        # Config has 3 passwords but max_attempts is 10
        # Since all fail, should try all 3
        results = bruteforcer.bruteforce()
        
        self.assertEqual(results['total_attempts'], 3)
        self.assertEqual(results['successful_attempts'], 0)
    
    def test_bruteforce_from_file(self):
        """Test bruteforce with password file"""
        # Create temporary password file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("password1\n")
            f.write("password2\n")
            f.write("password3\n")
            password_file = f.name
        
        try:
            with patch('ftp_bruteforce.FTP') as mock_ftp_class:
                from ftplib import error_perm
                
                mock_ftp = MagicMock()
                mock_ftp.login.side_effect = error_perm("530 Login incorrect")
                mock_ftp_class.return_value = mock_ftp
                
                bruteforcer = FTPBruteforcer(config_path=self.temp_config.name)
                results = bruteforcer.bruteforce_from_file('testuser', password_file)
                
                self.assertEqual(results['total_attempts'], 3)
        finally:
            os.unlink(password_file)
    
    def test_bruteforce_from_file_not_found(self):
        """Test bruteforce with non-existent password file"""
        bruteforcer = FTPBruteforcer(config_path=self.temp_config.name)
        
        with self.assertRaises(FileNotFoundError):
            bruteforcer.bruteforce_from_file('testuser', 'nonexistent.txt')


class TestFTPBruteforcerResults(unittest.TestCase):
    """Test result reporting and statistics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_config = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        )
        
        config_data = {
            "server": {
                "host": "test.example.com",
                "port": 21,
                "timeout": 5
            },
            "credentials": {
                "username": "admin",
                "password_list": ["test1", "test2"]
            },
            "bruteforce": {
                "max_attempts": 10,
                "delay_between_attempts": 0,
                "verbosity": 0,
                "stop_on_success": False
            }
        }
        
        json.dump(config_data, self.temp_config)
        self.temp_config.close()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    @patch('ftp_bruteforce.FTP')
    def test_results_structure(self, mock_ftp_class):
        """Test that results contain all expected fields"""
        from ftplib import error_perm
        
        mock_ftp = MagicMock()
        mock_ftp.login.side_effect = error_perm("530 Login incorrect")
        mock_ftp_class.return_value = mock_ftp
        
        bruteforcer = FTPBruteforcer(config_path=self.temp_config.name)
        results = bruteforcer.bruteforce()
        
        # Check all expected fields are present
        self.assertIn('total_attempts', results)
        self.assertIn('failed_attempts', results)
        self.assertIn('successful_attempts', results)
        self.assertIn('successful_credentials', results)
        self.assertIn('elapsed_time', results)
        self.assertIn('attempts_per_second', results)
        
        # Check types
        self.assertIsInstance(results['total_attempts'], int)
        self.assertIsInstance(results['failed_attempts'], int)
        self.assertIsInstance(results['successful_attempts'], int)
        self.assertIsInstance(results['successful_credentials'], list)
        self.assertIsInstance(results['elapsed_time'], float)


if __name__ == '__main__':
    unittest.main()

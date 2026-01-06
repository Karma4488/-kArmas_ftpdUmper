#!/usr/bin/env python3
"""
Basic tests for kArmas_ftpdUmper
"""

import sys
import os

# Add the current directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    """Test that all required imports are available."""
    try:
        from ftplib import FTP, error_perm, all_errors  # noqa: F401
        from tqdm import tqdm  # noqa: F401
        import os  # noqa: F401
        import sys  # noqa: F401
        import time  # noqa: F401
        import logging  # noqa: F401
        assert True
    except ImportError as e:
        assert False, f"Import failed: {e}"


def test_module_imports():
    """Test that the main module can be imported."""
    try:
        import kArmas_ftpdUmper
        assert hasattr(kArmas_ftpdUmper, 'main')
        assert hasattr(kArmas_ftpdUmper, 'download_file')
        assert hasattr(kArmas_ftpdUmper, 'crawl')
        assert hasattr(kArmas_ftpdUmper, 'scan_tree')
        assert hasattr(kArmas_ftpdUmper, 'ensure_dir')
        assert hasattr(kArmas_ftpdUmper, 'is_dir_fallback')
    except Exception as e:
        assert False, f"Module import failed: {e}"

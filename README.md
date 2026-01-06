# -kArmas_ftpdUmper
# 🐍 kArmas_ftpdUmper.py {'ALL-IN-ONE with GLOBAL BAR'}

#!/usr/bin/env python3
"""
kArmas_ftpdUmper
----------------
FTP Recursive Downloader
- Recursive crawl
- Global progress bar (all files)
- Per-file progress bar
- Resume support
- Retry logic
- Logging (file + console)
"""

from ftplib import FTP, error_perm, all_errors
from tqdm import tqdm
import os
import sys
import time
import logging

# ===================== CONFIG =====================
FTP_HOST = "ftp.example.com"
FTP_USER = "username"
FTP_PASS = "password"

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
# -------------------------------------------------

   
Here’s my tool kArmas_ftpdUmper updated with a GLOBAL progress bar that tracks total bytes across all files, while still keeping per-file bars.
✔ Pre-scans to calculate total size
✔ One global bar + one file bar at a time
✔ Resume-aware
✔ Logging + retry still intact

#!/usr/bin/env python3
"""
kArmas_ftpdUmper
----------------
FTP Recursive Downloader
- Recursive crawl
- Per-file progress bar
- Resume support
- Retry logic
- Logging to file + console

Author: kArmasec 🚀+🦝+🏴‍☠️=🎩

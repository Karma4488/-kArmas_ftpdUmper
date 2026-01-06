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
- Made In l0v3 bY kArmasec
- 4TheLulz 
- LulzURLife
- Prank
"""

from ftplib import FTP, error_perm, all_errors
from tqdm import tqdm
import os
import sys
import time
import logging

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


def main():
    log.info("Starting kArmas_ftpdUmper")

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
    log.info("kArmas_ftpdUmper completed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Interrupted by user")
        sys.exit(1)

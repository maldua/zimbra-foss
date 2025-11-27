#!/usr/bin/env python3
import os
import shutil
import subprocess

# Paths
SRC_DIR = os.path.abspath(os.path.dirname(__file__))
DEST_DIR = os.path.join(SRC_DIR, "docs")
DOWNLOADS_DIR = os.path.join(SRC_DIR, "downloads")

# Step 1: Copy all files/folders except downloads
if not os.path.exists(DEST_DIR):
    os.makedirs(DEST_DIR)

for item in os.listdir(SRC_DIR):
    s = os.path.join(SRC_DIR, item)
    d = os.path.join(DEST_DIR, item)
    if item == "downloads":
        continue
    if os.path.isdir(s):
        shutil.copytree(s, d, dirs_exist_ok=True)
    else:
        shutil.copy2(s, d)

# Step 2: Run generate-downloads-page.py in downloads dir
original_cwd = os.getcwd()
os.chdir(DOWNLOADS_DIR)

subprocess.run(["python3", "generate-downloads-page.py"], check=True, env=os.environ)

# Step 3: Change back to original directory
os.chdir(original_cwd)

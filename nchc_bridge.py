#!/usr/bin/env python3
"""
Antigravity NCHC Automation Bridge
This script runs a local daemon that maintains a persistent SSH connection to the NCHC cluster.
It solves the MFA/OTP obstacle by asking for your password and OTP once, keeping the connection alive,
and allowing Antigravity to sync files and submit Slurm jobs automatically.

Usage:
  python nchc_bridge.py start     - Start the daemon (interactive login)
  python nchc_bridge.py sync      - Sync local workspace to NCHC
  python nchc_bridge.py pull      - Pull remote files back to local
  python nchc_bridge.py run "<cmd>"- Run command on NCHC (e.g. sbatch, squeue)
  python nchc_bridge.py status    - Check daemon and Slurm job status
  python nchc_bridge.py stop      - Stop the daemon
"""

import os
import sys
import time
import json
import zipfile
import tempfile
import argparse
import getpass
import threading
from pathlib import Path

# Try to import dependencies; they are installed during setup
try:
    import paramiko
    from flask import Flask, request, jsonify
    import requests
except ImportError:
    print("[-] Missing dependencies. Run: pip install paramiko flask requests")
    sys.exit(1)

# Configuration
PORT = 9999
API_URL = f"http://127.0.0.1:{PORT}"
DEFAULT_HOST = "t3-c4.nchc.org.tw"
DEFAULT_USER = "kevinlin0411"
LOCAL_WORKSPACE = Path(__file__).parent.resolve()

app = Flask("NCHCBridge")

# Global SSH State
ssh_client = None
sftp_client = None
nchc_config = {
    "host": DEFAULT_HOST,
    "user": DEFAULT_USER,
    "remote_dir": f"/staging/biology/{DEFAULT_USER}/synbiopdactme"
}

def interactive_handler(title, instructions, prompt_list):
    """
    Handles keyboard-interactive authentication for SSH (Password & OTP)
    """
    responses = []
    for prompt, show in prompt_list:
        p_text = prompt.lower()
        if "login method" in p_text or "2fa login method" in p_text:
            responses.append("1")  # Auto-respond 1 for Mobile APP OTP
        elif "password" in p_text:
            responses.append(nchc_config["password"])
        elif "otp" in p_text or "verification" in p_text or "code" in p_text or "passcode" in p_text:
            # If OTP was pre-supplied, use it. Otherwise, prompt the user.
            if nchc_config.get("otp"):
                responses.append(nchc_config["otp"])
            else:
                otp = input(f"[MFA OTP] {prompt.strip()} ")
                responses.append(otp)
        else:
            resp = input(f"{prompt.strip()} ")
            responses.append(resp)
    return responses

def connect_ssh():
    global ssh_client, sftp_client
    print(f"[*] Connecting to {nchc_config['user']}@{nchc_config['host']}...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # We need an active transport to handle interactive auth
        transport = paramiko.Transport((nchc_config["host"], 22))
        transport.start_client()
        transport.set_keepalive(30)
        
        # Authenticate interactively
        transport.auth_interactive(nchc_config["user"], interactive_handler)
        
        if not transport.is_authenticated():
            raise Exception("Authentication failed. Please check your credentials and OTP.")
            
        ssh_client = ssh
        ssh._transport = transport
        sftp_client = ssh.open_sftp()
        print("[+] SSH & SFTP Connection established successfully!")
        
        # Ensure remote directory exists
        run_remote_cmd(f"mkdir -p {nchc_config['remote_dir']}")
        return True
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return False

def run_remote_cmd(cmd):
    """Executes a command on the remote NCHC host and returns (stdout, stderr, exit_code)"""
    global ssh_client
    if not ssh_client or not ssh_client.get_transport().is_active():
        return "", "SSH connection lost or not established.", -1
    
    # We execute relative to the project directory, ensuring it exists first
    full_cmd = f"mkdir -p {nchc_config['remote_dir']} && cd {nchc_config['remote_dir']} && {cmd}"
    try:
        stdin, stdout, stderr = ssh_client.exec_command(full_cmd)
        exit_code = stdout.channel.recv_exit_status()
        out_str = stdout.read().decode("utf-8", errors="ignore")
        err_str = stderr.read().decode("utf-8", errors="ignore")
        return out_str, err_str, exit_code
    except Exception as e:
        return "", f"Execution error: {e}", -1

# Flask API Endpoints
@app.route("/status", methods=["GET"])
def api_status():
    is_active = ssh_client is not None and ssh_client.get_transport().is_active()
    return jsonify({
        "status": "online" if is_active else "offline",
        "host": nchc_config["host"],
        "user": nchc_config["user"],
        "remote_dir": nchc_config["remote_dir"]
    })

@app.route("/config", methods=["POST"])
def api_config():
    data = request.json or {}
    remote_dir = data.get("remote_dir")
    if remote_dir:
        nchc_config["remote_dir"] = remote_dir
        run_remote_cmd(f"mkdir -p {remote_dir}")
        return jsonify({"success": True, "message": f"Remote directory updated to: {remote_dir}"})
    return jsonify({"error": "No remote_dir provided"}), 400

@app.route("/run", methods=["POST"])
def api_run():
    data = request.json or {}
    cmd = data.get("command")
    if not cmd:
        return jsonify({"error": "No command provided"}), 400
    
    stdout, stderr, exit_code = run_remote_cmd(cmd)
    return jsonify({
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code
    })

@app.route("/sync", methods=["POST"])
def api_sync():
    """Uploads the local workspace to the remote project folder using SFTP"""
    global sftp_client
    if not sftp_client:
        return jsonify({"error": "SFTP not connected"}), 500
    
    try:
        # Create a zip of local workspace to upload efficiently
        temp_zip = LOCAL_WORKSPACE / "temp_workspace.zip"
        
        # Avoid zipping the temp zip itself or credential caches
        ignore_files = [
            "temp_workspace.zip", 
            "nchc_bridge.py", 
            "__pycache__", 
            ".git", 
            ".gemini"
        ]
        
        print(f"[*] Packaging local files in {LOCAL_WORKSPACE}...")
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(LOCAL_WORKSPACE):
                # Filter ignore lists
                dirs[:] = [d for d in dirs if d not in ignore_files]
                for file in files:
                    if file in ignore_files or file.endswith(".log") or file.endswith(".tmp"):
                        continue
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(LOCAL_WORKSPACE)
                    zipf.write(file_path, rel_path)
        
        # Upload the zip
        remote_zip = f"{nchc_config['remote_dir']}/workspace.zip"
        print(f"[*] Uploading to {remote_zip}...")
        sftp_client.put(str(temp_zip), remote_zip)
        
        # Unzip on remote
        print("[*] Extracting files on NCHC...")
        stdout, stderr, code = run_remote_cmd(f"unzip -o workspace.zip && rm workspace.zip")
        
        # Clean up local zip
        if temp_zip.exists():
            temp_zip.unlink()
            
        if code != 0:
            return jsonify({"error": f"Failed to unzip remote: {stderr}"}), 500
            
        return jsonify({"success": True, "message": "Workspace synchronized successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/pull", methods=["POST"])
def api_pull():
    """Downloads remote workspace updates back to local"""
    global sftp_client, ssh_client
    if not sftp_client:
        return jsonify({"error": "SFTP not connected"}), 500
    
    try:
        # Package on remote, excluding large datasets, cache, outputs, logs and snakemake to avoid disk and speed issues
        print("[*] Archiving project on NCHC (excluding large directories)...")
        exclude_args = "-x 'workspace.zip' -x 'remote_workspace.zip' -x 'raw-dataset/*' -x 'processed-data/*' -x 'cache/*' -x 'tmp/*' -x 'outputs/*' -x 'logs/*' -x '.snakemake/*'"
        stdout, stderr, code = run_remote_cmd(f"zip -r remote_workspace.zip . {exclude_args}")
        if code != 0:
            return jsonify({"error": f"Failed to archive remote: {stderr}"}), 500
            
        # Download zip
        remote_zip = f"{nchc_config['remote_dir']}/remote_workspace.zip"
        local_zip = LOCAL_WORKSPACE / "temp_remote.zip"
        print(f"[*] Downloading {remote_zip} to local...")
        sftp_client.get(remote_zip, str(local_zip))
        
        # Delete remote zip
        run_remote_cmd("rm remote_workspace.zip")
        
        # Extract local
        print("[*] Extracting remote files locally...")
        with zipfile.ZipFile(local_zip, 'r') as zipf:
            zipf.extractall(LOCAL_WORKSPACE)
            
        # Clean up local zip
        if local_zip.exists():
            local_zip.unlink()
            
        return jsonify({"success": True, "message": "Remote updates pulled successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stop", methods=["POST"])
def api_stop():
    def shutdown():
        time.sleep(1)
        os._exit(0)
    threading.Thread(target=shutdown).start()
    return jsonify({"success": True, "message": "Daemon shutting down..."})


# CLI Controller Methods
def cmd_start(args):
    global nchc_config
    print("=== Antigravity NCHC Bridge Setup ===")
    
    # Prompt for details
    host = input(f"NCHC Hostname [{DEFAULT_HOST}]: ").strip() or DEFAULT_HOST
    user = input(f"NCHC Username [{DEFAULT_USER}]: ").strip() or DEFAULT_USER
    remote_dir = input(f"Remote Project Folder [/staging/biology/{user}/synbiopdactme]: ").strip() or f"/staging/biology/{user}/synbiopdactme"
    
    password = getpass.getpass("NCHC Password: ")
    otp = input("NCHC Verification Code (OTP): ").strip()
    
    nchc_config.update({
        "host": host,
        "user": user,
        "password": password,
        "otp": otp,
        "remote_dir": remote_dir
    })
    
    if connect_ssh():
        # Hide sensitive credentials from memory config after successful login
        nchc_config["password"] = password
        nchc_config["otp"] = ""
        
        print(f"\n[+] Starting Local Bridge Daemon on http://127.0.0.1:{PORT}...")
        print("[!] KEEP THIS WINDOW OPEN to maintain the automated connection.")
        print("[!] Antigravity can now run code syncs and Slurm jobs automatically!\n")
        
        # Run Flask
        app.run(port=PORT, debug=False, use_reloader=False)
    else:
        print("[-] Initialization failed. Please verify credentials/OTP.")

def cmd_sync():
    try:
        r = requests.post(f"{API_URL}/sync")
        res = r.json()
        if r.status_code == 200:
            print(f"[+] {res['message']}")
        else:
            print(f"[-] Sync failed: {res.get('error')}")
    except requests.exceptions.ConnectionError:
        print("[-] Bridge daemon is not running. Start it first: python nchc_bridge.py start")

def cmd_pull():
    try:
        r = requests.post(f"{API_URL}/pull")
        res = r.json()
        if r.status_code == 200:
            print(f"[+] {res['message']}")
        else:
            print(f"[-] Pull failed: {res.get('error')}")
    except requests.exceptions.ConnectionError:
        print("[-] Bridge daemon is not running. Start it first: python nchc_bridge.py start")

def cmd_run(remote_cmd):
    try:
        r = requests.post(f"{API_URL}/run", json={"command": remote_cmd})
        res = r.json()
        if r.status_code == 200:
            print(f"--- Standard Output (Exit Code: {res['exit_code']}) ---")
            print(res["stdout"])
            if res["stderr"].strip():
                print("--- Standard Error ---", file=sys.stderr)
                print(res["stderr"], file=sys.stderr)
        else:
            print(f"[-] Command failed: {res.get('error')}")
    except requests.exceptions.ConnectionError:
        print("[-] Bridge daemon is not running. Start it first: python nchc_bridge.py start")

def cmd_status():
    try:
        r = requests.get(f"{API_URL}/status")
        res = r.json()
        print("=== Bridge Daemon Status ===")
        print(f"Daemon:      ONLINE")
        print(f"NCHC Host:   {res['host']}")
        print(f"NCHC User:   {res['user']}")
        print(f"Remote Dir:  {res['remote_dir']}")
        print("============================")
        
        # Check active jobs on NCHC
        print("\n--- Running Jobs on NCHC ---")
        cmd_run("squeue -u " + res['user'])
    except requests.exceptions.ConnectionError:
        print("=== Bridge Daemon Status ===")
        print("Daemon:      OFFLINE")
        print("Hint:        To activate, run: python nchc_bridge.py start")
        print("============================")

def cmd_stop():
    try:
        r = requests.post(f"{API_URL}/stop")
        res = r.json()
        print(f"[+] {res['message']}")
    except requests.exceptions.ConnectionError:
        print("[-] Daemon is already stopped or offline.")

if __name__ == "__main__":
    # Reconfigure stdout/stderr to UTF-8 to prevent CP950 encoding errors on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(description="Antigravity NCHC Automation Bridge")
    parser.add_argument("command", choices=["start", "sync", "pull", "run", "status", "stop"], 
                        help="Action to perform")
    parser.add_argument("cmd_args", nargs="*", help="Arguments for 'run' command")
    
    args = parser.parse_args()
    
    if args.command == "start":
        cmd_start(args)
    elif args.command == "sync":
        cmd_sync()
    elif args.command == "pull":
        cmd_pull()
    elif args.command == "run":
        if not args.cmd_args:
            print("[-] Error: 'run' requires a command argument. e.g. python nchc_bridge.py run \"sbatch submit.sh\"")
            sys.exit(1)
        cmd_run(" ".join(args.cmd_args))
    elif args.command == "status":
        cmd_status()
    elif args.command == "stop":
        cmd_stop()

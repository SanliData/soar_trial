"""
SAFE RUN: safe_run
PURPOSE: Windows-safe uvicorn launcher with port conflict handling
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import sys
import socket
import subprocess
import time
from typing import Optional, Tuple, List

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None


def is_port_available(host: str, port: int) -> bool:
    """
    Check if a port is available for binding.
    
    Args:
        host: Host address (e.g., '0.0.0.0' or '127.0.0.1')
        port: Port number
        
    Returns:
        True if port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def get_port_processes(port: int) -> List[Tuple[int, str]]:
    """
    Get all process IDs and commands for processes holding a port.
    
    Uses psutil if available, falls back to platform-specific methods.
    
    Args:
        port: Port number
        
    Returns:
        List of tuples (pid, command) for processes using the port
    """
    processes = []
    seen_pids = set()
    
    if PSUTIL_AVAILABLE:
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN' and conn.laddr.port == port:
                    if conn.pid in seen_pids:
                        continue
                    seen_pids.add(conn.pid)
                    try:
                        proc = psutil.Process(conn.pid)
                        cmd = ' '.join(proc.cmdline()[:2]) if proc.cmdline() else proc.name()
                        processes.append((conn.pid, cmd))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        processes.append((conn.pid, f"PID {conn.pid}"))
        except (psutil.AccessDenied, Exception):
            pass
    
    ***REMOVED*** Fallback if psutil didn't find anything or not available
    if not processes:
        if sys.platform == "win32":
            processes = _get_port_processes_windows(port)
        else:
            proc_info = _get_port_process_info_linux(port)
            if proc_info:
                processes.append(proc_info)
    
    return processes


def _get_port_processes_windows(port: int) -> List[Tuple[int, str]]:
    """
    Windows fallback using netstat and tasklist.
    Returns all processes using the port.
    """
    processes = []
    seen_pids = set()
    
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return []
        
        port_str = f":{port}"
        for line in result.stdout.splitlines():
            if "LISTENING" in line and port_str in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    try:
                        pid_int = int(pid)
                        ***REMOVED*** Avoid duplicates
                        if pid_int in seen_pids:
                            continue
                        seen_pids.add(pid_int)
                        
                        tasklist_result = subprocess.run(
                            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/V"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if tasklist_result.returncode == 0:
                            lines = tasklist_result.stdout.splitlines()
                            if len(lines) > 1:
                                cmd = lines[1].split(',')[0].strip('"')
                                processes.append((pid_int, cmd))
                            else:
                                processes.append((pid_int, f"PID {pid}"))
                        else:
                            processes.append((pid_int, f"PID {pid}"))
                    except (ValueError, IndexError):
                        pass
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    return processes


def _get_port_process_info_linux(port: int) -> Optional[Tuple[int, str]]:
    """
    Linux fallback using lsof or ss.
    """
    try:
        ***REMOVED*** Try lsof first
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}", "-sTCP:LISTEN"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                pid = int(result.stdout.strip().split()[0])
                cmd_result = subprocess.run(
                    ["ps", "-p", str(pid), "-o", "comm="],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if cmd_result.returncode == 0:
                    cmd = cmd_result.stdout.strip() or f"PID {pid}"
                else:
                    cmd = f"PID {pid}"
                return (pid, cmd)
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            pass
    except Exception:
        pass
    
    return None


def kill_process(pid: int) -> bool:
    """
    Kill a process by PID.
    
    Args:
        pid: Process ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        else:
            import signal
            os.kill(pid, signal.SIGTERM)
            return True
    except Exception:
        return False


def main():
    """
    Main entry point for safe_run.
    """
    ***REMOVED*** Read configuration from environment (safe parsing to avoid empty-string crash)
    from src.config.settings import get_int_env
    port = get_int_env("PORT", get_int_env("FINDEROS_PORT", 8000))
    host = os.getenv("FINDEROS_HOST") or "127.0.0.1"
    
    print(f"Checking port {port}...")
    
    ***REMOVED*** Check if port is available on both host and 0.0.0.0 (Windows can have both bound)
    ***REMOVED*** A process on 0.0.0.0:port blocks binding to 127.0.0.1:port
    port_in_use = False
    if not is_port_available(host, port):
        port_in_use = True
    elif host != "0.0.0.0" and not is_port_available("0.0.0.0", port):
        ***REMOVED*** Also check 0.0.0.0 if we're binding to a specific interface
        port_in_use = True
    
    if port_in_use:
        processes = get_port_processes(port)
        
        if processes:
            print(f"Port {port} is in use by {len(processes)} process(es):")
            for pid, cmd in processes:
                print(f"  PID {pid}: {cmd}")
            
            ***REMOVED*** Automatically kill all processes (non-interactive for script usage)
            print(f"\nKilling {len(processes)} process(es)...")
            all_killed = True
            
            for pid, cmd in processes:
                print(f"  Killing PID {pid}...")
                if kill_process(pid):
                    print(f"    Process {pid} terminated successfully")
                else:
                    print(f"    ERROR: Failed to kill process {pid}")
                    all_killed = False
            
            if not all_killed:
                print(f"\nERROR: Failed to kill some processes")
                sys.exit(1)
            
            ***REMOVED*** Wait for port to be released (Windows can take a moment)
            max_wait = 5
            waited = 0
            while waited < max_wait:
                time.sleep(0.5)
                waited += 0.5
                if is_port_available(host, port):
                    break
            
            ***REMOVED*** Verify port is now available
            if not is_port_available(host, port):
                print(f"\nERROR: Port {port} is still in use after killing processes")
                print(f"To check manually:")
                if sys.platform == "win32":
                    print(f"  netstat -ano | findstr :{port}")
                else:
                    print(f"  lsof -i :{port}")
                sys.exit(1)
            
            print(f"Port {port} is free")
        else:
            print(f"\nERROR: Port {port} is in use, but cannot determine which process")
            print(f"To check manually:")
            if sys.platform == "win32":
                print(f"  netstat -ano | findstr :{port}")
            else:
                print(f"  lsof -i :{port}")
            sys.exit(1)
    else:
        print(f"Port {port} is free")
    
    ***REMOVED*** Port is available, start uvicorn
    print(f"\nStarting uvicorn...")
    
    ***REMOVED*** Determine reload mode
    reload = os.getenv("FINDEROS_RELOAD", "false").lower() == "true"
    if os.getenv("ENV") == "production":
        reload = False
    if sys.platform == "win32" and not os.getenv("FINDEROS_RELOAD"):
        reload = False
    
    ***REMOVED*** Build uvicorn command
    cmd = [
        sys.executable,
        "-m", "uvicorn",
        "src.app:app",
        "--host", host,
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
        cmd.extend(["--reload-dir", "src"])  ***REMOVED*** Only watch src directory (excludes .venv)
    
    ***REMOVED*** Start uvicorn (use subprocess.Popen to maintain process chain)
    try:
        ***REMOVED*** Use Popen with wait to keep process alive and handle signals properly
        ***REMOVED*** Don't redirect stdout/stderr so uvicorn logs appear in console
        process = subprocess.Popen(cmd)
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        sys.exit(process.returncode)
    except Exception as e:
        print(f"ERROR: Failed to start uvicorn: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

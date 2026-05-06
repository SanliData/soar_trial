"""
PORT CHECK: port_check
PURPOSE: Windows-safe port availability checking and process detection
ENCODING: UTF-8 WITHOUT BOM
"""

import socket
import sys
import os
from typing import Optional, Tuple


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


def get_port_process_info(port: int) -> Optional[Tuple[int, str]]:
    """
    Get process ID and command line for process holding a port.
    
    Platform-specific implementation:
    - Windows: Uses netstat and tasklist
    - Linux: Uses lsof or ss (if available)
    
    Args:
        port: Port number
        
    Returns:
        Tuple of (pid, command) if found, None otherwise
    """
    if sys.platform == "win32":
        return _get_port_process_info_windows(port)
    else:
        return _get_port_process_info_linux(port)


def _get_port_process_info_windows(port: int) -> Optional[Tuple[int, str]]:
    """
    Windows implementation using netstat and tasklist.
    """
    
    try:
        import subprocess
        ***REMOVED*** Use netstat to find process using port
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return None
        
        ***REMOVED*** Find line with LISTENING on our port
        port_str = f":{port}"
        for line in result.stdout.splitlines():
            if "LISTENING" in line and port_str in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    try:
                        pid_int = int(pid)
                        ***REMOVED*** Get process command line
                        tasklist_result = subprocess.run(
                            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/V"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if tasklist_result.returncode == 0:
                            lines = tasklist_result.stdout.splitlines()
                            if len(lines) > 1:
                                ***REMOVED*** CSV format: parse second line
                                cmd = lines[1].split(',')[0].strip('"')
                                return (pid_int, cmd)
                        return (pid_int, f"PID {pid}")
                    except (ValueError, IndexError):
                        pass
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    return None


def _get_port_process_info_linux(port: int) -> Optional[Tuple[int, str]]:
    """
    Linux implementation using lsof or ss.
    """
    try:
        import subprocess
        
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
                ***REMOVED*** Get command name
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
        
        ***REMOVED*** Fallback to ss
        try:
            result = subprocess.run(
                ["ss", "-tulpn"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if f":{port}" in line and "LISTEN" in line:
                        ***REMOVED*** Parse PID from ss output (format: pid=12345)
                        import re
                        match = re.search(r'pid=(\d+)', line)
                        if match:
                            pid = int(match.group(1))
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
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError, AttributeError):
            pass
            
    except Exception:
        pass
    
    return None


def check_port_and_exit(host: str, port: int) -> None:
    """
    Check if port is available, exit with clear error if not.
    
    On Linux/Docker, this is a simple availability check.
    On Windows, it also attempts to identify the process holding the port.
    
    Args:
        host: Host address
        port: Port number
        
    Raises:
        SystemExit with clear error message if port is in use
    """
    if not is_port_available(host, port):
        proc_info = get_port_process_info(port)
        
        if proc_info:
            pid, cmd = proc_info
            if sys.platform == "win32":
                error_msg = (
                    f"\nERROR: Port {port} is already in use.\n"
                    f"Process ID: {pid}\n"
                    f"Command: {cmd}\n"
                    f"\nTo free the port, run:\n"
                    f"  python -m src.core.port_check --kill {port}\n"
                    f"Or manually: taskkill /PID {pid} /F\n"
                )
            else:
                error_msg = (
                    f"\nERROR: Port {port} is already in use.\n"
                    f"Process ID: {pid}\n"
                    f"Command: {cmd}\n"
                    f"\nTo free the port, kill the process:\n"
                    f"  kill {pid}\n"
                )
        else:
            if sys.platform == "win32":
                error_msg = (
                    f"\nERROR: Port {port} is already in use.\n"
                    f"Cannot determine which process is holding it.\n"
                    f"\nTo check manually:\n"
                    f"  netstat -ano | findstr :{port}\n"
                    f"  python -m src.core.port_check --check {port}\n"
                )
            else:
                error_msg = (
                    f"\nERROR: Port {port} is already in use.\n"
                    f"Cannot determine which process is holding it.\n"
                    f"\nTo check manually:\n"
                    f"  lsof -i :{port}  ***REMOVED*** or: ss -tulpn | grep :{port}\n"
                )
        
        print(error_msg, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    ***REMOVED*** CLI tool for port checking and cleanup
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m src.core.port_check --check <port>")
        print("  python -m src.core.port_check --kill <port>")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if len(sys.argv) < 3:
        print("Error: Port number required", file=sys.stderr)
        sys.exit(1)
    
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("Error: Invalid port number", file=sys.stderr)
        sys.exit(1)
    
    if action == "--check":
        proc_info = get_port_process_info(port)
        if proc_info:
            pid, cmd = proc_info
            print(f"Port {port} is in use:")
            print(f"  PID: {pid}")
            print(f"  Command: {cmd}")
        else:
            available = is_port_available("127.0.0.1", port)
            if available:
                print(f"Port {port} is available")
            else:
                print(f"Port {port} is in use (cannot determine process)")
    
    elif action == "--kill":
        if sys.platform != "win32":
            print("Error: --kill is only supported on Windows", file=sys.stderr)
            sys.exit(1)
        
        proc_info = get_port_process_info(port)
        if not proc_info:
            print(f"Error: Cannot find process using port {port}", file=sys.stderr)
            sys.exit(1)
        
        pid, cmd = proc_info
        print(f"Found process using port {port}:")
        print(f"  PID: {pid}")
        print(f"  Command: {cmd}")
        
        response = input(f"\nKill process {pid}? (y/N): ").strip().lower()
        if response == "y":
            import subprocess
            try:
                result = subprocess.run(
                    ["taskkill", "/PID", str(pid), "/F"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print(f"Process {pid} killed successfully")
                else:
                    print(f"Error killing process: {result.stderr}", file=sys.stderr)
                    sys.exit(1)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("Cancelled")
    else:
        print(f"Error: Unknown action '{action}'", file=sys.stderr)
        sys.exit(1)

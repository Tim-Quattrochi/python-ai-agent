"""System monitoring and DevOps automation tools."""

import logging
import psutil
import subprocess
import os
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import requests

from .base import Tool

logger = logging.getLogger(__name__)


class SystemMonitorTool(Tool):
    """Tool for system monitoring and DevOps operations."""

    name = "system_monitor"
    description = "Monitor system resources, processes, and perform DevOps operations"

    def __init__(self):
        """Initialize system monitoring tool."""
        super().__init__(
            name="system_monitor",
            description="Monitor system resources, processes, and perform DevOps operations"
        )

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for system monitor parameters."""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["system_stats", "process_info", "disk_usage", "network_stats", "service_status", "docker_stats", "run_command", "log_analysis", "port_check"],
                    "description": "The system monitoring operation to perform"
                },
                "process_name": {
                    "type": "string",
                    "description": "Name of process to get information for"
                },
                "pid": {
                    "type": "integer",
                    "description": "Process ID to get information for"
                },
                "path": {
                    "type": "string",
                    "default": "/",
                    "description": "Path to check disk usage for"
                },
                "service_name": {
                    "type": "string",
                    "description": "Name of service to check status"
                },
                "command": {
                    "type": "string",
                    "description": "Shell command to execute"
                },
                "timeout": {
                    "type": "integer",
                    "default": 30,
                    "description": "Command timeout in seconds"
                },
                "log_path": {
                    "type": "string",
                    "description": "Path to log file for analysis"
                },
                "lines": {
                    "type": "integer",
                    "default": 100,
                    "description": "Number of log lines to analyze"
                },
                "host": {
                    "type": "string",
                    "default": "localhost",
                    "description": "Host to check port on"
                },
                "port": {
                    "type": "integer",
                    "description": "Port number to check"
                }
            },
            "required": ["action"],
            "additionalProperties": False
        }

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute system monitoring operations."""
        try:
            if action == "system_stats":
                return self._get_system_stats()
            elif action == "process_info":
                return self._get_process_info(
                    process_name=kwargs.get('process_name'),
                    pid=kwargs.get('pid')
                )
            elif action == "disk_usage":
                return self._get_disk_usage(path=kwargs.get('path', '/'))
            elif action == "network_stats":
                return self._get_network_stats()
            elif action == "service_status":
                return self._check_service_status(service_name=kwargs.get('service_name'))
            elif action == "docker_stats":
                return self._get_docker_stats()
            elif action == "run_command":
                return self._run_command(
                    command=kwargs.get('command'),
                    timeout=kwargs.get('timeout', 30)
                )
            elif action == "log_analysis":
                return self._analyze_logs(
                    log_path=kwargs.get('log_path'),
                    lines=kwargs.get('lines', 100)
                )
            elif action == "port_check":
                return self._check_port(
                    host=kwargs.get('host', 'localhost'),
                    port=kwargs.get('port')
                )
            else:
                return {"error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"Error in system monitor tool: {str(e)}")
            return {"error": f"System monitor error: {str(e)}"}

    def _get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk information
            disk = psutil.disk_usage('/')

            # Network information
            network = psutil.net_io_counters()

            # Boot time
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time

            # Load average (Unix-like systems)
            load_avg = os.getloadavg() if hasattr(
                os, 'getloadavg') else [0, 0, 0]

            stats = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": cpu_count,
                    "frequency_mhz": cpu_freq.current if cpu_freq else None
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "usage_percent": memory.percent
                },
                "swap": {
                    "total_gb": round(swap.total / (1024**3), 2),
                    "used_gb": round(swap.used / (1024**3), 2),
                    "usage_percent": swap.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 2)
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "system": {
                    "boot_time": boot_time.isoformat(),
                    "uptime_hours": round(uptime.total_seconds() / 3600, 2),
                    "load_average": load_avg
                }
            }

            return {
                "success": True,
                "message": f"📊 System statistics collected",
                "stats": stats
            }

        except Exception as e:
            return {"error": f"Failed to get system stats: {str(e)}"}

    def _get_process_info(self, process_name: str = None, pid: int = None) -> Dict[str, Any]:
        """Get information about running processes."""
        try:
            processes = []

            if pid:
                # Get specific process by PID
                try:
                    proc = psutil.Process(pid)
                    processes.append(self._format_process_info(proc))
                except psutil.NoSuchProcess:
                    return {"error": f"Process with PID {pid} not found"}
            elif process_name:
                # Get processes by name
                for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                    if process_name.lower() in proc.info['name'].lower():
                        processes.append(self._format_process_info(proc))
            else:
                # Get top 10 processes by memory usage
                procs = sorted(psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']),
                               key=lambda p: p.info['memory_info'].rss, reverse=True)[:10]
                for proc in procs:
                    processes.append(self._format_process_info(proc))

            return {
                "success": True,
                "message": f"🔍 Found {len(processes)} processes",
                "processes": processes
            }

        except Exception as e:
            return {"error": f"Failed to get process info: {str(e)}"}

    def _format_process_info(self, proc) -> Dict[str, Any]:
        """Format process information."""
        try:
            with proc.oneshot():
                return {
                    "pid": proc.pid,
                    "name": proc.name(),
                    "status": proc.status(),
                    "memory_mb": round(proc.memory_info().rss / (1024*1024), 2),
                    "cpu_percent": proc.cpu_percent(),
                    "create_time": datetime.fromtimestamp(proc.create_time()).isoformat(),
                    "cmdline": " ".join(proc.cmdline()) if proc.cmdline() else ""
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {"pid": proc.pid, "error": "Access denied or process not found"}

    def _get_disk_usage(self, path: str = '/') -> Dict[str, Any]:
        """Get disk usage information."""
        try:
            usage = psutil.disk_usage(path)

            return {
                "success": True,
                "message": f"💽 Disk usage for {path}",
                "path": path,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "usage_percent": round((usage.used / usage.total) * 100, 2)
            }

        except Exception as e:
            return {"error": f"Failed to get disk usage: {str(e)}"}

    def _get_network_stats(self) -> Dict[str, Any]:
        """Get network interface statistics."""
        try:
            interfaces = psutil.net_if_stats()
            addresses = psutil.net_if_addrs()
            io_counters = psutil.net_io_counters(pernic=True)

            network_info = {}
            for interface, stats in interfaces.items():
                interface_info = {
                    "is_up": stats.isup,
                    "speed_mbps": stats.speed,
                    "mtu": stats.mtu
                }

                # Add IP addresses
                if interface in addresses:
                    addrs = []
                    for addr in addresses[interface]:
                        addrs.append({
                            "family": str(addr.family),
                            "address": addr.address,
                            "netmask": addr.netmask
                        })
                    interface_info["addresses"] = addrs

                # Add I/O counters
                if interface in io_counters:
                    io = io_counters[interface]
                    interface_info["io"] = {
                        "bytes_sent": io.bytes_sent,
                        "bytes_recv": io.bytes_recv,
                        "packets_sent": io.packets_sent,
                        "packets_recv": io.packets_recv
                    }

                network_info[interface] = interface_info

            return {
                "success": True,
                "message": f"🌐 Network statistics for {len(network_info)} interfaces",
                "interfaces": network_info
            }

        except Exception as e:
            return {"error": f"Failed to get network stats: {str(e)}"}

    def _check_service_status(self, service_name: str) -> Dict[str, Any]:
        """Check the status of a system service."""
        try:
            # Use systemctl on Linux systems
            result = subprocess.run(
                ['systemctl', 'is-active', service_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            status = result.stdout.strip()
            is_active = result.returncode == 0

            # Get more detailed info
            info_result = subprocess.run(
                ['systemctl', 'status', service_name, '--no-pager'],
                capture_output=True,
                text=True,
                timeout=10
            )

            return {
                "success": True,
                "message": f"🔧 Service status for {service_name}",
                "service_name": service_name,
                "status": status,
                "is_active": is_active,
                "detailed_status": info_result.stdout
            }

        except subprocess.TimeoutExpired:
            return {"error": "Service check timed out"}
        except FileNotFoundError:
            return {"error": "systemctl not found (not a systemd system?)"}
        except Exception as e:
            return {"error": f"Failed to check service: {str(e)}"}

    def _get_docker_stats(self) -> Dict[str, Any]:
        """Get Docker container statistics."""
        try:
            # Get running containers
            result = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format',
                    'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}'],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode != 0:
                return {"error": "Docker not available or no permissions"}

            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            containers = []

            for line in lines:
                parts = line.split('\t')
                if len(parts) >= 6:
                    containers.append({
                        "container": parts[0],
                        "cpu_percent": parts[1],
                        "memory_usage": parts[2],
                        "memory_percent": parts[3],
                        "network_io": parts[4],
                        "block_io": parts[5]
                    })

            return {
                "success": True,
                "message": f"🐳 Docker stats for {len(containers)} containers",
                "containers": containers
            }

        except subprocess.TimeoutExpired:
            return {"error": "Docker stats command timed out"}
        except FileNotFoundError:
            return {"error": "Docker command not found"}
        except Exception as e:
            return {"error": f"Failed to get Docker stats: {str(e)}"}

    def _run_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Run a shell command safely."""
        try:
            # Security: only allow certain safe commands
            safe_commands = ['ls', 'pwd', 'date',
                             'whoami', 'uptime', 'df', 'free', 'ps']
            cmd_parts = command.split()
            if not cmd_parts or cmd_parts[0] not in safe_commands:
                return {"error": f"Command '{cmd_parts[0] if cmd_parts else command}' not allowed"}

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": True,
                "message": f"⚡ Command executed: {command}",
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": f"Failed to run command: {str(e)}"}

    def _analyze_logs(self, log_path: str, lines: int = 100) -> Dict[str, Any]:
        """Analyze log files for patterns and errors."""
        try:
            if not os.path.exists(log_path):
                return {"error": f"Log file not found: {log_path}"}

            # Read last N lines
            result = subprocess.run(
                ['tail', '-n', str(lines), log_path],
                capture_output=True,
                text=True,
                timeout=10
            )

            log_lines = result.stdout.split('\n')

            # Simple analysis
            error_count = sum(
                1 for line in log_lines if 'ERROR' in line.upper())
            warning_count = sum(
                1 for line in log_lines if 'WARNING' in line.upper() or 'WARN' in line.upper())

            # Extract recent errors
            recent_errors = [line for line in log_lines[-20:]
                             if 'ERROR' in line.upper()]

            return {
                "success": True,
                "message": f"📋 Log analysis for {log_path}",
                "log_path": log_path,
                "lines_analyzed": len(log_lines),
                "error_count": error_count,
                "warning_count": warning_count,
                "recent_errors": recent_errors[:5],  # Last 5 errors
                "file_size_mb": round(os.path.getsize(log_path) / (1024*1024), 2)
            }

        except Exception as e:
            return {"error": f"Failed to analyze logs: {str(e)}"}

    def _check_port(self, host: str, port: int) -> Dict[str, Any]:
        """Check if a port is open on a host."""
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)

            result = sock.connect_ex((host, port))
            sock.close()

            is_open = result == 0

            return {
                "success": True,
                "message": f"🔌 Port check for {host}:{port}",
                "host": host,
                "port": port,
                "is_open": is_open,
                "status": "Open" if is_open else "Closed/Filtered"
            }

        except Exception as e:
            return {"error": f"Failed to check port: {str(e)}"}

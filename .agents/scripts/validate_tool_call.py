# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Command validation utility to block destructive/unauthorized run_command executions."""

import re
import sys


# Define SecurityError exception class
class SecurityError(Exception):
    """Exception raised when a command violates validation security rules."""

    pass


# Define matching rules based on validate_tool_call.spec.md
SECURITY_RULES = [
    {
        "id": "SEC01_ROOT_DELETION",
        "regex": r"rm\s+-[a-zA-Z]*r[a-zA-Z]*f\s+/\s*($|\s)",
        "message": "Destructive command blocked: root directory deletion.",
    },
    {
        "id": "SEC02_SYS_DELETION",
        "regex": r"rm\s+-[a-zA-Z]*r[a-zA-Z]*f\s+/(etc|usr|var|home|boot|dev|sys|proc)\b",
        "message": "Destructive command blocked: critical system directory deletion.",
    },
    {
        "id": "SEC03_DISK_FORMAT",
        "regex": r"\b(mkfs|fdisk|parted|gparted)\b",
        "message": "Unauthorized command blocked: disk formatting / partitioning.",
    },
    {
        "id": "SEC04_RAW_DISK_WRITE",
        "regex": r"(>|dd\s+.*of=)/dev/(sd[a-z]|nvme[0-9]+n[0-9]+|xvd[a-z])",
        "message": "Unauthorized command blocked: writing directly to raw disk.",
    },
    {
        "id": "SEC05_CONFIG_TAMPER",
        "regex": r"\b(etc/passwd|etc/shadow|etc/sudoers)\b",
        "message": "Unauthorized command blocked: altering system configuration files.",
    },
    {
        "id": "SEC06_NET_DISRUPT",
        "regex": r"\b(iptables|ufw|nftables|ip\s+route)\b",
        "message": "Unauthorized command blocked: altering network routing or firewall.",
    },
    {
        "id": "SEC07_PROC_KILL",
        "regex": r"\b(kill\s+-[0-9]+\s+1|kill\s+-9\s+1|killall\s+systemd|killall\s+init)\b",
        "message": "Unauthorized command blocked: terminating system-critical processes.",
    },
    {
        "id": "SEC08_KERNEL_MOD",
        "regex": r"\b(modprobe|rmmod|insmod)\b",
        "message": "Unauthorized command blocked: modifying kernel modules.",
    },
    {
        "id": "SEC09_PACKET_SNIFF",
        "regex": r"\b(tcpdump|wireshark)\b",
        "message": "Unauthorized command blocked: network packet capture.",
    },
    {
        "id": "SEC10_SYS_PKG_REMOVE",
        "regex": r"\b(apt-get\s+remove|apt-get\s+purge|apt\s+remove|apt\s+purge|yum\s+remove|dpkg\s+-(r|P)|rpm\s+-e)\b",
        "message": "Unauthorized command blocked: removing system packages.",
    },
    {
        "id": "SEC11_CURL_PIPE_SHELL",
        "regex": r"\b(curl|wget)\b.*\s+\|\s*\b(sh|bash|zsh|dash)\b",
        "message": "Unauthorized command blocked: executing scripts directly from the web.",
    },
    {
        "id": "SEC12_SHELL_INJECTION",
        "regex": r"(`|\$\()",
        "message": "Potential command injection blocked: use of backticks or subshells.",
    },
    {
        "id": "SEC13_CHROOT_ESCAPE",
        "regex": r"\bchroot\b",
        "message": "Unauthorized command blocked: chroot escape attempt.",
    },
    {
        "id": "SEC14_SYS_PERM_DISRUPT",
        "regex": r"\b(chmod|chown)\b\s+-[a-zA-Z]*R[a-zA-Z]*\s+[^/]*\s+/",
        "message": "Unauthorized command blocked: modifying system root path permissions.",
    },
    {
        "id": "SEC15_LINKER_HIJACK",
        "regex": r"\b(LD_PRELOAD|LD_LIBRARY_PATH)=",
        "message": "Unauthorized command blocked: modifying library preloads or linker paths.",
    },
    {
        "id": "SEC16_DEVICE_MOUNT",
        "regex": r"\b(mount|umount)\b",
        "message": "Unauthorized command blocked: modifying system mounts.",
    },
    {
        "id": "SEC17_DNS_TAMPER",
        "regex": r"\b(etc/hosts|etc/resolv.conf)\b",
        "message": "Unauthorized command blocked: altering DNS resolution mappings.",
    },
    {
        "id": "SEC18_CRYPTOMINING",
        "regex": r"\b(xmrig|minerd)\b",
        "message": "Unauthorized command blocked: running cryptominers.",
    },
    {
        "id": "SEC19_HOST_COMPILATION",
        "regex": r"\b(gcc|clang|make)\b",
        "message": "Unauthorized command blocked: compiling foreign code on host.",
    },
    {
        "id": "SEC20_CRON_PERSISTENCE",
        "regex": r"\b(crontab|etc/cron\.(d|hourly|daily|weekly|monthly)|var/spool/cron)\b",
        "message": "Unauthorized command blocked: setting up task persistence.",
    },
    {
        "id": "SEC21_REVERSE_SHELL",
        "regex": r"\b(nc|netcat)\b.*\s+-[a-zA-Z]*e[a-zA-Z]*\b|/dev/tcp/[0-9]",
        "message": "Unauthorized command blocked: reverse shell execution.",
    },
]


def validate_command(cmd: str) -> None:
    """Validate command string against a set of predefined security rules.

    Args:
        cmd: Command string to validate.

    Raises:
        SecurityError: If command matches any security block regex.
    """
    for rule in SECURITY_RULES:
        if re.search(rule["regex"], cmd):
            raise SecurityError(f"Blocked by {rule['id']}: {rule['message']}")


def main() -> None:
    """Main CLI entry point reading from stdin."""
    cmd = sys.stdin.read().strip()
    try:
        validate_command(cmd)
        sys.exit(0)
    except SecurityError as err:
        sys.stderr.write(f"Error: {err}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

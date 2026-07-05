# validate_tool_call Spec

This script reads command strings from stdin to block destructive or unauthorized executions before they run.

## Specification

```yaml
name: validate_tool_call.py
path: .agents/scripts/validate_tool_call.py
input: stdin (raw command string)
output: stdout/stderr
exit_codes:
  success: 0 (safe command)
  blocked: 1 (unsafe command matching a security check rule)

rules:
  - id: SEC01_ROOT_DELETION
    regex: 'rm\s+-[a-zA-Z]*r[a-zA-Z]*f\s+/'
    message: "Destructive command blocked: root directory deletion."
  - id: SEC02_SYS_DELETION
    regex: 'rm\s+-[a-zA-Z]*r[a-zA-Z]*f\s+/(etc|usr|var|home|boot|dev|sys|proc)\b'
    message: "Destructive command blocked: critical system directory deletion."
  - id: SEC03_DISK_FORMAT
    regex: '\b(mkfs|fdisk|parted|gparted)\b'
    message: "Unauthorized command blocked: disk formatting / partitioning."
  - id: SEC04_RAW_DISK_WRITE
    regex: '(>|dd\s+.*of=)/dev/(sd[a-z]|nvme[0-9]+n[0-9]+|xvd[a-z])'
    message: "Unauthorized command blocked: writing directly to raw disk."
  - id: SEC05_CONFIG_TAMPER
    regex: '\b(etc/passwd|etc/shadow|etc/sudoers)\b'
    message: "Unauthorized command blocked: altering system configuration files."
  - id: SEC06_NET_DISRUPT
    regex: '\b(iptables|ufw|nftables|ip\s+route)\b'
    message: "Unauthorized command blocked: altering network routing or firewall."
  - id: SEC07_PROC_KILL
    regex: '\b(kill\s+-[0-9]+\s+1|kill\s+-9\s+1|killall\s+systemd|killall\s+init)\b'
    message: "Unauthorized command blocked: terminating system-critical processes."
  - id: SEC08_KERNEL_MOD
    regex: '\b(modprobe|rmmod|insmod)\b'
    message: "Unauthorized command blocked: modifying kernel modules."
  - id: SEC09_PACKET_SNIFF
    regex: '\b(tcpdump|wireshark)\b'
    message: "Unauthorized command blocked: network packet capture."
  - id: SEC10_SYS_PKG_REMOVE
    regex: '\b(apt-get\s+remove|apt-get\s+purge|apt\s+remove|apt\s+purge|yum\s+remove|dpkg\s+-(r|P)|rpm\s+-e)\b'
    message: "Unauthorized command blocked: removing system packages."
  - id: SEC11_CURL_PIPE_SHELL
    regex: '\b(curl|wget)\b.*\s+\|\s*\b(sh|bash|zsh|dash)\b'
    message: "Unauthorized command blocked: executing scripts directly from the web."
  - id: SEC12_SHELL_INJECTION
    regex: '(`|\$\()'
    message: "Potential command injection blocked: use of backticks or subshells."
  - id: SEC13_CHROOT_ESCAPE
    regex: '\bchroot\b'
    message: "Unauthorized command blocked: chroot escape attempt."
  - id: SEC14_SYS_PERM_DISRUPT
    regex: '\b(chmod|chown)\b\s+-[a-zA-Z]*R[a-zA-Z]*\s+[^/]*\s+/'
    message: "Unauthorized command blocked: modifying system root path permissions."
  - id: SEC15_LINKER_HIJACK
    regex: '\b(LD_PRELOAD|LD_LIBRARY_PATH)='
    message: "Unauthorized command blocked: modifying library preloads or linker paths."
  - id: SEC16_DEVICE_MOUNT
    regex: '\b(mount|umount)\b'
    message: "Unauthorized command blocked: modifying system mounts."
  - id: SEC17_DNS_TAMPER
    regex: '\b(etc/hosts|etc/resolv.conf)\b'
    message: "Unauthorized command blocked: altering DNS resolution mappings."
  - id: SEC18_CRYPTOMINING
    regex: '\b(xmrig|minerd)\b'
    message: "Unauthorized command blocked: running cryptominers."
  - id: SEC19_HOST_COMPILATION
    regex: '\b(gcc|clang|make)\b'
    message: "Unauthorized command blocked: compiling foreign code on host."
  - id: SEC20_CRON_PERSISTENCE
    regex: '\b(crontab|etc/cron\.(d|hourly|daily|weekly|monthly)|var/spool/cron)\b'
    message: "Unauthorized command blocked: setting up task persistence."
  - id: SEC21_REVERSE_SHELL
    regex: '\b(nc|netcat)\b\s+-[a-zA-Z]*e[a-zA-Z]*\b|/dev/tcp/[0-9]'
    message: "Unauthorized command blocked: reverse shell execution."
```

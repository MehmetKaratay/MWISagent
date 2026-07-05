# validate_tool_call.py

This utility script intercepts and validates commands passed to the `run_command` execution tool. It evaluates input command strings from `stdin` against 21 security rules, preventing destructive actions or unauthorized lateral movements.

## Usage

### Direct CLI Use
Feed a command via standard input (`stdin`) to check its security:
```bash
$ echo "git status" | python .agents/scripts/validate_tool_call.py
$ echo $?
0

$ echo "rm -rf /" | python .agents/scripts/validate_tool_call.py
Error: Blocked by SEC01_ROOT_DELETION: Destructive command blocked: root directory deletion.
$ echo $?
1
```

### Python API Usage
Import and call the validation function programmatically:
```python
from validate_tool_call import validate_command, SecurityError

try:
    validate_command("rm -rf /etc")
except SecurityError as err:
    print(f"Validation failed: {err}")
```

## Configured Checks
The validator checks for:
1. **SEC01_ROOT_DELETION**: `rm -rf /`
2. **SEC02_SYS_DELETION**: `rm -rf` on `/etc`, `/usr`, `/var`, `/home`, etc.
3. **SEC03_DISK_FORMAT**: Disk formatting commands (`mkfs`, `fdisk`, `parted`).
4. **SEC04_RAW_DISK_WRITE**: Writing directly to block devices (`/dev/sd*`).
5. **SEC05_CONFIG_TAMPER**: Overwriting critical system files (`/etc/passwd`, `/etc/shadow`).
6. **SEC06_NET_DISRUPT**: Firewall modifications (`iptables`, `ufw`).
7. **SEC07_PROC_KILL**: Killing init or systemd daemon.
8. **SEC08_KERNEL_MOD**: Modifying kernel modules (`modprobe`, `rmmod`).
9. **SEC09_PACKET_SNIFF**: Packet capturing tools (`tcpdump`).
10. **SEC10_SYS_PKG_REMOVE**: Purging packages via apt-get, yum, or rpm.
11. **SEC11_CURL_PIPE_SHELL**: Piped script installations (`curl ... | bash`).
12. **SEC12_SHELL_INJECTION**: Nested command expansions or subshells.
13. **SEC13_CHROOT_ESCAPE**: `chroot` commands.
14. **SEC14_SYS_PERM_DISRUPT**: Permission changes on root.
15. **SEC15_LINKER_HIJACK**: Linker preloads/overrides (`LD_PRELOAD`).
16. **SEC16_DEVICE_MOUNT**: Modifying system device mounts.
17. **SEC17_DNS_TAMPER**: Modifying `/etc/hosts` or `/etc/resolv.conf`.
18. **SEC18_CRYPTOMINING**: Cryptominer executables (`xmrig`).
19. **SEC19_HOST_COMPILATION**: Compiler commands (`gcc`, `clang`, `make`).
20. **SEC20_CRON_PERSISTENCE**: Modifying cron scheduled jobs.
21. **SEC21_REVERSE_SHELL**: Running netcat with execute flags or reverse sockets.

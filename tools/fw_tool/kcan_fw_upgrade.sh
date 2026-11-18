#!/bin/sh
# Compatibility entry point: keep Bash/Python upgrade behavior identical.
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -f "$script_dir/kcan_fw_upgrade.py" ]; then
    exec python3 "$script_dir/kcan_fw_upgrade.py" "$@"
fi
exec python3 "$script_dir/kcan_fw_upgrade" "$@"

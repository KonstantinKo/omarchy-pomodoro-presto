#!/usr/bin/env bash
# Explicitly install the companion application; Omarchy never runs this on plugin add.
set -euo pipefail
plugin_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
presto_binary=${1:-}
if [[ -z $presto_binary || ! -f $presto_binary || ! -x $presto_binary ]]; then
  echo 'Usage: bash install-runtime.sh /path/to/presto (an executable from the matching release)' >&2
  exit 1
fi
for dependency in python3 systemctl hyprctl install mktemp; do
  command -v "$dependency" >/dev/null || { echo "Missing dependency: $dependency" >&2; exit 1; }
done
hypr_config="$HOME/.config/hypr/hyprland.lua"
[[ -f $hypr_config ]] || { echo "Expected Omarchy Hyprland config at $hypr_config" >&2; exit 1; }
installed_binary="$HOME/.local/bin/presto"
if [[ -x $installed_binary ]]; then
  status=$("$installed_binary" --omarchy-control status 2>/dev/null || true)
  if [[ -n $status ]] && ! python3 - "$status" <<'PY'
import json, sys
try:
    state = json.loads(sys.argv[1])
except json.JSONDecodeError:
    sys.exit(0)
if state.get('isRunning') or state.get('isPaused'):
    sys.exit(1)
PY
  then
    echo 'Presto has an active or paused session. Finish it before installing an update.' >&2
    exit 1
  fi
fi
service_active=false
if systemctl --user is-active --quiet presto-omarchy.service; then
  service_active=true
  if ! python3 - "${status:-}" <<'PY'
import json, sys
try:
    state = json.loads(sys.argv[1])
except json.JSONDecodeError:
    sys.exit(1)
sys.exit(0 if state.get('ready') is True else 1)
PY
  then
    echo 'The existing Presto service is not ready; refusing to interrupt it.' >&2
    exit 1
  fi
fi
mkdir -p "$HOME/.local/state/presto-omarchy/backups" "$HOME/.local/bin" "$HOME/.config/systemd/user"
backup_dir=$(mktemp -d "$HOME/.local/state/presto-omarchy/backups/install.XXXXXXXX")
for path in "$installed_binary" "$HOME/.config/systemd/user/presto-omarchy.service" "$hypr_config" "$HOME/.config/hypr/presto.lua"; do
  if [[ -e $path ]]; then cp -a -- "$path" "$backup_dir/$(basename "$path")"; fi
done
if $service_active; then systemctl --user stop presto-omarchy.service; fi
install -m 755 -- "$presto_binary" "$installed_binary.new"
mv -- "$installed_binary.new" "$installed_binary"
install -m 644 "$plugin_dir/presto-omarchy.service" "$HOME/.config/systemd/user/presto-omarchy.service"
install -m 644 "$plugin_dir/window.lua" "$HOME/.config/hypr/presto.lua"
python3 - "$hypr_config" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
content = path.read_text()
if 'require("hypr.presto")' not in content:
    path.write_text(content + '\n-- Presto desktop widget\nrequire("hypr.presto")\n')
PY
hyprctl reload
config_errors=$(hyprctl configerrors)
if [[ -n $config_errors && $config_errors != ok ]]; then
  printf 'Hyprland configuration error: %s\nBackups: %s\n' "$config_errors" "$backup_dir" >&2
  exit 1
fi
systemctl --user daemon-reload
systemctl --user enable --now presto-omarchy.service
printf 'Installed the Presto runtime. Backups: %s\n' "$backup_dir"

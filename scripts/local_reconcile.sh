#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <a_json> <b_json>" >&2
  exit 1
fi
python -m v2.ccr.services.reconcile.app "$1" "$2"

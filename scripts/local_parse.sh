#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <input_ccda_xml> [output_json]" >&2
  exit 1
fi
INPUT="$1"
OUTPUT="${2:-}"
if [[ -n "$OUTPUT" ]]; then
  python v2/ccr/functions/parse_ccda/main.py --local-file "$INPUT" --output "$OUTPUT"
else
  python v2/ccr/functions/parse_ccda/main.py --local-file "$INPUT"
fi

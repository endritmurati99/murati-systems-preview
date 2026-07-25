#!/usr/bin/env bash
# Manual fallback pipeline for the Murati Systems Gate-1 run while Claude Design is quota-blocked.
set -euo pipefail

sub="${1:-}"; shift || true

case "$sub" in
  generate)
    project_dir="${1:?project dir required}"
    brief_file="${2:?brief file required}"
    out_dir="${3:?out dir required}"
    mkdir -p "$out_dir"
    count="$(find "$out_dir" -mindepth 1 -maxdepth 1 -type d -name '0*' | wc -l | tr -d ' ')"
    if [ "$count" -lt 3 ]; then
      echo "manual fallback expected existing 3 direction folders under $out_dir for $brief_file" >&2
      exit 2
    fi
    ;;
  refine)
    project_dir="${1:?project dir required}"
    pick="${2:?pick required}"
    out_dir="${3:?out dir required}"
    mapfile -t dirs < <(find "$project_dir/out" -mindepth 1 -maxdepth 1 -type d -name '0*' | sort)
    if ! [[ "$pick" =~ ^[1-9][0-9]*$ ]] || [ "$pick" -lt 1 ] || [ "$pick" -gt "${#dirs[@]}" ]; then
      echo "bad pick $pick" >&2
      exit 2
    fi
    src="${dirs[$((pick - 1))]}"
    rm -rf "$out_dir/final"
    mkdir -p "$out_dir/final"
    cp -R "$src"/. "$out_dir/final/"
    ;;
  *)
    echo "unknown subcommand: $sub" >&2
    exit 2
    ;;
esac

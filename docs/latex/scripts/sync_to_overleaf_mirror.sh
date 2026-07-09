#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: sync_to_overleaf_mirror.sh [--dry-run] [--mirror-root PATH]

Synchronize docs/latex into a separate, flat Overleaf Git checkout. The mirror
is made an exact projection of docs/latex except for scripts/ and builds/.
Set MEA_OVERLEAF_MIRROR or pass --mirror-root to select the mirror checkout.
EOF
}

dry_run=false
mirror_root=${MEA_OVERLEAF_MIRROR:-}

while (($#)); do
    case "$1" in
        --dry-run)
            dry_run=true
            ;;
        --mirror-root)
            (($# >= 2)) || { usage >&2; exit 2; }
            mirror_root=$2
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            usage >&2
            exit 2
            ;;
    esac
    shift
done

command -v rsync >/dev/null || { echo 'rsync is required.' >&2; exit 1; }
[[ -n "$mirror_root" ]] || { echo 'Set MEA_OVERLEAF_MIRROR or pass --mirror-root.' >&2; exit 1; }

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
source_root=$(cd -- "$script_dir/.." && pwd -P)
mirror_root=$(cd -- "$mirror_root" && pwd -P)

[[ -d "$mirror_root/.git" ]] || { echo "Mirror root is not a Git checkout: $mirror_root" >&2; exit 1; }

rsync_args=(--archive --delete --exclude '.git/' --exclude '__pycache__/' --exclude '.pytest_cache/' --exclude '*.aux' --exclude '*.bbl' --exclude '*.blg' --exclude '*.fdb_latexmk' --exclude '*.fls' --exclude '*.log' --exclude '*.out' --exclude '*.synctex.gz' --exclude '*.xdv')
if "$dry_run"; then
    rsync_args+=(--dry-run --itemize-changes)
fi

printf 'Source LaTeX folder: %s\nMirror root: %s\n' "$source_root" "$mirror_root"

while IFS= read -r -d '' source_entry; do
    name=${source_entry##*/}
    [[ "$name" == scripts || "$name" == builds ]] && continue
    if [[ -d "$source_entry" ]]; then
        if ! "$dry_run"; then
            mkdir -p -- "$mirror_root/$name"
        fi
        rsync "${rsync_args[@]}" -- "$source_entry/" "$mirror_root/$name/"
    else
        rsync "${rsync_args[@]}" -- "$source_entry" "$mirror_root/$name"
    fi
done < <(find "$source_root" -mindepth 1 -maxdepth 1 -print0)

while IFS= read -r -d '' mirror_entry; do
    name=${mirror_entry##*/}
    [[ "$name" == .git ]] && continue
    if [[ "$name" == scripts || "$name" == builds || ! -e "$source_root/$name" ]]; then
        if "$dry_run"; then
            printf 'would remove %s\n' "$mirror_entry"
        else
            rm -rf -- "$mirror_entry"
        fi
    fi
done < <(find "$mirror_root" -mindepth 1 -maxdepth 1 -print0)

printf 'LaTeX mirror sync complete.\n'

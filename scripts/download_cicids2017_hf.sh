#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DATA_DIR="${PROJECT_ROOT}/data/CICIDS2017/machine_learning"
BASE_URL="https://huggingface.co/datasets/bvsam/cic-ids-2017/resolve/main/machine_learning"

FILES=(
  "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv.parquet"
  "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv.parquet"
  "Friday-WorkingHours-Morning.pcap_ISCX.csv.parquet"
  "Monday-WorkingHours.pcap_ISCX.csv.parquet"
  "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv.parquet"
  "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv.parquet"
  "Tuesday-WorkingHours.pcap_ISCX.csv.parquet"
  "Wednesday-workingHours.pcap_ISCX.csv.parquet"
)

mkdir -p "${DATA_DIR}"

for filename in "${FILES[@]}"; do
  target="${DATA_DIR}/${filename}"
  if [[ ! -f "${target}" ]]; then
    curl -L "${BASE_URL}/${filename}" -o "${target}"
  fi
done

find "${DATA_DIR}" -type f -name '*.parquet' -print | sort

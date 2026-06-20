#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DATA_DIR="${PROJECT_ROOT}/data/CICIDS2017"
ARCHIVE_PATH="${DATA_DIR}/MachineLearningCSV.zip"
EXTRACT_DIR="${DATA_DIR}/MachineLearningCVE"
SOURCE_URL="http://205.174.165.80/CICDataset/CIC-IDS-2017/Dataset/CIC-IDS-2017/CSVs/MachineLearningCSV.zip"

mkdir -p "${DATA_DIR}"

if [[ ! -f "${ARCHIVE_PATH}" ]]; then
  curl -L "${SOURCE_URL}" -o "${ARCHIVE_PATH}"
fi

if [[ ! -d "${EXTRACT_DIR}" ]]; then
  unzip -o "${ARCHIVE_PATH}" -d "${DATA_DIR}"
fi

find "${DATA_DIR}" -type f -name '*.csv' -print | sort

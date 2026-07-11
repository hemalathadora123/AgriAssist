#!/usr/bin/env bash
set -euo pipefail

mkdir -p "${HOME}/.streamlit"
cp .streamlit/config.toml "${HOME}/.streamlit/config.toml"

echo "Streamlit config installed for Render."

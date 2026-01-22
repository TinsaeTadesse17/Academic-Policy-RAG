#!/bin/bash
set -e
# Install CPU-only PyTorch first to save memory (much smaller, no CUDA)
pip install torch==2.5.0 --index-url https://download.pytorch.org/whl/cpu
# Then install other requirements
pip install -r requirements.txt

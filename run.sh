#!/bin/bash
set -a
export PYTHONPATH=$PYTHONPATH:$(pwd)/app
source .env
uvicorn --reload --log-level debug app.main:app --host 0.0.0.0

#!/bin/bash

# Script to run tests using pytest
echo "-> running pytest ..."
uv run -m pytest tests/ -v

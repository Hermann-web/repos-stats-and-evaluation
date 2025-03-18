#!/bin/bash

# Script to run tests using pytest
echo "-> running pytest ..."
uv run coverage run -m pytest tests/

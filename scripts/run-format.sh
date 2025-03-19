#!/bin/bash

# Script to sort imports and format code using ruff for files in the src directory

echo "-> running ruff sort ..."
uv run ruff check --select I --fix src/ tests/ *.py # Check for isort issues and fix them

echo "-> running ruff format ..."
uv run ruff format src/ tests/ *.py # Format code using ruff

echo "-> running mypy ..."
uv run mypy  src/ tests/ *.py 
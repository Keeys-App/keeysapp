#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run tests with coverage
echo "Running tests with coverage..."
pytest --cov=app --cov-report=term-missing --cov-report=html -v

# Show coverage summary
echo ""
echo "Coverage report generated in htmlcov/index.html"
echo "Open it with: open htmlcov/index.html"


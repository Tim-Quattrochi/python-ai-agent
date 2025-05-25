#!/bin/bash

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the tests
python3 -m pytest tests/test_task_scheduler.py -v

# Optional: Run with more detailed output
# python3 tests/test_task_scheduler.py
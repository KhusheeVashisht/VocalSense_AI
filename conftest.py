"""Pytest configuration ensuring workspace root is on sys.path."""
import os
import sys

workspace_dir = os.path.dirname(os.path.abspath(__file__))
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

# Ensure TF logging is quiet
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["USE_TF"] = "0"

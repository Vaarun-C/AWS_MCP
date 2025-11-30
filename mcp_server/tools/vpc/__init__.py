"""
EC2 Tools Module

This module aggregates all EC2-related tools from their respective submodules.
Import this module to get access to all EC2 tools.
"""

from .describe_vpc import tools as describe_tools

# Aggregate all tools into a single list
tools = [
    *describe_tools,
]

__all__ = [
    "describe_tools",
]

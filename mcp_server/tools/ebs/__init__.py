"""
EBS Tools Module

This module aggregates all EBS-related tools from their respective submodules.
Import this module to get access to all EBS tools.
"""

from .attachment_tools import tools as attachment_tools
from .snapshot_tools import tools as snapshot_tools
from .volume_tools import tools as volume_tools

# Aggregate all tools into a single list
tools = [
    *attachment_tools,
    *snapshot_tools,
    *volume_tools,
]

__all__ = [
    "attachment_tools",
    "snapshot_tools",
    "volume_tools",
]

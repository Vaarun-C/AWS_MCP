"""
EC2 Tools Module

This module aggregates all EC2-related tools from their respective submodules.
Import this module to get access to all EC2 tools.
"""

from .list import tools as list_tools
from .instance_lifecycle import tools as lifecycle_tools
from .instance_creation import tools as instance_creation_tools
from .keypair import tools as keypair_tools
from .security_groups import tools as security_group_tools
from .launch_templates import tools as launch_template_tools

# Aggregate all tools into a single list
tools = [
    *list_tools,                 # 8 tools: list instances, get details, spot requests, etc.
    *lifecycle_tools,            # 5 tools: start, stop, reboot, hard reboot, terminate
    *instance_creation_tools,    # 4 tools: create instance, create minimal, create spot, generate SSH instructions
    *keypair_tools,              # 3 tools: create, delete, list keypairs
    *security_group_tools,       # 6 tools: create, delete, authorize, revoke, describe, list SGs
    *launch_template_tools,      # 6 tools: create, create version, describe, delete, list, launch from template
]

# Export individual tool lists for granular imports
__all__ = [
    "tools",
    "list_tools",
    "lifecycle_tools",
    "instance_creation_tools",
    "keypair_tools",
    "security_group_tools",
    "launch_template_tools",
]

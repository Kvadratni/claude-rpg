#!/usr/bin/env python3
"""
Setup script for RPG MCP Server
"""

from setuptools import setup

setup(
    name="rpg-mcp",
    version="1.0.0",
    description="Model Context Protocol server for RPG Game AI NPCs",
    author="AI NPC System",
    py_modules=["rpg_mcp_server"],
    install_requires=[
        "mcp>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "rpg-mcp=rpg_mcp_server:main",
        ],
    },
    python_requires=">=3.8",
)
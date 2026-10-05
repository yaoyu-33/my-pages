# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Run the pinned Gym weather app alone for the tutorial's HTTP exercise."""
import argparse
import json
import os
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--gym-root', type=Path, required=True)
parser.add_argument('--port', type=int, default=18080)
args = parser.parse_args()
root = args.gym_root.resolve()
if not (root / 'resources_servers/example_single_tool_call/app.py').is_file():
    parser.error('--gym-root must point to the pinned full Gym checkout')
if not 1024 <= args.port <= 65535:
    parser.error('--port must be between 1024 and 65535')

# A normal `gym env start` supplies this resolved configuration to child processes.
# For this single-service exercise we supply it explicitly; no Head process is started.
config = {
    'dry_run': False,
    'head_server': {'host': '127.0.0.1', 'port': 1},
    'weather_demo': {
        'resources_servers': {
            'example_single_tool_call': {
                'host': '127.0.0.1',
                'port': args.port,
                'entrypoint': 'app.py',
                'domain': 'agent',
            }
        }
    },
}
os.environ['NEMO_GYM_CONFIG_DICT'] = json.dumps(config)
os.environ['NEMO_GYM_CONFIG_PATH'] = 'weather_demo'
sys.path.insert(0, str(root))
os.chdir(root)

from resources_servers.example_single_tool_call.app import SimpleWeatherResourcesServer

# Reuse the actual Gym startup path, middleware, routes and business implementation.
SimpleWeatherResourcesServer.run_webserver()

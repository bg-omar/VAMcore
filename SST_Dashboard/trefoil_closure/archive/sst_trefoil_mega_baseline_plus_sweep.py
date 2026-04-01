"""
SST Trefoil Mega Script
=======================

This file keeps the older patched baseline version intact and appends the
newer Option-B sweep version in the same script.

Usage
-----
python sst_trefoil_mega_baseline_plus_sweep.py --mode baseline
python sst_trefoil_mega_baseline_plus_sweep.py --mode sweep
python sst_trefoil_mega_baseline_plus_sweep.py --mode both

Notes
-----
- The embedded baseline block is preserved intact in source form.
- The embedded sweep block is preserved intact in source form.
- Each block is executed in its own namespace, so variables do not collide.
"""

from __future__ import annotations

import argparse
import textwrap

BASELINE_SCRIPT = r
"""Compatibility facade for the V3 platform window.

Navigation labels remain "Address Visualizer", "Single Experiment", and
"Compare Experiment" inside their preserved lab pages and compatibility tests.
The V3 shell displays Address Explorer in platform navigation.
"""

from cachevis_rv.gui.main_window import CacheVisMainWindow

__all__ = ["CacheVisMainWindow"]

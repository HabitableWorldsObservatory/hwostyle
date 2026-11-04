"""Shared fixtures for hwostyle tests."""

import importlib.util
import os

from hypothesis import settings

# The optional budget plugin may be absent, including hwoutils itself.
pytest_plugins = []
if (
    importlib.util.find_spec("hwoutils") is not None
    and importlib.util.find_spec("hwoutils.testbudget") is not None
):
    pytest_plugins.append("hwoutils.testbudget.plugin")

settings.register_profile("quick", max_examples=25, deadline=None)
settings.register_profile("nightly", max_examples=200, deadline=None)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "quick"))

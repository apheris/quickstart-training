# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

# Patch the decorator before any imports
import os
from pathlib import Path
from unittest.mock import patch

import pytest

# Set up test environment variables
os.environ["APH_DATA"] = '{"whas1_gateway-1_org-1": "cohort1"}'
os.environ["APH_API_DAL_URL"] = "http://localhost"
os.environ["APH_DAL_TOKEN"] = "test_token"


def identity_decorator(func):
    return func


# Start the patch globally for all tests. This is necessary to patch the decorator
# before any imports that might use it. Otherwise, the decorator hides the true error
# and makes debugging difficult.
_patch = patch(
    "apheris_utils.extras_nvflare.logging.gateway_log_sender"
    ".safe_error_catchall_decorator",
    identity_decorator,
)
_patch.start()


@pytest.fixture
def assets_path():
    return Path(__file__).parent.resolve() / "assets"

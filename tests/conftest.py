# pylint: disable=missing-function-docstring,missing-module-docstring,no-self-use,unused-import
import os
import json

import pytest

# from collector.endpoint import Endpoint
from config import TestingConfig


@pytest.fixture
def conf():
    yield TestingConfig()


# @pytest.fixture
# def endpoints():
#     yield Endpoint.load_from_config(conf)


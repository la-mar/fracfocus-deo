import pytest  # noqa
import requests
import re
from datetime import datetime

from requests_mock import ANY

import util

expected_url = "https://api.example.com/v3/path/to/endpoint"


class TestTokenManager:
    def test_token_urljoin_vanilla(self, conf):
        url = conf.API_BASE_URL
        path = "/path/to/endpoint"
        assert util.urljoin(url, path) == expected_url

    def test_token_urljoin_double_slash(self, conf):
        url = f"{conf.API_BASE_URL}/"
        path = "/path/to/endpoint"
        assert util.urljoin(url, path) == expected_url

    def test_token_urljoin_no_slash(self, conf):
        url = conf.API_BASE_URL
        path = "path/to/endpoint"
        assert util.urljoin(url, path) == expected_url


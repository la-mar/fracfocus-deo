""" Manages access tokens for an api interface """
from __future__ import annotations

import logging
import urllib.parse

from oauthlib.oauth2 import (
    LegacyApplicationClient,
    BackendApplicationClient,
    TokenExpiredError,
)

from requests_oauthlib import OAuth2Session
from datetime import datetime, timedelta
from collector.yammler import Yammler
from config import BaseConfig
from collector.util import retry
import util

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages the Bearer token for a given service in an automated way."""

    client_id = None
    client_secret = None
    username = None
    password = None

    def __init__(
        self,
        client_type: str,
        url: str = None,
        headers: dict = None,
        cache: str = None,
        **kwargs,
    ):
        self._client_type = client_type
        self.url = url or util.urljoin(
            kwargs.get("base_url", ""), kwargs.get("token_path", "")
        )
        self.headers = headers
        self.cache = Yammler(cache or "./config/token.yaml")
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def client_type(self):
        client_map = {
            "legacy": self._get_access_token_legacy,
            "backend": self._get_access_token_backend,
        }

        try:
            return client_map[self._client_type]
        except KeyError:
            raise KeyError(
                f"{self._client_type} not found in available clients.  Valid options are: {list(client_map.keys())}"
            )

    def _get_access_token_backend(self):
        """Fetch a new access token from the provider using OAuth2"""
        # https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#backend-application-flow

        client = BackendApplicationClient(client_id=self.client_id)
        oauth = OAuth2Session(client=client)
        # oauth.populate_token_attributes(
        #     token_url=self.url,
        #     auth=(self.client_id, self.client_secret),
        #     headers=self.headers,
        # )
        return dict(
            oauth.fetch_token(
                token_url=self.url,
                auth=(self.client_id, self.client_secret),
                headers=self.headers,
            )
        )

    def _get_access_token_legacy(self):
        """Fetch a new access token from the provider using OAuth2"""
        # https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#backend-application-flow
        oauth = OAuth2Session(client=LegacyApplicationClient(client_id=self.client_id))

        return dict(
            oauth.fetch_token(
                token_url=self.url,
                username=self.username,
                password=self.password,
                client_id=self.client_id,
                client_secret=self.client_secret,
            )
        )

    def _cache_token(self, token: dict):
        """Save response token and token expiration date to configuration file.
        Arguments:
            response_token {dict} -- oauth response object
        Returns:
            str -- response token as string
        """

        self.cache["token"] = token
        self.cache["token_expiration"] = datetime.utcfromtimestamp(token["expires_at"])
        self.cache.dump()
        return token

    @retry(Exception, tries=3, delay=5, backoff=2, logger=logger)
    def get_token_dict(self, force_refresh: bool = False) -> dict:
        """ Checks if saved token is still valid"""
        token = self.cache.get("token")
        expiration = self.cache.get("token_expiration")

        if not force_refresh:
            # if expiration date exists and is a datetime
            if expiration is not None and isinstance(expiration, datetime):
                # if current time is < time of expiration minus one day
                if datetime.now() < expiration - timedelta(hours=1):

                    return token  # current token is valid

        # Token isn't valid. Return new token
        logger.info("Retrieved new token.")
        return self._cache_token(self.client_type())

    def get_token(self, force_refresh=False):
        """Returns bearer authorization string for inclusion
            in request header.
        Returns:
            str -- bearer string
        """
        token = self.get_token_dict(force_refresh=force_refresh)
        return f"{token['token_type']} {token['access_token']}"

    @classmethod
    def from_app_config(cls, conf: BaseConfig) -> TokenManager:
        return TokenManager(**conf.api_params)


if __name__ == "__main__":

    from config import get_active_config

    conf = get_active_config()
    tm = TokenManager(**conf.api_params)

    tm.url
    tm.get_token_dict()
    list(tm.get_token_dict().keys())
    tm.get_token()

"""REST client handling, including hellobatonStream base class."""

import requests
from urllib.parse import (
    urlparse,
    parse_qs
)
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import APIKeyAuthenticator


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class hellobatonStream(RESTStream):
    """hellobaton stream class."""

    results_per_page: int = 100

    #BATON has a dynamically generated base url based on customer installation
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        company=self.config["company"]
        return f"https://{company}.hellobaton.com/api"

    @property
    def authenticator(self) -> APIKeyAuthenticator:
        """Return a new authenticator object."""
        return APIKeyAuthenticator.create_for_stream(
            self,
            key = "api_key",
            value = self.config.get("api_key"),
            location  = "params"
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""

        payload = response.json()
        result_count = payload['count']

        if result_count > self.results_per_page:
            #next returns a full link we just want the query string for pagination
            query_string = urlparse(payload['next']).query
            #@TODO - error handle for bad q strings instead of passing pagination exit criteria None
            next_page_token = parse_qs(query_string).get('page', None)
        else:
            next_page_token = None

        return next_page_token

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            #baton expects the api key for pagination
            params['api_key'] = self.config['api_key']
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        for result in response.json()["results"]:
            yield result

    def post_process(self, row: dict, context: Optional[dict] = None ) -> Optional[Dict[Any,Any]]:
        """As needed, append or transform raw data to match expected structure."""
        return row

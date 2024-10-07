import base64
from typing import Optional
import urllib
import secrets
import urllib.parse
from dataclasses import dataclass

import requests

from app.spotify.models.tokens import Tokens


@dataclass
class Authorization_manager:
    def __init__(self, client_id: str, client_secret: str, auth_url: str, token_url: str, redirect_url: str, scope: str, tokens: Optional[Tokens] = None) -> None:
        self.state: str = None

        #TODO: clean up
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__auth_url = auth_url
        self.__token_url = token_url
        self.__redirect_url = redirect_url
        self.__scope = scope

        self.__tokens = tokens

    @property
    def access_token(self) -> str:
        if not self.__tokens or self.__tokens.refresh_token is None:
            # Start from zero: request user authorization and new tokens
            authorization_code = self.request_user_authorization()    #FIXME: actually return the code
            self.__tokens = self.__request_new_tokens("AQA2SERWeTu2YFxx1DkHaB6ZnPcCaIgLoHsNhCRrqnaYwa6wanOxEy9EMt_zEZamdchSBbq5HTfx-N606hNQYHEMrQb1hdb1mzu24suX_wOe5YugD7Z9u_PWsfFFMZUYC19g6Q8C59O3RqmYBd1kxFufU4MFbbpsAjfIZ4BwjXL8b7h6b_T5Vy1FGJqxau1BHN_J-sJKL8V6YxC3l2fCtckZzjOj3KBuSEJqM5jgXEvDVG-mUXsl9vE")
        elif self.__tokens.access_token is None or self.__tokens.access_token.is_expired:
            # Refresh the existing tokens
            self.__tokens.update(self.__refresh_tokens())
        return self.__tokens.access_token

    def __base_64_encode(self, text: str) -> str:
        """Encodes str to byte format, performs base64 encoding and transforms the result back to a string; """
        byte_text: bytes = text.encode()
        b64_encoded_byte_text: bytes = base64.b64encode(byte_text)
        b64_encoded_text: str = b64_encoded_byte_text.decode()
        return b64_encoded_text

    def __request_user_authorization(self) -> None:
        self.state=secrets.token_urlsafe(16), # Generates a secure 16-byte random string to prevent CSRF
        params = urllib.parse.urlencode({
            "client_id": self.__client_id,
            "response_type": "code",    # Static value dictated by the Spotify API docs
            "redirect_uri": self.__redirect_url,
            "state": self.state,
            "scope": self.__scope
            })
        response = requests.get(self.__auth_url, params, timeout=5)

        # TODO: automate this process
        # No automated way was present in the old code, so this function simply prints the URL out.
        # For now, a user must manually:
        #   open this link,
        #   extract the code and state from the redirect response after providing the needed permissions,
        #   save the code in the environment as "TEMP_USER_AUTH_CODE"
        print(response.url)

    def __request_new_tokens(self, authorization_code: str) -> Tokens:
        """ Exchanges a user authorization code for an access & refresh token. """
        url = self.__token_url
        parameters = {
            "grant_type": 'authorization_code',  # Static value dictated by the Spotify API docs
            "code": authorization_code,
            "redirect_uri": self.__redirect_url
            }
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + self.__base_64_encode(f"{self.__client_id}:{self.__client_secret}") # Form should be "Basic <base64 encoded client_id:client_secret>"
            }
        response = requests.post(
            url=url,
            params=parameters,
            headers=headers,
            timeout=5
            )
        if not response.ok:
            raise requests.HTTPError(f"{response.status_code} - {response.reason}: {response.text}")
        response_content = response.content.decode()
        print(f'__request_new_tokens: {response_content=}')
        return Tokens.from_dict(response_content)

    def __refresh_tokens(self) -> Tokens:
        params = urllib.parse.urlencode({
            "grant_type": 'refresh_token',
            "refresh_token": self.__tokens.refresh_token,
            "client_id": self.__client_id
        })
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(
            url=self.__token_url,
            params=params,
            headers=headers,
            timeout=5
            )
        if not response.ok:
            raise requests.HTTPError(f"{response.status_code} - {response.reason}: {response.text}")
        response_content = response.content.decode()
        return Tokens.from_dict(response_content)

    
#TODO: remove this
if __name__ == "__main__":
    from app.configuration.config_parser import ConfigParser
    from app.environment.environment_manager import EnvironmentManager

    env = EnvironmentManager("app\\environment\\.env").load_from_env()
    cfg = ConfigParser(env.config_file).load_config()

    auth_initializer = Authorization_manager(
        env.spotify_client_id,
        env.spotify_client_secret,
        cfg.spotify_config.api.authorization.url,
        cfg.spotify_config.api.authorization.token_url,
        cfg.spotify_config.api.authorization.redirect_url,
        cfg.spotify_config.api.authorization.permissions
    )
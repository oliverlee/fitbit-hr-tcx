#!/usr/bin/env python
# -*- coding: utf-8 -*-
import fitbit
import pickle
import threading
import webbrowser

DEFAULT_TOKEN_FILE = ".fitbit.token"


class OAuth2Server:
    def __init__(
        self,
        client_id,
        client_secret,
        redirect_uri="http://127.0.0.1:8080/",
        token_file=DEFAULT_TOKEN_FILE,
    ):
        """ Initialize the FitbitOauth2Client. """
        self.token_file = token_file

        try:
            token = self._load_token()

        except FileNotFoundError:
            access_token = None
            refresh_token = None
            expires_at = None
            refresh_cb = None
        else:
            access_token = token["access_token"]
            refresh_token = token["refresh_token"]
            expires_at = token["expires_at"]
            refresh_cb = lambda x: self._save_token(x)

        self.fitbit = fitbit.Fitbit(
            client_id,
            client_secret,
            redirect_uri=redirect_uri,
            timeout=10,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            refresh_cb=refresh_cb,
        )

        if access_token is None:
            self._browser_authorize()

    def _browser_authorize(self):
        """ Open a browser to the authorization url and wait for the response. """
        url, _ = self.fitbit.client.authorize_token_url()

        # Open the web browser in a new thread for command-line browser support
        threading.Timer(1, webbrowser.open, args=(url,)).start()

        code = input(
            "Enter code from url after granting authorization. Read+Write is necessary for intraday heart rate.\n"
        )
        token = self.fitbit.client.fetch_access_token(code)

        print(f"User authorized, writing access token to '{self.token_file}'")
        self._save_token(token)

    def _save_token(self, token):
        pickle.dump(token, open(self.token_file, "wb"))

    def _load_token(self):
        return pickle.load(open(self.token_file, "rb"))

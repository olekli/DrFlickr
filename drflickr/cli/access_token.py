# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.cli.path_options import creds_path_option
from drflickr.credentials import getCredentials
from drflickr.file import readYaml, writeYaml
from drflickr.api import Api
from drresult import Ok, Err, returns_result

import json
import os
import click
import logging
from requests_oauthlib import OAuth1Session

logger = logging.getLogger(__name__)


request_token_url = 'https://www.flickr.com/services/oauth/request_token'
base_authorization_url = 'https://www.flickr.com/services/oauth/authorize'
access_token_url = 'https://www.flickr.com/services/oauth/access_token'


@click.group()
def access_token():
    pass


@access_token.command()
@creds_path_option
def make_authorization_url(creds_path):
    os.umask(0o077)

    client_credentials = getCredentials(creds_path, 'api-key')
    if not client_credentials.is_ok():
        raise click.exceptions.Exit(code=1)

    client_credentials = client_credentials.unwrap()

    oauth = OAuth1Session(
        client_key=client_credentials['key'],
        client_secret=client_credentials['secret'],
        callback_uri='https://domain.invalid',
    )
    request_token_response = oauth.fetch_request_token(request_token_url)
    resource_owner_key = request_token_response.get('oauth_token')
    resource_owner_secret = request_token_response.get('oauth_token_secret')

    resource_owner_filename = os.path.join(
        creds_path, 'resource-owner-credentials.yaml'
    )
    result = writeYaml(
        resource_owner_filename,
        {'key': resource_owner_key, 'secret': resource_owner_secret},
    )
    if not result.is_ok():
        logger.error(
            f'Cannot write resource owner credentials to {filename}: {result.unwrap_err()}'
        )
        raise click.exceptions.Exit(code=1)
    authorization_url = oauth.authorization_url(base_authorization_url)
    print(f'{authorization_url}')


@access_token.command()
@creds_path_option
@click.argument('redirect_url')
def make_access_token(creds_path, redirect_url):
    os.umask(0o077)

    resource_owner_creds = getCredentials(creds_path, 'resource-owner-credentials')
    if resource_owner_creds.is_ok():
        logger.error(f'Do make-authorization-url first!')
        raise click.exceptions.Exit(code=1)
    resource_owner_creds = resource_owner_creds.unwrap()

    client_credentials = getCredentials(creds_path, 'api-key')
    if not client_credentials.is_ok():
        raise click.exceptions.Exit(code=1)
    client_credentials = client_credentials.unwrap()

    oauth = OAuth1Session(
        client_key=client_credentials['key'],
        client_secret=client_credentials['secret'],
        callback_uri='https://domain.invalid',
    )
    authorization_response = oauth.parse_authorization_response(redirect_url)
    oauth_verifier = authorization_response.get('oauth_verifier')

    oauth = OAuth1Session(
        client_key=client_credentials['key'],
        client_secret=client_credentials['secret'],
        resource_owner_key=resource_owner_creds['key'],
        resource_owner_secret=resource_owner_creds['secret'],
        verifier=oauth_verifier,
    )
    access_token = oauth.fetch_access_token(access_token_url)
    access_token_filename = os.path.join(creds_path, 'access-token.yaml')
    result = writeYaml(access_token_filename, access_token)
    if result.is_ok():
        print(f'Access token written to: {access_token_filename}')
        os.remove(os.path.join(creds_path, 'resource-owner-credentials.yaml'))
    else:
        logger.error(
            f'Unable to write access token to {access_token_filename}: {result.unwrap_err()}'
        )
        raise click.exceptions.Exit(code=1)


@returns_result()
def _test(creds_path):
    api_key = getCredentials(creds_path, 'api-key').unwrap_or_return()
    access_token = readYaml(
        os.path.join(creds_path, 'access-token.yaml')
    ).unwrap_or_return()
    api = (
        Api(dry_run=True, api_key=api_key, access_token=access_token)
        .load()
        .unwrap_or_return()
    )
    return Ok(None)


@access_token.command()
@creds_path_option
def test(creds_path):
    result = _test(creds_path)
    if result.is_ok():
        print(f'Access to Flickr is set up correctly!')
    else:
        print(f'Cannot access Flickr: {result.unwrap_err()}')
        raise click.exceptions.Exit(code=1)

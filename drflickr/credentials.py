# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.file import readYaml

from result import Err, is_ok, is_err
import json
import os
import logging

logger = logging.getLogger(__name__)


def getCredentials(creds_path, name):
    filename = os.path.join(creds_path, f'{name}.yaml')
    credentials = readYaml(filename)
    if (
        not is_ok(credentials)
        or 'key' not in credentials.ok_value
        or 'secret' not in credentials.ok_value
    ):
        logger.error(
            f'Provide {name} credentials as `key` and `secret` in file {filename}'
        )
        if is_err(credentials):
            logger.error(credentials.unwrap_err())
            return credentials
        else:
            return Err(None)
    return credentials

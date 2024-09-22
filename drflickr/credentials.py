# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.file import readYaml

from rust_result import Ok, Err, returns_result
import json
import os
import logging

logger = logging.getLogger(__name__)


def getCredentials(creds_path, name):
    filename = os.path.join(creds_path, f'{name}.yaml')
    credentials = readYaml(filename)
    if (
        not credentials.is_ok()
        or 'key' not in credentials.unwrap()
        or 'secret' not in credentials.unwrap()
    ):
        logger.error(
            f'Provide {name} credentials as `key` and `secret` in file {filename}'
        )
        if credentials.is_ok():
            logger.error(credentials.unwrap_err())
            return credentials
        else:
            return Err(None)
    return credentials

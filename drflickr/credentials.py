# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.file import readYaml

from drresult import Ok, Err, returns_result
import json
import os
import logging

logger = logging.getLogger(__name__)


@returns_result()
def getCredentials(creds_path, name):
    filename = os.path.join(creds_path, f'{name}.yaml')
    credentials = readYaml(filename)
    if (
        not credentials
        or 'key' not in credentials.unwrap()
        or 'secret' not in credentials.unwrap()
    ):
        logger.error(
            f'Provide {name} credentials as `key` and `secret` in file {filename}'
        )
        if credentials:
            logger.error(credentials.unwrap())
        else:
            logger.error(credentials.unwrap_err())
        return Err(RuntimeError())
    else:
        return credentials

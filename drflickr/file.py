# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drresult import Ok, Err, returns_result
import json
import yaml
import os
import logging

logger = logging.getLogger(__name__)


@returns_result(
    expects=[
        PermissionError,
        NotADirectoryError,
    ]
)
def mkdir(dirname):
    os.makedirs(dirname, exist_ok=True)
    return Ok(None)


@returns_result(
    expects=[
        FileNotFoundError,
        PermissionError,
        IsADirectoryError,
        json.JSONDecodeError,
        UnicodeDecodeError,
    ]
)
def readJson(filename):
    with open(filename) as f:
        return Ok(json.loads(f.read()))


@returns_result(
    expects=[
        FileNotFoundError,
        PermissionError,
        IsADirectoryError,
        json.JSONDecodeError,
        UnicodeDecodeError,
    ]
)
def writeJson(filename, content):
    with open(filename, 'w') as f:
        f.write(json.dumps(content))
    return Ok(None)


@returns_result(
    expects=[
        FileNotFoundError,
        PermissionError,
        IsADirectoryError,
        json.JSONDecodeError,
        UnicodeDecodeError,
    ]
)
def readYaml(filename):
    with open(filename) as f:
        return Ok(yaml.safe_load(f.read()))


@returns_result(
    expects=[
        FileNotFoundError,
        PermissionError,
        IsADirectoryError,
        json.JSONDecodeError,
        UnicodeDecodeError,
    ]
)
def writeYaml(filename, content):
    with open(filename, 'w') as f:
        f.write(yaml.safe_dump(content))
    return Ok(None)

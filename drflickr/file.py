# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from result import as_result
import json
import yaml
import os
import logging

logger = logging.getLogger(__name__)


@as_result(
    PermissionError,
    NotADirectoryError,
)
def mkdir(dirname):
    os.makedirs(dirname, exist_ok=True)
    return None


@as_result(
    FileNotFoundError,
    PermissionError,
    IsADirectoryError,
    json.JSONDecodeError,
    UnicodeDecodeError,
)
def readJson(filename):
    with open(filename) as f:
        return json.loads(f.read())


@as_result(
    FileNotFoundError,
    PermissionError,
    IsADirectoryError,
    json.JSONDecodeError,
    UnicodeDecodeError,
)
def writeJson(filename, content):
    with open(filename, 'w') as f:
        f.write(json.dumps(content))
    return None


@as_result(
    FileNotFoundError,
    PermissionError,
    IsADirectoryError,
    json.JSONDecodeError,
    UnicodeDecodeError,
)
def readYaml(filename):
    with open(filename) as f:
        return yaml.safe_load(f.read())


@as_result(
    FileNotFoundError,
    PermissionError,
    IsADirectoryError,
    json.JSONDecodeError,
    UnicodeDecodeError,
)
def writeYaml(filename, content):
    with open(filename, 'w') as f:
        f.write(yaml.safe_dump(content))
    return None

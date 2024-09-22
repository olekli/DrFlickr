# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from result import Ok, Err, Result, is_ok, is_err, returns_result
from mrjsonstore import JsonStore
import logging

logger = logging.getLogger(__name__)


class GroupInfo:
    def __init__(self, filename, api):
        self.group_names = JsonStore(filename)
        self.api = api

    def get(self, group_id):
        info = self.group_names.view().get(group_id, None)
        if info:
            return info
        else:
            with self.group_names() as group_names:
                result = self.api.getGroupInfo(group_id)
                if is_ok(result):
                    group_names[group_id] = result.ok_value
                    return result.ok_value
                else:
                    return {'name': group_id}

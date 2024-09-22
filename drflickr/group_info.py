# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from rust_result import Ok, Err, returns_result
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
                if result.is_ok():
                    group_names[group_id] = result.unwrap()
                    return result.unwrap()
                else:
                    return {'name': group_id}

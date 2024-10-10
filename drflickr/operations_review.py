# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import re
import json

from drflickr.group_info import GroupInfo


class OperationsReview:
    def __init__(self, group_info):
        self.group_info = GroupInfo(group_info)

    def __call__(self, operations):
        return [self.flatten(op) for op in operations]

    def visit(self, params):
        for index, item in enumerate(params):
            if isinstance(item, str):
                if bool(re.fullmatch(r'^[0-9]*@N[0-9][0-9]$', item)):
                    params[index] = f'{self.group_info.getName(item)} {item}'
            elif isinstance(item, dict):
                assert 'title' in item
                params[index] = item['title']
            elif isinstance(item, list):
                self.visit(item)

    def flatten(self, operation):
        flattened = json.loads(json.dumps(operation))
        self.visit(flattened['params'])
        return flattened

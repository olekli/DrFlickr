# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import hashlib
import json
import time
import logging

logger = logging.getLogger(__name__)


class ApplicatorGreylist:
    def __init__(self, greylist, config):
        self.greylist = greylist
        self.config = config

    def update(self, operation, result):
        key = self.makeKey(operation)
        if result.is_ok():
            if key in self.greylist:
                del self.greylist[key]
        else:
            self.greylist.setdefault(key, {'timeout': 0, 'attempts': []})
            self.greylist[key]['timeout'] = (
                time.time() + 60 * 60 * self.config['timeout']
            )
            self.greylist[key]['attempts'].append(
                {'operation': operation, 'error': str(result.unwrap_err())}
            )

    def __contains__(self, operation):
        key = self.makeKey(operation)
        return key in self.greylist and (
            len(self.greylist[key]['attempts']) >= self.config['max_attempts']
            or self.greylist[key]['timeout'] > time.time()
        )

    def to_dict(self):
        return self.greylist

    def visit(self, item):
        if isinstance(item, dict):
            assert 'id' in item
            id = item['id']
            item.clear()
            item['id'] = id
        elif isinstance(item, list):
            for i in item:
                self.visit(i)

    def makeKey(self, operation):
        key = json.loads(json.dumps(operation))
        self.visit(key['params'])
        return hashlib.md5(json.dumps(key, sort_keys=True).encode('utf-8')).hexdigest()

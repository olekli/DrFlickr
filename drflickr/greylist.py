# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import logging
import time

logger = logging.getLogger(__name__)


class Greylist:
    def __init__(self, greylist, config):
        self.config = config
        self.greylist = greylist

        for key in self.config:
            if key not in greylist:
                self.greylist[key] = {}

    def to_dict(self):
        return self.greylist

    @classmethod
    def from_dict(cls, greylist_dict):
        return cls(greylist_dict)

    def add(self, type, id, reason=None):
        if not reason:
            reason = id
        until = time.time() + (self.config[type][reason] * 3600)
        if id in self.greylist[type] and self.greylist[type][id] > until:
            logger.info(f'{type} {id} already greylisted with longer timeout')
        else:
            self.greylist[type][id] = until
            logger.info(f'greylisting {type} {id}: {reason}')

    def has(self, type, id):
        if id in self.greylist[type]:
            if time.time() >= self.greylist[type][id]:
                del self.greylist[type][id]
            else:
                logger.debug(f'{type} greylisted: {id}')
                return True
        return False

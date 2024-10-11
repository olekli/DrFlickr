# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import logging

from drresult import noexcept

logger = logging.getLogger(__name__)


class GroupInfo:
    def __init__(self, group_info):
        self.group_info = group_info

    @noexcept()
    def isRestricted(self, group_id):
        return group_id not in self.group_info or self.group_info[group_id]['ispoolmoderated']

    @noexcept()
    def getName(self, group_id):
        return self.group_info[group_id]['name']

    @noexcept()
    def hasPhotoLimit(self, group_id):
        group = self.group_info[group_id]
        return (
            'throttle' in group
            and 'remaining' in group['throttle']
            and group['throttle']['remaining'] <= 0
        )

    @noexcept()
    def reduceRemaining(self, group_id):
        group = self.group_info[group_id]
        if 'throttle' in group and 'remaining' in group['throttle']:
            group['throttle']['remaining'] -= 1

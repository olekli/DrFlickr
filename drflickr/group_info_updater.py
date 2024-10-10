# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import time
from typing import List

from drresult import noexcept

logger = logging.getLogger(__name__)


class GroupInfoUpdater:
    def __init__(self, api):
        self.api = api

    @noexcept()
    def __call__(self, group_info: dict, group_list: List[str]) -> dict:
        group_info = dict(group_info)
        for group_id in [g for g in group_list if g not in group_info]:
            group_info[group_id] = {'name': group_id, 'last_update': 0}
        for group_id in group_info:
            if (group_info[group_id]['last_update'] + 24 * 60 * 60) < time.time():
                result = self.api.getGroupInfo(group_id)
                if result:
                    group_info[group_id] = {
                        **result.unwrap(),
                        'last_update': time.time(),
                    }
        return group_info

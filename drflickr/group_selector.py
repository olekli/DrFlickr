# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import time
import random
import logging

logger = logging.getLogger(__name__)


class GroupSelector:
    def __init__(self):
        self.rng = random.Random(time.time())

    def __call__(self, photo, eligible_groups, group_info, initial_burst, switch_phase):
        eligible_groups.sort(key=lambda p: p['tier'])
        logger.debug(f'sorted eligible_groups: {eligible_groups}')
        if len(photo['groups']) == 0:
            eligible_groups = [
                group
                for group in eligible_groups
                if not group_info.isRestricted(group['id']) and group['tier'] < 3
            ]
            num_to_select = initial_burst
        elif len(photo['groups']) < switch_phase:
            eligible_groups = [group for group in eligible_groups if group['tier'] < 4]
            num_to_select = 1
        else:
            eligible_groups = [group for group in eligible_groups if group['tier'] > 2]
            num_to_select = 1

        result = eligible_groups[:1]
        eligible_groups = eligible_groups[1:]
        num_to_select -= 1
        while num_to_select > 0:
            result += self.getUnlike(eligible_groups, result)
            eligible_groups = eligible_groups[1:]
            num_to_select -= 1
        return result

    def getUnlike(self, available, selected):
        selected_tags = set([tag for s in selected for tag in s['tags']])
        result = [
            {
                'intersection': len(
                    selected_tags.intersection(set(group['tags']['require']))
                ),
                'group': group,
            }
            for group in available
        ]
        result.sort(key=lambda g: g['intersection'])
        return [r['group'] for r in result][:1]

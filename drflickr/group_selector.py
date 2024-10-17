# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import time
import json
import logging

logger = logging.getLogger(__name__)


class GroupSelector:
    def __init__(self, config):
        self.config = config

    def __call__(self, photo, eligible_groups, group_info):
        eligible_groups = json.loads(json.dumps(eligible_groups))
        photo_tags = set(photo['tags'])
        for group in eligible_groups:
            group_tags = set(group['tags']['require'])
            group['match'] = len(photo_tags.intersection(group_tags)) + 2 - group['tier']
        eligible_groups.sort(key=lambda group: group['match'], reverse=True)
        logger.debug(f'sorted eligible_groups: {eligible_groups}')
        if len(photo['groups']) == 0:
            eligible_groups = [
                group
                for group in eligible_groups
                if not group_info.isRestricted(group['id']) and group['tier'] <= self.config['initial_burst']['min_tier']
            ]
            num_to_select = self.config['initial_burst']['num_photos']
        elif len(photo['groups']) < self.config['switch_phase']['num_required_groups'] or self.config['switch_phase']['curated_tag'] in photo['tags']:
            eligible_groups = [group for group in eligible_groups if group['tier'] <= self.config['switch_phase']['min_tier']]
            num_to_select = 1
        else:
            eligible_groups = [group for group in eligible_groups if group['tier'] >= self.config['dump_phase']['max_tier']]
            num_to_select = 1

        if num_to_select > 1:
            num_to_select -= 1
            unlike = True
        else:
            unlike = False
        result = eligible_groups[:num_to_select]
        eligible_groups = eligible_groups[num_to_select:]
        if unlike:
            result += self.getUnlike(eligible_groups, result)
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

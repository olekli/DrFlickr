# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import json
import logging

logger = logging.getLogger(__name__)


class BlacklistUpdater:
    def __init__(self):
        pass

    def __call__(self, photo_id, submitted_groups, actual_groups, blacklist):
        blacklist = json.loads(json.dumps(blacklist))
        submitted_groups = set(submitted_groups)
        actual_groups = set(actual_groups)
        blacklist.setdefault(photo_id, {})
        blacklist_entry = blacklist[photo_id]
        blacklist_entry.setdefault('blocked', [])
        blacklist_entry.setdefault('manually_added', [])
        blacklist_entry['blocked'] = list(
            set(blacklist_entry['blocked']).union(
                submitted_groups.difference(actual_groups)
            )
        )
        blacklist_entry['manually_added'] = list(
            set(blacklist_entry['manually_added']).union(
                actual_groups.difference(submitted_groups)
            )
        )
        return blacklist

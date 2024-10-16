# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import logging
from drresult import constructs_as_result, returns_result
from mrjsonstore import JsonStore

logger = logging.getLogger(__name__)


@constructs_as_result
class Submissions:
    def __init__(self, filename, dry_run):
        self.submissions = JsonStore(filename, dry_run=dry_run).unwrap_or_raise()

    def _add(self, photo, group_id):
        self.submissions.content.setdefault(photo['id'], {})
        self.submissions.content[photo['id']][group_id] = True

    @returns_result
    def add(self, photo, group_id):
        with self.submissions.transaction() as t:
            self._add(photo, group_id)
        return t.result

    @returns_result
    def remove(self, photo, group_id):
        with self.submissions.transaction() as t:
            self.submissions.content.setdefault(photo['id'], {})
            del self.submissions.content[photo['id']][group_id]
        return t.result

    def isPhotoInGroup(self, photo, group_id):
        view = self.submissions.content
        return (photo['id'] in view) and view[photo['id']].get(group_id, False)

    def getGroups(self, photo):
        view = self.submissions.content
        view.setdefault(photo['id'], {})
        return [
            group for group in view[photo['id']] if view[photo['id']].get(group, False)
        ]

    def isEmpty(self):
        return len(self.submissions.content) == 0

# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import logging
from mrjsonstore import JsonStore

logger = logging.getLogger(__name__)


class Submissions:
    def __init__(self, filename, dry_run):
        self.submissions = JsonStore(filename, dry_run=dry_run)

    def _add(self, submissions, photo, group_id):
        submissions.setdefault(photo['id'], {})
        submissions[photo['id']][group_id] = True

    def add(self, photo, group_id):
        with self.submissions() as submissions:
            self._add(submissions, photo, group_id)

    def remove(self, photo, group_id):
        with self.submissions() as submissions:
            submissions.setdefault(photo['id'], {})
            del submissions[photo['id']][group_id]

    def isPhotoInGroup(self, photo, group_id):
        view = self.submissions.view()
        return (photo['id'] in view) and view[photo['id']].get(group_id, False)

    def getGroups(self, photo):
        view = self.submissions.view()
        view.setdefault(photo['id'], {})
        return [
            group for group in view[photo['id']] if view[photo['id']].get(group, False)
        ]

    def isEmpty(self):
        with self.submissions() as submissions:
            return submissions.len == 0

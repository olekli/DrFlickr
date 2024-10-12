# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drresult import Ok, Err, returns_result
from collections import namedtuple

from drflickr.blacklist_updater import BlacklistUpdater

import json
import logging

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, api, submissions):
        self.api = api
        self.submissions = submissions
        self.blacklist_updater = BlacklistUpdater()

    @returns_result()
    def __call__(self, blacklist):
        blacklist = json.loads(json.dumps(blacklist))
        photos_actual = self.api.getPhotos(
            sort='interestingness-desc'
        ).unwrap_or_return()
        for photo in photos_actual.values():
            blacklist = self.blacklist_updater(
                photo_id=photo['id'],
                submitted_groups=self.submissions.getGroups(photo),
                actual_groups=photo['groups'],
                blacklist=blacklist
            )
            photo['groups'] = self.submissions.getGroups(photo)
            photo['sets'] = {}

        photosets = self.api.getPhotosets().unwrap_or_return()
        for name, id in photosets.items():
            photoset_photos = self.api.getPhotoset(id).unwrap_or_return()
            for index, photo_id in enumerate(photoset_photos):
                photos_actual[photo_id]['sets'][name] = index

        return Ok(
            namedtuple('RetrieverResult', ['photos_actual', 'photosets_map', 'blacklist'])(
                photos_actual, photosets, blacklist
            )
        )

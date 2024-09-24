# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drresult import Ok, Err, returns_result
from collections import namedtuple
import json
import logging

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, api, submissions):
        self.api = api
        self.submissions = submissions

    @returns_result()
    def __call__(self):
        photos_actual = self.api.getPhotos(
            sort='interestingness-desc'
        ).unwrap_or_return()
        for photo in photos_actual.values():
            photo['groups'] = self.submissions.getGroups(photo)
            photo['sets'] = {}

        photosets = self.api.getPhotosets().unwrap_or_return()
        for name, id in photosets.items():
            photoset_photos = self.api.getPhotoset(id).unwrap_or_return()
            for index, photo_id in enumerate(photoset_photos):
                photos_actual[photo_id]['sets'][name] = index

        return Ok(
            namedtuple('RetrieverResult', ['photos_actual', 'photosets_map'])(
                photos_actual, photosets
            )
        )

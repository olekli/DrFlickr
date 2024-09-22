# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.list_ordering import orderPhotos

import time


class Reorderer:
    def __init__(self, config):
        self.cutoff_ts = time.time() - (
            config['days_until_being_ordered'] * 24 * 60 * 60
        )

    def __call__(self, photos_actual, photos_expected):
        reference_order = [
            photos_expected[photo_id]
            for photo_id in photos_actual.keys()
            if photo_id in photos_expected
        ]
        photos = [
            photo for photo in reference_order if photo['date_posted'] < self.cutoff_ts
        ]

        ordered_by_time = sorted(
            photos, key=lambda photo: photo['date_posted'], reverse=True
        )

        if photos:
            orderPhotos(
                photos, self.cutoff_ts, ordered_by_time[-1]['date_posted'] - 60 * 60
            )

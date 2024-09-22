# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.photoset import getPhotosetAsOrderedList

import time
import logging

logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self, stats, config):
        self.stats = stats
        self.config = config

    def __call__(self, photos, greylist):
        if (
            time.localtime(time.time()).tm_hour >= self.config['time_window_start']
            and time.localtime(time.time()).tm_hour <= self.config['time_window_end']
            and not greylist.has('publish', 'published')
            and self.stats.viewsBelowEma()
        ):
            logger.info(f'criteria for publish fulfilled')
            queue_album = self.config['queue_album']
            showcase_album = self.config['showcase_album']
            queue = getPhotosetAsOrderedList(photos, queue_album)
            if len(queue) > 0:
                greylist.add('publish', 'published')
                photo_to_publish = queue[0]
                photo_to_publish['date_posted'] = int(time.time())
                photo_to_publish['date_taken'] = photo_to_publish['date_posted']
                del photo_to_publish['sets'][queue_album]
                queue = getPhotosetAsOrderedList(photos, queue_album)
                self.updatePhotoset(queue, queue_album)

                showcase = getPhotosetAsOrderedList(photos, showcase_album)
                showcase.insert(0, photo_to_publish)
                self.updatePhotoset(showcase, showcase_album)

                photo_to_publish['is_public'] = True
            else:
                logger.info(f'no photos queued for publication')

    def updatePhotoset(self, photoset, set_name):
        for index, photo in enumerate(photoset):
            photo['sets'][set_name] = index

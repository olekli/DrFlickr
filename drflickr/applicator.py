# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.applicator_greylist import ApplicatorGreylist
from drflickr.photoset import getPhotosetAsOrderedList
from drflickr.api import ApiError, NetworkError
from drflickr.group_info import GroupInfo

from drresult import Ok, Err, returns_result
from collections import namedtuple
import json
import time
import logging
import random

logger = logging.getLogger(__name__)


class Applicator:
    methods = [
        "addPhotoToGroup",
        "removePhotoFromGroup",
        "publishPhoto",
        "updatePhotoDates",
        "addPhotoToSet",
        "removePhotoFromSet",
    ]

    def __init__(self, api, submissions, group_info, config):
        self.api = api
        self.submissions = submissions
        self.group_info = GroupInfo(group_info)
        self.config = config

    def __call__(self, operations, photosets, greylist):
        self.photosets = photosets
        greylist = ApplicatorGreylist(
            json.loads(json.dumps(greylist)), self.config["greylist"]
        )
        applied = []
        for op in operations:
            if op["method"] in Applicator.methods:
                if not op in greylist:
                    result = getattr(self, op["method"])(*op["params"])
                    greylist.update(op, result)
                    applied.append(result.is_ok())
                    time.sleep(
                        random.uniform(
                            self.config['throttle']['min_ms'],
                            self.config['throttle']['max_ms'],
                        )
                        / 1000.0
                    )
        return namedtuple("ApplicatorResult", ["result", "greylist"])(
            all(applied), greylist.to_dict()
        )

    def addPhotoToGroup(self, photo, group_id):
        logger.info(f'Adding photo {photo["title"]} to group {group_id}')
        result = self.api.addPhotoToGroup(photo, group_id)
        if result.is_ok():
            # photo was added successfully
            self.submissions.add(photo, group_id)
            return result
        else:
            result = result.unwrap_err()
            if isinstance(result, ApiError):
                if result.code == 3:
                    # already in pool
                    logger.info(
                        f'{photo["title"]}: group {self.group_info.getName(group_id)} has photo already in pool'
                    )
                    self.submissions.add(photo, group_id)
                    return Ok(result)
                elif result.code == 4:
                    # already in max pools
                    logger.info(f'{photo["title"]}: already in max pools')
                    self.submissions.add(photo, group_id)
                    return Ok(result)
                elif result.code == 5:
                    # photo limit
                    logger.info(
                        f'group {self.group_info.getName(group_id)} photo limit hit'
                    )
                    assert False, "Should not happen anymore"
                elif (result.code == 6) or (result.code == 7):
                    # photo already in pending
                    # in case this entry was missed in submissions, add it now
                    logger.info(
                        f'{photo["title"]}: group {self.group_info.getName(group_id)} has photo in pending'
                    )
                    self.submissions.add(photo, group_id)
                    return Ok(result)
                else:
                    logger.warning(
                        f'adding {photo["title"]} to {self.group_info.getName(group_id)}: {result}'
                    )
                    return Err(result)
            else:
                logger.warning(
                    f'adding {photo["title"]} to {self.group_info.getName(group_id)}: {result}'
                )
                return Err(result)
        assert False

    def removePhotoFromGroup(self, photo, group_id):
        logger.info(f'Removing photo {photo["title"]} from group {group_id}')
        result = self.api.removePhotoFromGroup(photo, group_id)
        if result.is_ok():
            self.submissions.remove(photo, group_id)
        else:
            result = result.unwrap_err()
            if isinstance(result, ApiError):
                if result.code == 2:
                    # Photo already removed from pool
                    self.submissions.remove(photo, group_id)
                    return Ok(result)
        return result

    def publishPhoto(self, photo):
        logger.info(f'Publishing new photo: {photo["title"]}')
        return self.api.publishPhoto(photo)

    def updatePhotoDates(self, photo):
        logger.info(f'Updating photo dates: {photo["title"]}')
        return self.api.updatePhotoDates(photo)

    def addPhotoToSet(self, photo, set_name):
        logger.info(f'Adding photo {photo["title"]} to set {set_name}')
        return self.api.addPhotoToSet(photo, self.photosets[set_name])

    def removePhotoFromSet(self, photo, set_name):
        logger.info(f'Removing photo {photo["title"]} from set {set_name}')
        return self.api.removePhotoFromSet(photo, self.photosets[set_name])

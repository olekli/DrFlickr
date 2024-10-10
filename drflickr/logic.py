# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.greylist import Greylist
from drflickr.group_info import GroupInfo
from drflickr.group_checker import GroupChecker
from drflickr.publisher import Publisher
from drflickr.reorderer import Reorderer
from drflickr.reconciler import Reconciler

from collections import namedtuple
import json
import logging

logger = logging.getLogger(__name__)


class Logic:
    def __init__(self, views_groups, favorites_groups, tag_groups, stats, config):
        self.views_groups = views_groups
        self.favorites_groups = favorites_groups
        self.tag_groups = tag_groups
        self.stats = stats
        self.config = config

        self.group_checker = GroupChecker(
            self.tag_groups,
            self.views_groups,
            self.favorites_groups,
            self.config['group_checker'],
        )
        self.publisher = Publisher(self.stats, config['publisher'])
        self.reorderer = Reorderer(config['reorderer'])
        self.reconciler = Reconciler()

    def __call__(self, photos_actual, photos_expected, greylist, group_info):
        photos_expected = json.loads(json.dumps(photos_expected))
        greylist = Greylist(json.loads(json.dumps(greylist)), self.config['greylist'])
        group_info = GroupInfo(json.loads(json.dumps(group_info)))

        photos_actual = {
            id: photo
            for id, photo in photos_actual.items()
            if self.config['managed_album'] in photo['sets']
        }

        for id in photos_actual:
            if id not in photos_expected:
                photos_expected[id] = json.loads(json.dumps(photos_actual[id]))

        to_delete = [id for id in photos_expected if id not in photos_actual]
        for id in to_delete:
            del photos_expected[id]

        for id in photos_expected:
            photos_expected[id]['tags'] = list(photos_actual[id]['tags'])
            photos_expected[id]['views'] = photos_actual[id]['views']
            photos_expected[id]['faves'] = photos_actual[id]['faves']
            if not photos_expected[id]['is_public']:
                photos_expected[id]['is_public'] = photos_actual[id]['is_public']
                photos_expected[id]['sets'] = dict(photos_actual[id]['sets'])
            else:
                queue_album = self.config['publisher']['queue_album']
                for set_name in photos_actual[id]['sets']:
                    if (
                        set_name != queue_album
                        and set_name not in photos_expected[id]['sets']
                    ):
                        photos_expected[id]['sets'][set_name] = photos_actual[id][
                            'sets'
                        ][set_name]
                to_delete = []
                for set_name in photos_expected[id]['sets']:
                    if (
                        set_name != queue_album
                        and set_name not in photos_actual[id]['sets']
                    ):
                        to_delete.append(set_name)

                for set_name in to_delete:
                    del photos_expected[id]['sets'][set_name]

        logger.info(
            f'Managing photos: {[photo["title"] for photo in photos_expected.values()]}'
        )
        photos_expected_public = {
            photo_id: photo
            for photo_id, photo in photos_expected.items()
            if photo['is_public']
        }
        for photo in photos_expected_public.values():
            self.group_checker(photo, greylist, group_info)
        self.publisher(photos_expected.values(), greylist)
        if self.config['reorderer']['enabled'] and not greylist.has(
            'ordering', 'photos_ordered'
        ):
            self.reorderer(photos_actual, photos_expected_public)
            greylist.add('ordering', 'photos_ordered')

        operations = self.reconciler(photos_actual, photos_expected)

        return namedtuple(
            'LogicResult', ['photos_expected', 'greylist', 'group_info', 'operations']
        )(photos_expected, greylist.greylist, group_info.group_info, operations)

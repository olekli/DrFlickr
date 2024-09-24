# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.photoset import getPhotosetAsOrderedList
import logging

logger = logging.getLogger(__name__)


class Reconciler:
    def __init__(self):
        pass

    def __call__(self, photos_actual, photos_expected):
        operations = []
        for photo_expected in photos_expected.values():
            photo_actual = photos_actual[photo_expected['id']]
            groups_to_add = [
                group
                for group in photo_expected['groups']
                if group not in photo_actual['groups']
            ]
            groups_to_remove = [
                group
                for group in photo_actual['groups']
                if group not in photo_expected['groups']
            ]

            for group in groups_to_add:
                operations.append(
                    {'method': 'addPhotoToGroup', 'params': [photo_expected, group]}
                )

            for group in groups_to_remove:
                operations.append(
                    {
                        'method': 'removePhotoFromGroup',
                        'params': [photo_expected, group],
                    }
                )

            if (photo_expected['date_posted'] != photo_actual['date_posted']) or (
                photo_expected['date_taken'] != photo_actual['date_taken']
            ):
                operations.append(
                    {'method': 'updatePhotoDates', 'params': [photo_expected]}
                )

            if photo_expected['is_public'] and not photo_actual['is_public']:
                operations.append(
                    {'method': 'publishPhoto', 'params': [photo_expected]}
                )

            sets_list_expected = [set_name for set_name in photo_expected['sets']]
            sets_list_actual = [set_name for set_name in photo_actual['sets']]
            sets_to_add = [
                set_name
                for set_name in sets_list_expected
                if set_name not in sets_list_actual
            ]
            sets_to_remove = [
                set_name
                for set_name in sets_list_actual
                if set_name not in sets_list_expected
            ]
            for set_name in sets_to_add:
                operations.append(
                    {'method': 'addPhotoToSet', 'params': [photo_expected, set_name]}
                )
            for set_name in sets_to_remove:
                operations.append(
                    {
                        'method': 'removePhotoFromSet',
                        'params': [photo_expected, set_name],
                    }
                )

        return operations

# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0


def getPhotosetAsOrderedList(photos, set_name):
    return sorted(
        [photo for photo in photos if set_name in photo['sets']],
        key=lambda photo: photo['sets'][set_name],
    )

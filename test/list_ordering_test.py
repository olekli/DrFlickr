# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.list_ordering import getOutOfOrderIndices, orderPhotos

import pytest

test_data_getOutOfOrderIndices = [
    ([], []),
    ([0], []),
    ([20], []),
    ([10, 0], []),
    ([40, 30], []),
    ([30, 20, 10], []),
    ([90, 80, 40], []),
    ([0, 10], [1]),
    ([20, 30], [1]),
    ([20, 50], [1]),
    ([40, 50, 20, 10], [1]),
    ([40, 50, 20, 0], [1]),
    ([10, 60, 50, 40, 20, 30, 0], [0, 5])
]

@pytest.mark.parametrize("input, expected", test_data_getOutOfOrderIndices)
def test_getOutOfOrderIndices(input, expected):
    assert getOutOfOrderIndices(input) == expected

test_data_orderPhotos = [
    ([]),
    ([30]),
    ([30, 50]),
    ([50, 30]),
    ([30, 60, 50, 40, 20, 30, 120]),
    ([20, 60, 50, 40, 20, 30, 170]),
    ([20, 60, 50, 40, 20, 30, 30]),
]

@pytest.mark.parametrize("input", test_data_orderPhotos)
def test_getOutOfOrderIndices(input):
    photos = [
        { 'id': index, 'date_posted': date_posted }
        for index, date_posted in enumerate(input)
    ]
    id_order_expected = [photo['id'] for photo in photos]
    orderPhotos(photos, 300, 1)
    id_order_actual = [photo['id'] for photo in photos[1:-1]]
    assert id_order_actual == id_order_expected

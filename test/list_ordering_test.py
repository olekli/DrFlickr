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
    ([10, 60, 50, 40, 20, 30, 0], [0, 5]),
    ([1, 6, 5, 4, 2, 3, 0], [0, 5]),
    ([5, 5, 5, 5], []),
    ([6, 5, 4, 3, 3, 1, 1], []),
    ([6, 5, 5, 3, 3, 4, 1, 1], [5]),
]


@pytest.mark.parametrize("input, expected", test_data_getOutOfOrderIndices)
def test_getOutOfOrderIndices(input, expected):
    assert getOutOfOrderIndices(input) == expected


test_data_orderPhotos = [
    ([], 300, 1),
    ([30], 300, 1),
    ([30, 50], 300, 1),
    ([50, 30], 300, 1),
    ([30, 60, 50, 40, 20, 30, 120], 300, 1),
    ([20, 60, 50, 40, 20, 30, 170], 300, 1),
    ([20, 60, 50, 40, 20, 30, 30], 300, 1),
    ([20, 60, 50, 40, 30], 300, 1),
    ([1722586950, 1722582014, 1722566383, 1722565805, 1722565228, 1722564650, 1722564361, 1722564073, 1722559896, 1722454143, 1722559106,
        1722519871, 1722480637, 1722471356, 1722470195, 1722469035, 1722432712, 1722463561, 1722450684, 1722447225, 1722433050, 1722432375,
        1722431700, 1721983162, 1722429000, 1722426300, 1722337200, 1722294000, 1722250800, 1722191400, 1722112087, 1722032775, 1722018600,
        1721985525, 1721980800, 1721962575, 1721944350, 1721907900, 1721902879, 1721897859, 1721897669, 1721895756, 1721895084, 1721894412,
        1721894410, 1721894409, 1721881112, 1721894408, 1721894407, 1721894402, 1721839249, 1721839221, 1721839193, 1721839165, 1721839138,
        1721735100, 1721730037, 1721702924, 1721675812, 1721655000, 1721627043, 1721620054, 1721613065, 1721605959, 1721598737, 1721598679,
        1721598621, 1721596975, 1721594753, 1721590874, 1721590853, 1721590846, 1721590818, 1721590706, 1733646036, 1721589806, 1721588906],
        1733750578.4129267, 1721585306),
]

@pytest.mark.parametrize("input, window_begin, window_end", test_data_orderPhotos)
def test_orderPhotos(input, window_begin, window_end):
    photos = [
        {'id': index, 'date_posted': date_posted}
        for index, date_posted in enumerate(input)
    ]
    id_order_expected = [photo['id'] for photo in photos]
    orderPhotos(photos, window_begin, window_end)
    photos.sort(key=lambda x: x['date_posted'], reverse=True)
    id_order_actual = [photo['id'] for photo in photos[1:-1]]
    assert id_order_actual == id_order_expected

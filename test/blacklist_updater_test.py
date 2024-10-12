# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.blacklist_updater import BlacklistUpdater

import pytest

test_data = [
    (
        ('p1', [], [], {}),
        {'p1': {'blocked': [], 'manually_added': []}}
    ),
    (
        ('p1', [], [], {'p1': {'blocked': [], 'manually_added': []}}),
        {'p1': {'blocked': [], 'manually_added': []}}
    ),
    (
        ('p1', [], [], {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}),
        {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}
    ),
    (
        ('p1', ['g3'], ['g3'], {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}),
        {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}
    ),
    (
        ('p1', ['g3','g4','g5'], ['g3','g4','g5'], {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}),
        {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}
    ),
    (
        ('p1', ['g3','g4','g5'], ['g3','g5','g4'], {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}),
        {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}
    ),
    (
        ('p1', [], ['g3'], {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}),
        {'p1': {'blocked': ['g1'], 'manually_added': ['g2','g3']}}
    ),
    (
        ('p1', ['g4'], ['g3', 'g4'], {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}),
        {'p1': {'blocked': ['g1'], 'manually_added': ['g2','g3']}}
    ),
    (
        ('p1', ['g4'], [], {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}),
        {'p1': {'blocked': ['g1','g4'], 'manually_added': ['g2']}}
    ),
    (
        ('p1', ['g4','g3'], ['g3'], {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}),
        {'p1': {'blocked': ['g1','g4'], 'manually_added': ['g2']}}
    ),
    (
        ('p1', ['g3','g5'], ['g5','g4'], {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}),
        {'p1': {'blocked': ['g1','g3'], 'manually_added': ['g2','g4']}}
    ),
    (
        ('p1', ['g3','g5','g6'], ['g5','g7','g4'], {'p1': {'blocked': ['g1'], 'manually_added': ['g2']}}),
        {'p1': {'blocked': ['g1','g3','g6'], 'manually_added': ['g2','g4','g7']}}
    ),
    (
        ('p1', ['g3','g5','g6'], ['g5','g7','g4'], {'p2': {'blocked': ['g1'], 'manually_added': ['g2']}}),
        {'p1': {'blocked': ['g3','g6'], 'manually_added': ['g4','g7']}, 'p2': {'blocked': ['g1'], 'manually_added': ['g2']}}
    ),
]

@pytest.mark.parametrize("input, expected", test_data)
def test_blacklist_updater(input, expected):
    actual = BlacklistUpdater().__call__(*input)
    for i in actual:
        actual[i]['blocked'].sort()
        actual[i]['manually_added'].sort()
    for i in expected:
        expected[i]['blocked'].sort()
        expected[i]['manually_added'].sort()
    assert actual == expected

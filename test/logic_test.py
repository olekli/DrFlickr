# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.logic import Logic
from deepdiff import DeepDiff
import json
import time

tag_groups = {
    'group-1': {'id': 'group-1', 'tier': 2, 'tags': {'require': ['photography']}},
    'group-2': {'id': 'group-1', 'tier': 2, 'tags': {'require': ['photography']}},
    'street-group-1': {
        'id': 'street-group-1',
        'tier': 2,
        'tags': {'require': ['streetphotography']},
    },
    'street-group-2': {
        'id': 'street-group-2',
        'tier': 2,
        'tags': {'require': ['streetphotography']},
    },
    'street-group-3': {
        'id': 'street-group-3',
        'tier': 2,
        'tags': {'require': ['streetphotography']},
    },
    'mono-group-1': {
        'id': 'mono-group-1',
        'tier': 2,
        'tags': {
            'require': [
                'streetphotography',
                'monochrome',
            ]
        },
    },
    'mono-group-2': {
        'id': 'mono-group-2',
        'tier': 2,
        'tags': {
            'require': [
                'streetphotography',
                'monochrome',
            ]
        },
    },
    'mono-group-3': {
        'id': 'mono-group-3',
        'tier': 2,
        'tags': {
            'require': [
                'streetphotography',
                'monochrome',
            ]
        },
    },
}

group_info = {
    'mono-group-1': {
        'name': 'mono-group-1',
        'ispoolmoderated': False,
        'invitation_only': False,
    },
    'mono-group-2': {
        'name': 'mono-group-2',
        'ispoolmoderated': False,
        'invitation_only': False,
    },
    'mono-group-3': {
        'name': 'mono-group-3',
        'ispoolmoderated': False,
        'invitation_only': False,
    },
    'street-group-1': {
        'name': 'street-group-1',
        'ispoolmoderated': False,
        'invitation_only': False,
    },
    'street-group-2': {
        'name': 'street-group-2',
        'ispoolmoderated': False,
        'invitation_only': False,
    },
    'street-group-3': {
        'name': 'street-group-3',
        'ispoolmoderated': False,
        'invitation_only': False,
    },
    'group-1': {'name': 'group-1', 'ispoolmoderated': False, 'invitation_only': False},
    'group-2': {'name': 'group-2', 'ispoolmoderated': False, 'invitation_only': False},
    'group-3': {'name': 'group-3', 'ispoolmoderated': False, 'invitation_only': False},
}

views_groups = [
    {'name': 'Views: 100', 'nsid': 'views-100', 'ge': 100, 'less': 200},
    {'name': 'Views: 200', 'nsid': 'views-200', 'ge': 200, 'less': 300},
    {'name': 'Views: 300', 'nsid': 'views-300', 'ge': 300, 'less': 1000},
]

favorites_groups = [
    {'name': 'Faves: 10', 'nsid': 'faves-100', 'ge': 10, 'less': 20},
    {'name': 'Faves: 20', 'nsid': 'faves-20', 'ge': 20, 'less': 30},
    {'name': 'Faves: 30', 'nsid': 'faves-30', 'ge': 30, 'less': 100},
]

config_logic = {
    'managed_album': 'All',
    'group_checker': {
        'stats': {'required_tag': 'stats', 'delay': 0},
        'tags': {'initial_burst': 1, 'switch_phase': 10},
    },
    'publisher': {
        'queue_album': 'Queue',
        'showcase_album': 'Showcase',
        'time_window_start': 0,
        'time_window_end': 24,
    },
    'reorderer': {'days_until_being_ordered': 7, 'enabled': True},
    'greylist': {
        'group': {'photo_added': 16, 'photo_added_to_category': 1},
        'photo': {'added_to_group': 1, 'published': 6},
        'publish': {'published': 20, 'published10': 68, 'published15': 44},
        'ordering': {'photos_ordered': 24},
    },
}

blacklist = {
    'photo-1': { 'blocked': [], 'manually_added': [] },
    'photo-2': { 'blocked': [], 'manually_added': [] },
    'photo-3': { 'blocked': [], 'manually_added': [] },
}


class StatsDummy:
    def __init__(self, value):
        self.value = value

    def viewsBelowEma(self):
        return self.value


def make_logic(stats_value=True, publish=True, reorder=True):
    config = json.loads(json.dumps(config_logic))
    if not publish:
        config['publisher']['time_window_start'] = 3
        config['publisher']['time_window_end'] = 2
    if not reorder:
        config['reorderer']['enabled'] = False
    return Logic(
        views_groups=views_groups,
        favorites_groups=favorites_groups,
        tag_groups=tag_groups,
        stats=StatsDummy(stats_value),
        config=config,
    )


def test_empty_input():
    logic = make_logic()
    greylist = {}
    photos_actual = {}
    photos_expected = {}
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 0
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_1():
    # Nothing managed, nothing published, nothing in queue, nothing in expected
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {},
            'is_public': False,
        },
    }
    photos_expected = {}
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 0
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_2():
    # Some managed, nothing published, nothing in queue, nothing in expected
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {}
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 2
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_3():
    # Some managed, nothing published, nothing in queue, expected is up-to-date
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 2
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_4():
    # Some managed, nothing published, nothing in queue
    # Unmanaged are removed
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 0},
            'is_public': False,
        },
    }
    photos_expected = {}
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 1
    assert result.photos_expected == {'photo-3': photos_actual['photo-3']}
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_5():
    # Some managed, nothing published, nothing in queue
    # Adding sets to non-published propagates
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {'All': 2},
            'is_public': False,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': photos_actual['photo-2'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_5_():
    # Some managed, nothing published, nothing in queue
    # Adding protected sets to non-published propagates
    logic = make_logic(publish=False)
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {'All': 2, 'Queue': 0},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {'All': 2},
            'is_public': False,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': photos_actual['photo-2'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_6_():
    # Some managed, nothing published, nothing in queue
    # Removing protected sets from non-published propagates
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {'All': 2},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {'All': 2, 'Queue': 0},
            'is_public': False,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': photos_actual['photo-2'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_6():
    # Some managed, nothing published, nothing in queue
    # Removing sets from non-published propagates
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {'All': 2},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': False,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': photos_actual['photo-2'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_7():
    # Some managed, nothing published, nothing in queue
    # Adding tags to non-published propagates
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome', 'awesome'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': False,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': photos_actual['photo-2'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_8():
    # Some managed, nothing published, nothing in queue
    # Removing tags from non-published propagates
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['streetphotography', 'monochrome'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography', 'monochrome'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': False,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': photos_actual['photo-2'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_9():
    # Some managed, some published, nothing in queue
    # Adding protected sets to published photo is ignored
    logic = make_logic(publish=False)
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2, 'Queue': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2},
            'is_public': True,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == photos_expected
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 1
    assert result.operations[0]['method'] == 'removePhotoFromSet'


def test_case_10():
    # Some managed, some published, nothing in queue
    # Adding protected sets to published photo is ignored
    # Even if public is not actual yet
    logic = make_logic(publish=False)
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2, 'Queue': 0},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2},
            'is_public': True,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == photos_expected
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 2
    assert result.operations[0]['method'] == 'publishPhoto'
    assert result.operations[1]['method'] == 'removePhotoFromSet'


def test_case_11():
    # Some managed, some published, nothing in queue
    # Removing protected sets from published photo is ignored
    logic = make_logic(publish=False)
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2, 'Queue': 0},
            'is_public': True,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == photos_expected
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 1
    assert result.operations[0]['method'] == 'addPhotoToSet'


def test_case_12():
    # Some managed, some published, nothing in queue
    # Removing protected sets from published photo is ignored
    # Even if public is not actual yet
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2, 'Queue': 0},
            'is_public': True,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == photos_expected
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 1
    assert result.operations[0]['method'] == 'publishPhoto'


def test_case_9_():
    # Some managed, some published, nothing in queue
    # Adding non-protected sets to published photo propagates
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2},
            'is_public': True,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': photos_actual['photo-2'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_10_():
    # Some managed, some published, nothing in queue
    # Adding non-protected sets to published photo propagates
    # Even if public is not actual yet
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2},
            'is_public': True,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 1
    assert result.operations[0]['method'] == 'publishPhoto'


def test_case_11_():
    # Some managed, some published, nothing in queue
    # Removing non-protected sets from published photo propagates
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': photos_actual['photo-2'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_12():
    # Some managed, some published, nothing in queue
    # Removing non-protected sets from published photo propagates
    # Even if public is not actual yet
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2},
            'is_public': True,
        },
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 1
    assert result.operations[0]['method'] == 'publishPhoto'


def test_case_13():
    # Some managed, some published, nothing in queue
    # Adding tags to published propagates
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_', 'awesome'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': photos_actual['photo-2'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_14():
    # Some managed, some published, nothing in queue
    # Removing tags from non-published propagates
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['street_', 'monochrome_'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography_', 'street_', 'monochrome_'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': photos_actual['photo-2'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_15():
    # Some managed, nothing in queue
    # Public propagates from actual
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['street_', 'monochrome_'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['street_', 'monochrome_'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': False,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': photos_actual['photo-2'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_16():
    # Some managed, some in queue
    # Queued photo gets published
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['street_', 'monochrome_'],
            'sets': {'All': 2, 'Queue': 0},
            'is_public': False,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1, 'Queue': 1},
            'is_public': False,
        },
    }
    photos_expected = {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['street_', 'monochrome_'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': False,
        },
        'photo-3': photos_actual['photo-3'],
    }
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected['photo-1'] == photos_actual['photo-1']
    assert result.photos_expected['photo-3'] == photos_actual['photo-3']
    assert not DeepDiff(
        result.photos_expected['photo-2'],
        photos_actual['photo-2'],
        exclude_paths=[
            "root['is_public']",
            "root['date_taken']",
            "root['date_posted']",
            "root['sets']",
        ],
    )
    assert result.photos_expected['photo-2']['is_public'] == True
    assert result.photos_expected['photo-2']['sets'] == {'All': 2, 'Showcase': 0}
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 1
    assert 'photo-2' in result.greylist['photo']
    assert len(result.greylist['publish']) == 1
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 4
    publish_photo = next(
        op for op in result.operations if op['method'] == 'publishPhoto'
    )
    assert publish_photo['params'][0]['id'] == 'photo-2'
    update_photo_dates = (
        op for op in result.operations if op['method'] == 'publishPhoto'
    )
    for op in update_photo_dates:
        assert op['params'][0]['id'] == 'photo-2'
    add_photo_to_set = next(
        op for op in result.operations if op['method'] == 'addPhotoToSet'
    )
    assert add_photo_to_set['params'][0]['id'] == 'photo-2'
    assert add_photo_to_set['params'][1] == 'Showcase'
    remove_photo_from_set = next(
        op for op in result.operations if op['method'] == 'removePhotoFromSet'
    )
    assert remove_photo_from_set['params'][0]['id'] == 'photo-2'
    assert remove_photo_from_set['params'][1] == 'Queue'


def test_case_17():
    # Some published, legit groups are added
    logic = make_logic()
    greylist = {}
    now = time.time()
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [
                'streetphotography',
            ],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    result = logic(photos_actual, {}, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert len(result.photos_expected['photo-2']['groups']) == 1
    group_added = result.photos_expected['photo-2']['groups'][0]
    assert any(
        [
            'street-group-1' == group_added,
            'street-group-2' == group_added,
            'street-group-3' == group_added,
        ]
    )
    assert len(result.greylist['group']) == 1
    assert group_added in result.greylist['group']
    assert len(result.greylist['photo']) == 1
    assert 'photo-2' in result.greylist['photo']
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 1
    assert result.operations[0]['method'] == 'addPhotoToGroup'
    assert result.operations[0]['params'][0]['id'] == 'photo-2'
    assert result.operations[0]['params'][1] == group_added


def test_case_18():
    # Some published, legit groups are not removed, greylisted not added
    logic = make_logic()
    now = time.time()
    greylist = {'group': {'street-group-2': now + 1 * 24 * 60 * 60}}
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [
                'street-group-1',
                'street-group-3',
            ],
            'tags': [
                'streetphotography',
            ],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    result = logic(photos_actual, {}, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': photos_actual['photo-2'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 1
    assert 'street-group-2' in result.greylist['group']
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_19():
    # Some published, legit groups are not removed, greylisted not added
    # multiple tags
    logic = make_logic()
    now = time.time()
    greylist = {'group': {'street-group-2': now + 1 * 24 * 60 * 60}}
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [
                'street-group-1',
                'street-group-3',
            ],
            'tags': ['bar', 'streetphotography', 'foo', 'baz'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    result = logic(photos_actual, {}, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': photos_actual['photo-2'],
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 1
    assert 'street-group-2' in result.greylist['group']
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_20():
    # Some published, non-legit groups are removed
    logic = make_logic()
    now = time.time()
    greylist = {'group': {'street-group-2': now + 1 * 24 * 60 * 60}}
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography'],
            'sets': {'All': 0},
            'is_public': False,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [
                'street-group-1',
                'group-1',
                'street-group-3',
            ],
            'tags': ['bar', 'streetphotography', 'foo', 'baz'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['photography', 'streetphotography'],
            'sets': {'All': 1},
            'is_public': False,
        },
    }
    result = logic(photos_actual, {}, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == {
        'photo-1': photos_actual['photo-1'],
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [
                'street-group-1',
                'street-group-3',
            ],
            'tags': ['bar', 'streetphotography', 'foo', 'baz'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': photos_actual['photo-3'],
    }
    assert len(result.greylist['group']) == 1
    assert 'street-group-2' in result.greylist['group']
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 1
    assert result.operations[0]['method'] == 'removePhotoFromGroup'
    assert result.operations[0]['params'][0]['id'] == 'photo-2'
    assert result.operations[0]['params'][1] == 'group-1'


def test_case_21():
    # Does not reorder when correct ordering
    logic = make_logic()
    now = time.time()
    greylist = {}
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 0},
            'is_public': True,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 1},
            'is_public': True,
        },
    }
    result = logic(photos_actual, {}, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert result.photos_expected == photos_actual
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_21():
    # Does not reorder when incorrect ordering within grace period
    logic = make_logic()
    now = time.time()
    greylist = {}
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 2 * 24 * 60 * 60,
            'date_taken': now - 2 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 0},
            'is_public': True,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 1 * 24 * 60 * 60,
            'date_taken': now - 1 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 3 * 24 * 60 * 60,
            'date_taken': now - 3 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 1},
            'is_public': True,
        },
    }
    result = logic(photos_actual, {}, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 0


def test_case_21():
    # Does reorder when incorrect ordering outside grace period
    logic = make_logic()
    now = time.time()
    greylist = {}
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 12 * 24 * 60 * 60,
            'date_taken': now - 12 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 0},
            'is_public': True,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 11 * 24 * 60 * 60,
            'date_taken': now - 11 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 13 * 24 * 60 * 60,
            'date_taken': now - 13 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 1},
            'is_public': True,
        },
    }
    result = logic(photos_actual, {}, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 1
    assert 'photos_ordered' in result.greylist['ordering']
    assert len(result.operations) == 1
    assert result.operations[0]['method'] == 'updatePhotoDates'


def test_case_21():
    # Does not reorder when incorrect ordering outside grace period but disabled
    logic = make_logic(reorder=False)
    now = time.time()
    greylist = {}
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 12 * 24 * 60 * 60,
            'date_taken': now - 12 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 0},
            'is_public': True,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 11 * 24 * 60 * 60,
            'date_taken': now - 11 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 13 * 24 * 60 * 60,
            'date_taken': now - 13 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 1},
            'is_public': True,
        },
    }
    result = logic(photos_actual, {}, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert len(result.greylist['group']) == 0
    assert len(result.greylist['photo']) == 0
    assert len(result.greylist['publish']) == 0
    assert len(result.greylist['ordering']) == 0
    assert len(result.operations) == 0


def test_case_22():
    # Stats are updated correctly from actual
    logic = make_logic(reorder=False)
    now = time.time()
    greylist = {}
    photos_actual = {
        'photo-1': {
            'id': 'photo-1',
            'title': 'Photo 1',
            'date_posted': now - 12 * 24 * 60 * 60,
            'date_taken': now - 12 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 0},
            'is_public': True,
        },
        'photo-2': {
            'id': 'photo-2',
            'title': 'Photo 2',
            'date_posted': now - 11 * 24 * 60 * 60,
            'date_taken': now - 11 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': ['stats'],
            'sets': {'All': 2, 'Streets': 0},
            'is_public': True,
        },
        'photo-3': {
            'id': 'photo-3',
            'title': 'Photo 3',
            'date_posted': now - 13 * 24 * 60 * 60,
            'date_taken': now - 13 * 24 * 60 * 60,
            'faves': 0,
            'views': 0,
            'groups': [],
            'tags': [],
            'sets': {'All': 1},
            'is_public': True,
        },
    }
    result = logic(photos_actual, {}, greylist, group_info, blacklist)
    photos_expected = result.photos_expected
    assert photos_expected == photos_actual
    photos_actual['photo-2']['views'] = 153
    photos_actual['photo-2']['faves'] = 22
    result = logic(photos_actual, photos_expected, greylist, group_info, blacklist)
    assert len(result.photos_expected) == 3
    assert len(result.photos_expected['photo-2']['groups']) == 2
    assert 'views-100' in result.photos_expected['photo-2']['groups']
    assert 'faves-20' in result.photos_expected['photo-2']['groups']
    assert len(result.operations) == 2

# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.greylist import Greylist
from drflickr.group_checker import GroupChecker
from drflickr.group_info import GroupInfo

import time
import json

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
        'tags': {'require': ['streetphotography'], 'exclude': ['excluded']},
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

view_groups = [
    {'name': 'Views: 100', 'nsid': 'views-100', 'ge': 100, 'less': 200},
    {'name': 'Views: 200', 'nsid': 'views-200', 'ge': 200, 'less': 300},
    {'name': 'Views: 300', 'nsid': 'views-300', 'ge': 300, 'less': 1000},
]

favorites_groups = [
    {'name': 'Faves: 10', 'nsid': 'faves-10', 'ge': 10, 'less': 20},
    {'name': 'Faves: 20', 'nsid': 'faves-20', 'ge': 20, 'less': 30},
    {'name': 'Faves: 30', 'nsid': 'faves-30', 'ge': 30, 'less': 100},
]

greylist_config = {
    'group': {'photo_added': 16, 'photo_added_to_category': 1},
    'photo': {'added_to_group': 1, 'published': 6},
}

greylist_config_disabled = {
    'group': {'photo_added': 0, 'photo_added_to_category': 0},
    'photo': {'added_to_group': 0, 'published': 0},
}

group_checker_config = {
    'stats': {'required_tag': 'stat-groups', 'delay': 0},
    'selector': {
        'initial_burst': {
            'num_photos': 1,
            'min_tier': 3
        },
        'switch_phase': {
            'num_required_groups': 10,
            'min_tier': 3,
            'curated_tag': 'curated',
        },
        'dump_phase': {
            'max_tier': 3
        }
    }
}

blacklist = {
    'photo-1': { 'blocked': [], 'manually_added': [] },
    'photo-2': { 'blocked': [], 'manually_added': [] },
}


def test_does_add_legit_tag_groups():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 1
    assert any(
        [
            'street-group-1' in photo['groups'],
            'street-group-2' in photo['groups'],
            'street-group-3' in photo['groups'],
        ]
    )


def test_does_add_legit_tag_groups_in_initial_burst():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker_config_ = json.loads(json.dumps(group_checker_config))
    group_checker_config_['selector']['initial_burst']['num_photos'] = 2
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config_
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 2
    assert any(
        [
            'street-group-1' in photo['groups'] or 'street-group-2' in photo['groups'],
            'street-group-1' in photo['groups'] or 'street-group-3' in photo['groups'],
            'street-group-2' in photo['groups'] or 'street-group-3' in photo['groups'],
        ]
    )


def test_does_add_legit_tag_groups_after_initial_burst():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': ['street-group-1', 'street-group-3'],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker_config_ = json.loads(json.dumps(group_checker_config))
    group_checker_config_['selector']['initial_burst']['num_photos'] = 2
    group_checker_config_['selector']['switch_phase']['num_required_groups'] = 3
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config_
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 3
    assert all(
        [
            'street-group-1' in photo['groups'],
            'street-group-2' in photo['groups'],
            'street-group-3' in photo['groups'],
        ]
    )


def test_does_add_legit_tag_groups_in_dump_phase():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': ['street-group-1', 'street-group-3'],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker_config_ = json.loads(json.dumps(group_checker_config))
    group_checker_config_['selector']['initial_burst']['num_photos'] = 2
    group_checker_config_['selector']['switch_phase']['num_required_groups'] = 2
    tag_groups_ = json.loads(json.dumps(tag_groups))
    tag_groups_['street-group-2']['tier'] = 3
    group_checker = GroupChecker(
        tag_groups_, view_groups, favorites_groups, group_checker_config_
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 3
    assert all(
        [
            'street-group-1' in photo['groups'],
            'street-group-2' in photo['groups'],
            'street-group-3' in photo['groups'],
        ]
    )


def test_does_not_add_legit_higher_tier_tag_groups_in_dump_phase():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': ['street-group-1', 'street-group-3'],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker_config_ = json.loads(json.dumps(group_checker_config))
    group_checker_config_['selector']['initial_burst']['num_photos'] = 2
    group_checker_config_['selector']['switch_phase']['num_required_groups'] = 2
    tag_groups_ = json.loads(json.dumps(tag_groups))
    tag_groups_['street-group-2']['tier'] = 2
    group_checker = GroupChecker(
        tag_groups_, view_groups, favorites_groups, group_checker_config_
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 2
    assert all(
        [
            'street-group-1' in photo['groups'],
            'street-group-3' in photo['groups'],
        ]
    )


def test_does_add_legit_and_restricted_tag_groups_after_initial_burst():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': ['street-group-1', 'street-group-3'],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker_config_ = json.loads(json.dumps(group_checker_config))
    group_checker_config_['selector']['initial_burst']['num_photos'] = 2
    group_checker_config_['selector']['switch_phase']['num_required_groups'] = 3
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config_
    )
    group_info_ = json.loads(json.dumps(group_info))
    group_info_['street-group-2']['ispoolmoderated'] = True
    group_checker(photo, greylist, GroupInfo(group_info_), blacklist)
    assert len(photo['groups']) == 3
    assert all(
        [
            'street-group-1' in photo['groups'],
            'street-group-2' in photo['groups'],
            'street-group-3' in photo['groups'],
        ]
    )


def test_does_not_add_excluded_tag_groups_after_initial_burst():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': ['street-group-1', 'street-group-3'],
        'tags': ['streetphotography', 'excluded'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker_config_ = json.loads(json.dumps(group_checker_config))
    group_checker_config_['selector']['initial_burst']['num_photos'] = 2
    group_checker_config_['selector']['switch_phase']['num_required_groups'] = 3
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config_
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 2
    assert all(
        [
            'street-group-1' in photo['groups'],
            'street-group-3' in photo['groups'],
        ]
    )


def test_does_not_add_excluded_tag_groups_in_initial_burst():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [],
        'tags': ['streetphotography', 'excluded'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker_config_ = json.loads(json.dumps(group_checker_config))
    group_checker_config_['selector']['initial_burst']['num_photos'] = 3
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config_
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 2
    assert all(
        [
            'street-group-1' in photo['groups'],
            'street-group-3' in photo['groups'],
        ]
    )


def test_does_add_legit_tag_groups_in_initial_burst_selects_highest_tier():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker_config_ = json.loads(json.dumps(group_checker_config))
    group_checker_config_['selector']['initial_burst']['num_photos'] = 1
    tag_groups_ = json.loads(json.dumps(tag_groups))
    tag_groups_['street-group-2']['tier'] = 1
    group_checker = GroupChecker(
        tag_groups_, view_groups, favorites_groups, group_checker_config_
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 1
    assert 'street-group-2' in photo['groups']


def test_does_not_add_legit_but_restricted_tag_groups_in_initial_burst():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker_config_ = json.loads(json.dumps(group_checker_config))
    group_checker_config_['selector']['initial_burst']['num_photos'] = 3
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config_
    )
    group_info_ = json.loads(json.dumps(group_info))
    group_info_['street-group-2']['ispoolmoderated'] = True
    group_checker(photo, greylist, GroupInfo(group_info_), blacklist)
    assert len(photo['groups']) == 2
    assert all(
        [
            'street-group-1' in photo['groups'],
            'street-group-3' in photo['groups'],
        ]
    )


def test_does_not_add_legit_but_low_tier_groups_in_initial_burst():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker_config_ = json.loads(json.dumps(group_checker_config))
    group_checker_config_['selector']['initial_burst']['num_photos'] = 3
    tag_groups_ = json.loads(json.dumps(tag_groups))
    tag_groups_['street-group-2']['tier'] = 4
    group_checker = GroupChecker(
        tag_groups_, view_groups, favorites_groups, group_checker_config_
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 2
    assert all(
        [
            'street-group-1' in photo['groups'],
            'street-group-3' in photo['groups'],
        ]
    )


def test_does_not_add_legit_tag_group_when_limited():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config_disabled)
    group_info_ = json.loads(json.dumps(group_info))
    group_info_['street-group-1']['throttle'] = {'remaining': 0}
    group_info_['street-group-2']['throttle'] = {'remaining': 0}
    group_info_['street-group-3']['throttle'] = {'remaining': 0}
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info_), blacklist)
    assert len(photo['groups']) == 0

def test_does_not_add_legit_tag_group_when_blacklisted():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config_disabled)
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    blacklist_ = json.loads(json.dumps(blacklist))
    blacklist_['photo-1']['blocked'] = ['street-group-1', 'street-group-2', 'street-group-3']
    group_checker(photo, greylist, GroupInfo(group_info), blacklist_)
    assert len(photo['groups']) == 0


def test_does_add_legit_tag_group_that_is_not_limited():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config_disabled)
    group_info_ = dict(group_info)
    group_info_['street-group-1']['throttle'] = {'remaining': 0}
    group_info_['street-group-2']['throttle'] = {'remaining': 1}
    group_info_['street-group-3']['throttle'] = {'remaining': 0}
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info_), blacklist)
    assert len(photo['groups']) == 1
    assert photo['groups'] == ['street-group-2']

    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info_), blacklist)

    assert len(photo['groups']) == 1
    assert photo['groups'] == ['street-group-2']


def test_does_add_legit_tag_group_only_as_long_as_remaining():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config_disabled)
    group_info_ = dict(group_info)
    group_info_['street-group-1']['throttle'] = {'remaining': 0}
    group_info_['street-group-2']['throttle'] = {'remaining': 2}
    group_info_['street-group-3']['throttle'] = {'remaining': 0}
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info_), blacklist)
    assert len(photo['groups']) == 1
    assert photo['groups'] == ['street-group-2']

    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info_), blacklist)

    assert len(photo['groups']) == 1
    assert photo['groups'] == ['street-group-2']

    photo_2 = {
        'id': 'photo-2',
        'title': 'Photo 2',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }

    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo_2, greylist, GroupInfo(group_info_), blacklist)

    assert len(photo_2['groups']) == 1
    assert photo['groups'] == ['street-group-2']

    photo_3 = {
        'id': 'photo-2',
        'title': 'Photo 2',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }

    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo_3, greylist, GroupInfo(group_info_), blacklist)

    assert len(photo_3['groups']) == 0


def test_does_not_remove_legit_tag_groups():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [
            'street-group-1',
            'street-group-2',
        ],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert 'street-group-1' in photo['groups']
    assert 'street-group-2' in photo['groups']


def test_does_remove_non_legit_tag_groups():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [
            'group-1',
            'street-group-2',
        ],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert 'group-1' not in photo['groups']
    assert 'street-group-2' in photo['groups']
    assert len(photo['groups']) == 1


def test_does_not_remove_non_legit_tag_groups_if_restricted():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [
            'group-1',
            'street-group-2',
        ],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_info_ = json.loads(json.dumps(group_info))
    group_info_['group-1']['ispoolmoderated'] = True
    group_checker(photo, greylist, GroupInfo(group_info_), blacklist)
    assert 'group-1' in photo['groups']
    assert 'street-group-2' in photo['groups']

def test_does_not_remove_non_legit_tag_groups_if_manually_added():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [
            'group-1',
            'street-group-2',
        ],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    greylist = Greylist({}, greylist_config)
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    blacklist_ = json.loads(json.dumps(blacklist))
    blacklist_['photo-1']['manually_added'] = ['group-1']
    group_checker(photo, greylist, GroupInfo(group_info), blacklist_)
    assert 'group-1' in photo['groups']
    assert 'street-group-2' in photo['groups']

def test_does_not_add_tag_groups_when_greylisted():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 0,
        'views': 0,
        'groups': [],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    timeout = time.time() + 24 * 60 * 60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout,
            }
        },
        greylist_config,
    )
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 0


def test_does_not_add_stat_groups_when_tag_is_missing():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 12,
        'views': 250,
        'groups': [],
        'tags': ['streetphotography'],
        'sets': {},
        'is_public': True,
    }
    timeout = time.time() + 24 * 60 * 60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout,
            }
        },
        greylist_config,
    )
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 0


def test_does_not_add_stat_groups_when_delay_not_passed():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 12,
        'views': 250,
        'groups': [],
        'tags': ['streetphotography', 'stat-groups'],
        'sets': {},
        'is_public': True,
    }
    timeout = time.time() + 24 * 60 * 60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout,
            }
        },
        greylist_config,
    )
    group_checker_config_ = json.loads(json.dumps(group_checker_config))
    group_checker_config_['stats']['delay'] = 48
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config_
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 0


def test_does_add_correct_stat_groups():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 12,
        'views': 250,
        'groups': [],
        'tags': ['streetphotography', 'stat-groups'],
        'sets': {},
        'is_public': True,
    }
    timeout = time.time() + 24 * 60 * 60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout,
            }
        },
        greylist_config,
    )
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 2
    assert all(
        [
            'views-200' in photo['groups'],
            'faves-10' in photo['groups'],
        ]
    )


def test_does_correct_stat_groups_not_removed():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 12,
        'views': 250,
        'groups': ['views-200', 'faves-10'],
        'tags': ['streetphotography', 'stat-groups'],
        'sets': {},
        'is_public': True,
    }
    timeout = time.time() + 24 * 60 * 60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout,
            }
        },
        greylist_config,
    )
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 2
    assert all(
        [
            'views-200' in photo['groups'],
            'faves-10' in photo['groups'],
        ]
    )


def test_does_correctly_changes_stat_groups_views():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 12,
        'views': 350,
        'groups': ['views-200', 'faves-10'],
        'tags': ['streetphotography', 'stat-groups'],
        'sets': {},
        'is_public': True,
    }
    timeout = time.time() + 24 * 60 * 60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout,
            }
        },
        greylist_config,
    )
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 2
    assert all(
        [
            'views-300' in photo['groups'],
            'faves-10' in photo['groups'],
        ]
    )


def test_does_correctly_changes_stat_groups_faves():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 22,
        'views': 250,
        'groups': ['views-200', 'faves-10'],
        'tags': ['streetphotography', 'stat-groups'],
        'sets': {},
        'is_public': True,
    }
    timeout = time.time() + 24 * 60 * 60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout,
            }
        },
        greylist_config,
    )
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 2
    assert all(
        [
            'views-200' in photo['groups'],
            'faves-20' in photo['groups'],
        ]
    )


def test_does_correctly_changes_stat_groups_both():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1 * 24 * 60 * 60,
        'date_taken': now - 1 * 24 * 60 * 60,
        'faves': 22,
        'views': 350,
        'groups': ['views-200', 'faves-10'],
        'tags': ['streetphotography', 'stat-groups'],
        'sets': {},
        'is_public': True,
    }
    timeout = time.time() + 24 * 60 * 60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout,
            }
        },
        greylist_config,
    )
    group_checker = GroupChecker(
        tag_groups, view_groups, favorites_groups, group_checker_config
    )
    group_checker(photo, greylist, GroupInfo(group_info), blacklist)
    assert len(photo['groups']) == 2
    assert all(
        [
            'views-300' in photo['groups'],
            'faves-20' in photo['groups'],
        ]
    )

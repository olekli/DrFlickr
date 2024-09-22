# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.greylist import Greylist
from drflickr.group_checker import GroupChecker

import time
import json

tag_groups = {
    'photography': {
        'tags': [ 'photography' ],
        'groups': [
            'group-1',
            'group-2'
        ]
    },
    'streetphotography': {
        'tags': [ 'streetphotography' ],
        'groups': [
            'street-group-1',
            'street-group-2',
            'street-group-3'
        ]
    },
    'streetphotography_monochrome': {
        'tags': [ 'street', 'monochrome' ],
        'groups': [
            'mono-group-1',
            'mono-group-2',
            'mono-group-3'
        ]
    }
}

view_groups = [
    {
        'name': 'Views: 100',
        'nsid': 'views-100',
        'ge': 100,
        'less': 200
    },
    {
        'name': 'Views: 200',
        'nsid': 'views-200',
        'ge': 200,
        'less': 300
    },
    {
        'name': 'Views: 300',
        'nsid': 'views-300',
        'ge': 300,
        'less': 1000
    }
]

favorites_groups = [
    {
        'name': 'Faves: 10',
        'nsid': 'faves-10',
        'ge': 10,
        'less': 20
    },
    {
        'name': 'Faves: 20',
        'nsid': 'faves-20',
        'ge': 20,
        'less': 30
    },
    {
        'name': 'Faves: 30',
        'nsid': 'faves-30',
        'ge': 30,
        'less': 100
    }
]

greylist_config = {
    'group': {
      'photo_added': 16,
      'photo_added_to_category': 1
    },
    'photo': {
      'added_to_group': 1,
      'published': 6
    }
}

group_checker_config = {
    'stats': {
        'required_tag': 'stat-groups',
        'delay': 0
    },
    'tags': {
        'group_add_limit': 1
    }
}

def test_does_add_legit_tag_groups():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1*24*60*60,
        'date_taken' : now - 1*24*60*60,
        'faves': 0,
        'views': 0,
        'groups': [
        ],
        'tags': [
            'streetphotography'
        ],
        'sets': {},
        'is_public': True
    }
    greylist = Greylist({}, greylist_config)
    group_checker = GroupChecker(tag_groups, view_groups, favorites_groups, group_checker_config)
    group_checker(photo, greylist)
    assert len(photo['groups']) == 1
    assert any([
        'street-group-1' in photo['groups'],
        'street-group-2' in photo['groups'],
        'street-group-3' in photo['groups']
    ])

def test_does_not_remove_legit_tag_groups():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1*24*60*60,
        'date_taken' : now - 1*24*60*60,
        'faves': 0,
        'views': 0,
        'groups': [
            'street-group-1',
            'street-group-2',
        ],
        'tags': [
            'streetphotography'
        ],
        'sets': {},
        'is_public': True
    }
    greylist = Greylist({}, greylist_config)
    group_checker = GroupChecker(tag_groups, view_groups, favorites_groups, group_checker_config)
    group_checker(photo, greylist)
    assert 'street-group-1' in photo['groups']
    assert 'street-group-2' in photo['groups']

def test_does_not_add_tag_groups_when_greylisted():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1*24*60*60,
        'date_taken' : now - 1*24*60*60,
        'faves': 0,
        'views': 0,
        'groups': [
        ],
        'tags': [
            'streetphotography'
        ],
        'sets': {},
        'is_public': True
    }
    timeout = time.time() + 24*60*60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout
            }
        }, greylist_config
    )
    group_checker = GroupChecker(tag_groups, view_groups, favorites_groups, group_checker_config)
    group_checker(photo, greylist)
    assert len(photo['groups']) == 0

def test_does_not_add_stat_groups_when_tag_is_missing():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1*24*60*60,
        'date_taken' : now - 1*24*60*60,
        'faves': 12,
        'views': 250,
        'groups': [
        ],
        'tags': [
            'streetphotography'
        ],
        'sets': {},
        'is_public': True
    }
    timeout = time.time() + 24*60*60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout
            }
        }, greylist_config
    )
    group_checker = GroupChecker(tag_groups, view_groups, favorites_groups, group_checker_config)
    group_checker(photo, greylist)
    assert len(photo['groups']) == 0

def test_does_not_add_stat_groups_when_delay_not_passed():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1*24*60*60,
        'date_taken' : now - 1*24*60*60,
        'faves': 12,
        'views': 250,
        'groups': [
        ],
        'tags': [
            'streetphotography',
            'stat-groups'
        ],
        'sets': {},
        'is_public': True
    }
    timeout = time.time() + 24*60*60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout
            }
        }, greylist_config
    )
    group_checker_config_ = json.loads(json.dumps(group_checker_config))
    group_checker_config_['stats']['delay'] = 48
    group_checker = GroupChecker(tag_groups, view_groups, favorites_groups, group_checker_config_)
    group_checker(photo, greylist)
    assert len(photo['groups']) == 0

def test_does_add_correct_stat_groups():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1*24*60*60,
        'date_taken' : now - 1*24*60*60,
        'faves': 12,
        'views': 250,
        'groups': [
        ],
        'tags': [
            'streetphotography',
            'stat-groups'
        ],
        'sets': {},
        'is_public': True
    }
    timeout = time.time() + 24*60*60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout
            }
        }, greylist_config
    )
    group_checker = GroupChecker(tag_groups, view_groups, favorites_groups, group_checker_config)
    group_checker(photo, greylist)
    assert len(photo['groups']) == 2
    assert all([
        'views-200' in photo['groups'],
        'faves-10' in photo['groups'],
    ])

def test_does_correct_stat_groups_not_removed():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1*24*60*60,
        'date_taken' : now - 1*24*60*60,
        'faves': 12,
        'views': 250,
        'groups': [
            'views-200',
            'faves-10'
        ],
        'tags': [
            'streetphotography',
            'stat-groups'
        ],
        'sets': {},
        'is_public': True
    }
    timeout = time.time() + 24*60*60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout
            }
        }, greylist_config
    )
    group_checker = GroupChecker(tag_groups, view_groups, favorites_groups, group_checker_config)
    group_checker(photo, greylist)
    assert len(photo['groups']) == 2
    assert all([
        'views-200' in photo['groups'],
        'faves-10' in photo['groups'],
    ])

def test_does_correctly_changes_stat_groups_views():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1*24*60*60,
        'date_taken' : now - 1*24*60*60,
        'faves': 12,
        'views': 350,
        'groups': [
            'views-200',
            'faves-10'
        ],
        'tags': [
            'streetphotography',
            'stat-groups'
        ],
        'sets': {},
        'is_public': True
    }
    timeout = time.time() + 24*60*60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout
            }
        }, greylist_config
    )
    group_checker = GroupChecker(tag_groups, view_groups, favorites_groups, group_checker_config)
    group_checker(photo, greylist)
    assert len(photo['groups']) == 2
    assert all([
        'views-300' in photo['groups'],
        'faves-10' in photo['groups'],
    ])

def test_does_correctly_changes_stat_groups_faves():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1*24*60*60,
        'date_taken' : now - 1*24*60*60,
        'faves': 22,
        'views': 250,
        'groups': [
            'views-200',
            'faves-10'
        ],
        'tags': [
            'streetphotography',
            'stat-groups'
        ],
        'sets': {},
        'is_public': True
    }
    timeout = time.time() + 24*60*60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout
            }
        }, greylist_config
    )
    group_checker = GroupChecker(tag_groups, view_groups, favorites_groups, group_checker_config)
    group_checker(photo, greylist)
    assert len(photo['groups']) == 2
    assert all([
        'views-200' in photo['groups'],
        'faves-20' in photo['groups'],
    ])

def test_does_correctly_changes_stat_groups_both():
    now = time.time()
    photo = {
        'id': 'photo-1',
        'title': 'Photo 1',
        'date_posted': now - 1*24*60*60,
        'date_taken' : now - 1*24*60*60,
        'faves': 22,
        'views': 350,
        'groups': [
            'views-200',
            'faves-10'
        ],
        'tags': [
            'streetphotography',
            'stat-groups'
        ],
        'sets': {},
        'is_public': True
    }
    timeout = time.time() + 24*60*60
    greylist = Greylist(
        {
            'group': {
                'street-group-1': timeout,
                'street-group-2': timeout,
                'street-group-3': timeout
            }
        }, greylist_config
    )
    group_checker = GroupChecker(tag_groups, view_groups, favorites_groups, group_checker_config)
    group_checker(photo, greylist)
    assert len(photo['groups']) == 2
    assert all([
        'views-300' in photo['groups'],
        'faves-20' in photo['groups'],
    ])

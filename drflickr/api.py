# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.credentials import getCredentials
from drflickr.file import readYaml

import requests
import json
import re
import time
from datetime import datetime
from requests_oauthlib import OAuth1
from drresult import Ok, Err, returns_result
import logging

logger = logging.getLogger(__name__)


class NetworkError:
    def __init__(self, payload):
        self.payload = payload

    def isNetworkError(self):
        return True

    def isApiError(self):
        return False

    def __str__(self):
        return str(self.payload)


class ApiError:
    def __init__(self, payload):
        self.code = payload['code']
        self.message = payload['message']

    def isNetworkError(self):
        return False

    def isApiError(self):
        return True

    def __str__(self):
        return str(f'{self.code} {self.message}')


class Api:
    URL = 'https://www.flickr.com/services/rest'

    def __init__(self, dry_run, api_key, access_token):
        self.dry_run = dry_run
        self.api_key = api_key
        self.access_token = access_token
        self.user_id = self.access_token['user_nsid']

    @returns_result()
    def checkResult(self, result):
        if result['stat'] == 'success':
            return Ok(result)
        else:
            return Err(result)

    @returns_result()
    def load(self):
        self.auth = OAuth1(
            self.api_key['key'],
            self.api_key['secret'],
            self.access_token['oauth_token'],
            self.access_token['oauth_token_secret'],
        )

        login = self.call('test.login')
        if not login.is_ok():
            self.auth = None
            return login
        return Ok(self)

    @returns_result()
    def call(self, method, params={}, use_user_id=True):
        assert self.auth

        params_ = {'method': f'flickr.{method}', 'format': 'json', **params}
        if use_user_id:
            params_['user_id'] = self.user_id
        response = requests.get(Api.URL, auth=self.auth, params=params_)
        if response.status_code == 200:
            json_str = re.sub(r'^jsonFlickrApi\((.*)\)$', r'\1', response.text)
            data = json.loads(json_str)
            if data['stat'] == 'ok':
                return Ok(data)
            else:
                return Err(ApiError(data))
        else:
            return Err(NetworkError(response))

    @returns_result()
    def getPhotos(self, sort='interestingness-desc'):
        page = 1
        pages = 1
        photos = []
        while page <= pages:
            result = self.call(
                'photos.search',
                {
                    'extras': 'count_views, count_faves, tags, date_upload, date_taken',
                    'sort': sort,
                    'page': page,
                },
                use_user_id=True,
            ).unwrap_or_return()
            photos += result['photos']['photo']
            page += 1
            pages = result['photos']['pages']
        photos = [
            {
                'title': photo['title'],
                'id': photo['id'],
                'tags': photo['tags'].lower().split(' '),
                'views': int(photo['count_views']),
                'faves': int(photo['count_faves']),
                'date_posted': int(photo['dateupload']),
                'date_taken': int(
                    datetime.strptime(
                        photo['datetaken'], '%Y-%m-%d %H:%M:%S'
                    ).timestamp()
                ),
                'is_public': bool(photo['ispublic']),
            }
            for photo in photos
        ]
        for photo in photos:
            contexts = self.call('photos.getAllContexts', {'photo_id': photo['id']}).unwrap_or_return()
            photo['groups'] = [pool['id'] for pool in contexts.get('pool', [])]
        photos = {photo['id']: photo for photo in photos}
        return Ok(photos)

    @returns_result()
    def getPhotoset(self, photoset_id):
        photoset = self.call(
            'photosets.getPhotos', {'photoset_id': photoset_id}
        ).unwrap_or_return()
        photoset = photoset['photoset']['photo']
        return Ok([photo['id'] for photo in photoset])

    @returns_result()
    def updatePhotoDates(self, photo):
        if not self.dry_run:
            return self.call(
                'photos.setDates',
                {
                    'photo_id': photo['id'],
                    'date_posted': photo['date_posted'],
                    'date_taken': datetime.fromtimestamp(photo['date_taken']).strftime(
                        '%Y-%m-%d %H:%M:%S'
                    ),
                    'date_taken_granularity': '0',
                },
            )
        else:
            logger.info(f'dry run: updating times on {photo["title"]}')
            return Ok({'stat': 'success'})

    @returns_result()
    def getGroupInfo(self, group_id):
        group = self.call('groups.getInfo', {'group_id': group_id}).unwrap_or_return()
        group = {
            'name': group['group']['name']['_content'],
            'description': group['group']['description']['_content'],
            'members': int(group['group']['members']['_content']),
            'throttle': group['group']['throttle'],
            'ispoolmoderated': bool(group['group']['ispoolmoderated']),
            'invitation_only': bool(group['group']['invitation_only']),
            'photo_limit_opt_out': bool(group['group']['photo_limit_opt_out']),
        }
        if 'remaining' in group['throttle']:
            group['throttle']['remaining'] = int(group['throttle']['remaining'])
        return Ok(group)

    @returns_result()
    def publishPhoto(self, photo):
        if not self.dry_run:
            return self.call(
                'photos.setPerms',
                {
                    'photo_id': photo['id'],
                    'is_public': '1',
                    'is_friend': '0',
                    'is_family': '0',
                },
            )
        else:
            logger.info(f'dry run: publish photo: {photo["title"]}')
            return Ok({'stat': 'success'})

    @returns_result()
    def getPhotosets(self):
        photosets = self.call('photosets.getList', {}).unwrap_or_return()
        photosets = {
            photoset['title']['_content']: photoset['id']
            for photoset in photosets['photosets']['photoset']
        }
        return Ok(photosets)

    @returns_result()
    def addPhotoToGroup(self, photo, group_id):
        if not self.dry_run:
            return self.call(
                'groups.pools.add', {'photo_id': photo['id'], 'group_id': group_id}
            )
        else:
            logger.info(f'dry run: add {photo["title"]} to group {group_id}')
            return Ok({'stat': 'success'})

    @returns_result()
    def removePhotoFromGroup(self, photo, group_id):
        if not self.dry_run:
            return self.call(
                'groups.pools.remove', {'photo_id': photo['id'], 'group_id': group_id}
            )
        else:
            logger.info(f'dry run: remove {photo["title"]} from group {group_id}')
            return Ok({'stat': 'success'})

    @returns_result()
    def addPhotoToSet(self, photo, set_id):
        if not self.dry_run:
            return self.call(
                'photosets.addPhoto', {'photoset_id': set_id, 'photo_id': photo['id']}
            )
        else:
            logger.info(f'dry run: add {photo["title"]} to set {set_id}')
            return Ok({'stat': 'success'})

    @returns_result()
    def removePhotoFromSet(self, photo, set_id):
        if not self.dry_run:
            return self.call(
                'photosets.removePhoto',
                {'photoset_id': set_id, 'photo_id': photo['id']},
            )
        else:
            logger.info(f'dry run: remove {photo["title"]} from set {set_id}')
            return Ok({'stat': 'success'})

    @returns_result()
    def getTotalViews(self, date):
        result = self.call('stats.getTotalViews', {'date': date})
        if result.is_err():
            result = result.unwrap_err()
            if result.isApiError():
                return Ok(0)
            else:
                return Err(result)
        else:
            return result.unwrap()['stats']['total']['views']

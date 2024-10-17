# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import time
import logging

from drflickr.group_selector import GroupSelector

logger = logging.getLogger(__name__)


class GroupChecker:
    def __init__(self, tag_groups, views_groups, favorites_groups, config):
        self.tag_groups = tag_groups
        self.views_groups = views_groups
        self.favorites_groups = favorites_groups
        self.config = config
        self.group_selector = GroupSelector(self.config['selector'])

    def __call__(self, photo, greylist, group_info, blacklist):
        self.photo = photo
        self.greylist = greylist
        self.group_info = group_info
        self.blacklist = blacklist

        self.purgeGroups()
        if not self.greylist.has('photo', self.photo['id']):
            self.checkStatGroups()
            self.checkTagGroups()

    def purgeGroups(self):
        logger.debug(f'tag_groups: {self.tag_groups}')
        for group in self.tag_groups:
            self.tag_groups[group]['tags'].setdefault('require', [])
            self.tag_groups[group]['tags'].setdefault('match', [])
            self.tag_groups[group]['tags'].setdefault('exclude', [])

        self.target_groups = [
            self.tag_groups[group]
            for group in self.tag_groups.keys()
            if set(self.tag_groups[group]['tags']['require']).issubset(
                set(self.photo['tags'])
            )
            and len(
                set(self.tag_groups[group]['tags']['exclude']).intersection(
                    set(self.photo['tags'])
                )
            )
            == 0
        ]
        logger.debug(f'target_groups: {self.target_groups}')

        allowed_group_ids = (
            [target_group['id'] for target_group in self.target_groups]
            + [group['nsid'] for group in self.views_groups]
            + [group['nsid'] for group in self.favorites_groups]
        )
        logger.debug(f'allowed_group_ids: {allowed_group_ids}')

        logger.debug(f'self.photo["groups"] before purge: {self.photo["groups"]}')
        self.photo['groups'] = [
            group_id
            for group_id in self.photo['groups']
            if
                group_id in allowed_group_ids
                or self.group_info.isRestricted(group_id)
                or group_id in self.blacklist[self.photo['id']]['manually_added']
        ]
        logger.debug(f'self.photo["groups"] after purge: {self.photo["groups"]}')

    def checkTagGroups(self):
        logger.info(f'Checking photo for groups {self.photo["title"]} {self.photo["id"]}')
        eligible_groups = [
            group
            for group in self.target_groups
            if not self.greylist.has('group', group['id'])
            and not group['id'] in self.photo['groups']
            and not self.group_info.hasPhotoLimit(group['id'])
            and not group['id'] in self.blacklist[self.photo['id']]['blocked']
        ]
        logger.debug(f'eligible_groups: {eligible_groups}')
        selected_groups = self.group_selector(
            self.photo,
            eligible_groups,
            self.group_info,
        )
        logger.debug(f'selected_groups: {selected_groups}')
        if selected_groups:
            for group in selected_groups:
                self.greylist.add('group', group['id'], 'photo_added')
                self.group_info.reduceRemaining(group['id'])
                self.photo['groups'].append(group['id'])
            self.greylist.add('photo', self.photo['id'], 'added_to_group')

    def checkStatGroups(self):
        logger.info(f'Checking photo for stats {self.photo["title"]} {self.photo["id"]}')
        logger.debug(f'current groups: {self.photo["groups"]}')
        if (
            self.photo['date_posted'] + self.config['stats']['delay'] * 60 * 60
        ) < time.time():
            if self.config['stats']['required_tag'] in self.photo['tags']:
                for groups, stat in [
                    (self.views_groups, 'views'),
                    (self.favorites_groups, 'faves'),
                ]:
                    for group in groups:
                        logger.debug(f'checking {self.photo} against {group}')
                        if self.photo[stat] >= group['ge'] and self.photo[stat] < group['less']:
                            if group['nsid'] not in self.photo['groups']:
                                logger.info(f'should be in {group["name"]}, adding')
                                self.photo['groups'].append(group['nsid'])
                        elif group['nsid'] in self.photo['groups']:
                            logger.info(f'should not be in {group["name"]}, removing')
                            self.photo['groups'].remove(group['nsid'])
            else:
                logger.info(
                    f'not in "{self.config["stats"]["required_tag"]}", ignoring'
                )

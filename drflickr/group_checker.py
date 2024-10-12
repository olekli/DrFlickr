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
        self.group_selector = GroupSelector()

    def __call__(self, photo, greylist, group_info, blacklist):
        self.checkStatGroups(photo)
        self.checkTagGroups(photo, greylist, group_info, blacklist)

    def checkTagGroups(self, photo, greylist, group_info, blacklist):
        logger.info(f'Checking photo for groups {photo["title"]} {photo["id"]}')
        logger.debug(f'tag_groups: {self.tag_groups}')
        for group in self.tag_groups:
            self.tag_groups[group]['tags'].setdefault('require', [])
            self.tag_groups[group]['tags'].setdefault('match', [])
            self.tag_groups[group]['tags'].setdefault('exclude', [])

        target_groups = [
            self.tag_groups[group]
            for group in self.tag_groups.keys()
            if set(self.tag_groups[group]['tags']['require']).issubset(
                set(photo['tags'])
            )
            and len(
                set(self.tag_groups[group]['tags']['exclude']).intersection(
                    set(photo['tags'])
                )
            )
            == 0
        ]
        logger.debug(f'target_groups: {target_groups}')

        allowed_group_ids = (
            [target_group['id'] for target_group in target_groups]
            + [group['nsid'] for group in self.views_groups]
            + [group['nsid'] for group in self.favorites_groups]
        )
        logger.debug(f'allowed_group_ids: {allowed_group_ids}')

        logger.debug(f'photo["groups"] before purge: {photo["groups"]}')
        photo['groups'] = [
            group_id
            for group_id in photo['groups']
            if
                group_id in allowed_group_ids
                or group_info.isRestricted(group_id)
                or group_id in blacklist[photo['id']]['manually_added']
        ]
        logger.debug(f'photo["groups"] after purge: {photo["groups"]}')
        if not greylist.has('photo', photo['id']):
            eligible_groups = [
                group
                for group in target_groups
                if not greylist.has('group', group['id'])
                and not group['id'] in photo['groups']
                and not group_info.hasPhotoLimit(group['id'])
                and not group['id'] in blacklist[photo['id']]['blocked']
            ]
            logger.debug(f'eligible_groups: {eligible_groups}')
            selected_groups = self.group_selector(
                photo,
                eligible_groups,
                group_info,
                self.config['tags']['initial_burst'],
                self.config['tags']['switch_phase'],
            )
            logger.debug(f'selected_groups: {selected_groups}')
            if selected_groups:
                for group in selected_groups:
                    greylist.add('group', group['id'], 'photo_added')
                    group_info.reduceRemaining(group['id'])
                    photo['groups'].append(group['id'])
                greylist.add('photo', photo['id'], 'added_to_group')

    def checkStatGroups(self, photo):
        logger.info(f'Checking photo for stats {photo["title"]} {photo["id"]}')
        logger.debug(f'current groups: {photo["groups"]}')
        if (
            photo['date_posted'] + self.config['stats']['delay'] * 60 * 60
        ) < time.time():
            if self.config['stats']['required_tag'] in photo['tags']:
                for groups, stat in [
                    (self.views_groups, 'views'),
                    (self.favorites_groups, 'faves'),
                ]:
                    for group in groups:
                        logger.debug(f'checking {photo} against {group}')
                        if photo[stat] >= group['ge'] and photo[stat] < group['less']:
                            if group['nsid'] not in photo['groups']:
                                logger.info(f'should be in {group["name"]}, adding')
                                photo['groups'].append(group['nsid'])
                        elif group['nsid'] in photo['groups']:
                            logger.info(f'should not be in {group["name"]}, removing')
                            photo['groups'].remove(group['nsid'])
            else:
                logger.info(
                    f'not in "{self.config["stats"]["required_tag"]}", ignoring'
                )

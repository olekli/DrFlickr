# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import time
import random
import logging

logger = logging.getLogger(__name__)


class GroupChecker:
    def __init__(self, tag_groups, views_groups, favorites_groups, config):
        self.tag_groups = tag_groups
        self.views_groups = views_groups
        self.favorites_groups = favorites_groups
        self.config = config
        self.rng = random.Random(time.time())

    def __call__(self, photo, greylist):
        self.checkStatGroups(photo)
        self.checkTagGroups(photo, greylist)

    def checkTagGroups(self, photo, greylist):
        logger.info(f'Checking photo for groups {photo["title"]} {photo["id"]}')
        logger.debug(f'tag_groups: {self.tag_groups}')
        target_groups = [
            group
            for groups in [
                self.tag_groups[cat]['groups']
                for cat in self.tag_groups.keys()
                if set(self.tag_groups[cat]['tags']).issubset(set(photo['tags']))
            ]
            for group in groups
        ]
        logger.debug(f'target_groups: {target_groups}')

        allowed_groups = (
            target_groups
            + [group['nsid'] for group in self.views_groups]
            + [group['nsid'] for group in self.favorites_groups]
        )
        logger.debug(f'target_groups: {allowed_groups}')

        logger.debug(f'photo["groups"] before purge: {photo["groups"]}')
        photo['groups'] = [
            group for group in photo['groups'] if group in allowed_groups
        ]
        logger.debug(f'photo["groups"] after purge: {photo["groups"]}')
        if not greylist.has('photo', photo['id']):
            eligible_groups = [
                group
                for group in target_groups
                if not greylist.has('group', group) and not group in photo['groups']
            ]
            logger.debug(f'eligible_groups: {eligible_groups}')
            self.rng.shuffle(eligible_groups)
            eligible_groups = eligible_groups[: self.config['tags']['group_add_limit']]
            photo['groups'] += eligible_groups
            if len(eligible_groups) > 0:
                for group in eligible_groups:
                    greylist.add('group', group, 'photo_added')
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

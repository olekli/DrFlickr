# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.file import readYaml, writeYaml, readJson, writeJson, mkdir
from drflickr.credentials import getCredentials
from drflickr.api import Api
from drflickr.greylist import Greylist
from drflickr.submissions import Submissions
from drflickr.retriever import Retriever
from drflickr.logic import Logic
from drflickr.reconciler import Reconciler
from drflickr.applicator import Applicator
from drflickr.stats import Stats
from drflickr.operations_review import OperationsReview
from drflickr.group_info_updater import GroupInfoUpdater
from mrjsonstore import JsonStore
from drresult import Ok, Err, returns_result
import yaml
import json
import logging
import random
import time
import os

logger = logging.getLogger(__name__)


class Runner:
    def __init__(self, config_path, run_path, creds_path, dry_run=True, debug_dry_run=False):
        self.dry_run = dry_run
        self.debug_dry_run = debug_dry_run
        self.local_dry_run = self.dry_run and not self.debug_dry_run
        self.run_path = run_path
        self.creds_path = creds_path
        self.access_token_filename = os.path.join(creds_path, 'access-token.yaml')
        self.views_groups_filename = os.path.join(config_path, 'groups-views.yaml')
        self.favorites_groups_filename = os.path.join(
            config_path, 'groups-favorites.yaml'
        )
        self.tag_groups_filename = os.path.join(config_path, 'groups-tags.yaml')
        self.config_filename = os.path.join(config_path, 'config.yaml')
        self.submissions_filename = os.path.join(run_path, 'submissions.json')
        self.stats_filename = os.path.join(run_path, 'stats.json')
        self.state_store_filename = os.path.join(run_path, 'state_store.json')
        self.blacklist_filename = os.path.join(run_path, 'blacklist.json')

        self.state_store = None
        self.blacklist_store = None
        self.retriever = None
        self.logic = None
        self.applicator = None
        self.operations_review = None

    @returns_result()
    def load(self):
        logger.info(f'initializing')
        mkdir(self.run_path).unwrap_or_return()
        api_key = getCredentials(self.creds_path, 'api-key').unwrap_or_return()
        access_token = readYaml(self.access_token_filename).unwrap_or_return()
        views_groups = readYaml(self.views_groups_filename).unwrap_or_return()
        favorites_groups = readYaml(self.favorites_groups_filename).unwrap_or_return()
        tag_groups = readYaml(self.tag_groups_filename).unwrap_or_return()
        config = readYaml(self.config_filename).unwrap_or_return()
        if self.dry_run:
            config['applicator']['throttle']['min_ms'] = 0
            config['applicator']['throttle']['max_ms'] = 1

        submissions = Submissions(self.submissions_filename, dry_run=self.local_dry_run)
        api = (
            Api(dry_run=self.dry_run, api_key=api_key, access_token=access_token)
            .load()
            .unwrap_or_return()
        )
        stats = Stats(api, self.stats_filename).load()

        self.state_store = JsonStore(self.state_store_filename, dry_run=self.local_dry_run)
        self.blacklist_store = JsonStore(self.blacklist_filename, dry_run=self.local_dry_run)
        self.retriever = Retriever(api, submissions)
        self.logic = Logic(
            views_groups=views_groups,
            favorites_groups=favorites_groups,
            tag_groups=tag_groups,
            config=config['logic'],
            stats=stats,
        )

        all_groups = [
            group
            for group in list(tag_groups.keys())
            + [group['nsid'] for group in views_groups]
            + [group['nsid'] for group in favorites_groups]
        ]
        group_info_updater = GroupInfoUpdater(api)
        with self.state_store.transaction() as state:
            state.setdefault('group_info', {})
            state['group_info'] = group_info_updater(state['group_info'], all_groups)

        self.applicator = Applicator(
            api,
            submissions,
            self.state_store.view()['group_info'],
            config['applicator'],
        )
        self.operations_review = OperationsReview(self.state_store.view()['group_info'])

        return Ok(self)

    @returns_result()
    def __call__(self):
        with self.blacklist_store.transaction() as blacklist:
            retriever_result = self.retriever(blacklist).unwrap_or_raise()
            blacklist.clear()
            blacklist.update(retriever_result.blacklist)
        with self.state_store.transaction() as state:
            state.setdefault('photos_expected', {})
            state.setdefault('logic_greylist', {})
            state.setdefault('group_info', {})

            logic_result = self.logic(
                photos_actual=retriever_result.photos_actual,
                photos_expected=state['photos_expected'],
                greylist=state['logic_greylist'],
                group_info=state['group_info'],
                blacklist=retriever_result.blacklist
            )

            state['photos_expected'] = logic_result.photos_expected
            state['logic_greylist'] = logic_result.greylist
            state['group_info'] = logic_result.group_info
        if self.dry_run:
            writeYaml(
                'operations-review-full.yaml', logic_result.operations
            ).unwrap_or_return()
            writeYaml(
                'operations-review.yaml',
                self.operations_review(logic_result.operations),
            ).unwrap_or_return()
        with self.state_store.transaction() as state:
            state.setdefault('applicator_greylist', {})
            applicator_result = self.applicator(
                logic_result.operations,
                retriever_result.photosets_map,
                state['applicator_greylist'],
            )
            state['applicator_greylist'] = applicator_result.greylist
        logger.debug(f'reconciled: {applicator_result.result}')

        return Ok(applicator_result.result)

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
from drflickr.group_info import GroupInfo
from drflickr.operations_review import OperationsReview
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
    def __init__(self, config_path, run_path, creds_path, dry_run=True):
        self.dry_run = dry_run
        self.run_path = run_path
        self.creds_path = creds_path
        self.access_token_filename = os.path.join(creds_path, 'access-token.yaml')
        self.views_groups_filename = os.path.join(config_path, 'groups-views.yaml')
        self.favorites_groups_filename = os.path.join(
            config_path, 'groups-favorites.yaml'
        )
        self.tag_groups_filename = os.path.join(config_path, 'groups-tags.yaml')
        self.config_filename = os.path.join(config_path, 'config.yaml')
        self.group_info_filename = os.path.join(run_path, 'group-info.yaml')
        self.submissions_filename = os.path.join(run_path, 'submissions.json')
        self.stats_filename = os.path.join(run_path, 'stats.json')
        self.state_store_filename = os.path.join(run_path, 'state_store.json')

        self.state_store = None
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

        submissions = Submissions(self.submissions_filename, dry_run=self.dry_run)
        api = (
            Api(dry_run=self.dry_run, api_key=api_key, access_token=access_token)
            .load()
            .unwrap_or_return()
        )
        group_info = GroupInfo(self.group_info_filename, api)
        stats = Stats(api, self.stats_filename).load().unwrap_or_return()

        self.state_store = JsonStore(self.state_store_filename, dry_run=self.dry_run)
        self.retriever = Retriever(api, submissions)
        self.logic = Logic(
            views_groups=views_groups,
            favorites_groups=favorites_groups,
            tag_groups=tag_groups,
            config=config['logic'],
            stats=stats,
        )
        self.applicator = Applicator(api, submissions, group_info, config['applicator'])
        self.operations_review = OperationsReview(group_info)

        return Ok(self)

    @returns_result()
    def __call__(self):
        retriever_result = self.retriever().unwrap_or_return()
        with self.state_store.transaction() as state:
            state.setdefault('photos_expected', {})
            state.setdefault('logic_greylist', {})

            logic_result = self.logic(
                retriever_result.photos_actual,
                state['photos_expected'],
                state['logic_greylist'],
            )

            state['photos_expected'] = logic_result.photos_expected
            state['logic_greylist'] = logic_result.greylist
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

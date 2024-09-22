# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import click


def config_path_option(f):
    f = click.option(
        '--config-path',
        type=click.Path(),
        default='./config',
        help='Path to the config directory.',
    )(f)
    return f


def run_path_option(f):
    f = click.option(
        '--run-path',
        type=click.Path(),
        default='./run',
        help='Path to the run directory.',
    )(f)
    return f


def creds_path_option(f):
    f = click.option(
        '--creds-path',
        type=click.Path(),
        default='./auth',
        help='Path to the credentials directory.',
    )(f)
    return f

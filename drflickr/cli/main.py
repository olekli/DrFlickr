# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.cli.access_token import access_token
from drflickr.cli.automation import automation

import click


@click.group()
def main():
    pass


main.add_command(access_token)
main.add_command(automation)

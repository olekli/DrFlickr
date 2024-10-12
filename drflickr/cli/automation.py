# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.runner import Runner
from drflickr.cli.path_options import (
    config_path_option,
    run_path_option,
    creds_path_option,
)

import click
import traceback
from daemon import DaemonContext
from daemon.pidfile import PIDLockFile
import signal
import time
import logging
import sys
import os
import random

pidfile_path = '/tmp/flickr-daemon.pid'


def create_logger(logfile=None):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # Remove any existing handlers
    logger.handlers = []

    if logfile:
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def signal_handler(signum, frame, exit_flag):
    if not exit_flag['flag']:
        logging.info(f'Received signal {signum}: will exit gracefully when idle')
        exit_flag['flag'] = True
    else:
        logging.info(f'Received signal {signum}: terminating now')
        sys.exit(1)


def run(dry_run, config_path, run_path, creds_path):
    runner = Runner(
        config_path=config_path,
        run_path=run_path,
        creds_path=creds_path,
        dry_run=dry_run,
    ).load()
    if runner:
        runner = runner.unwrap()
        result = runner()
        if result:
            logging.info(f'Runner succeeded. Fully reconciled: {result.unwrap()}')
        else:
            logging.critical(
                f'Runner failed: {"".join(traceback.format_exception(result.unwrap_err()))}'
            )
        return result
    else:
        logging.critical(
            f'Cannot load runner: {"".join(traceback.format_exception(runner.unwrap_err()))}'
        )
        return runner


def loop(interval, exit_flag, dry_run, config_path, run_path, creds_path):
    logging.info('Startup')
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, exit_flag))
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, exit_flag))

    while not exit_flag['flag']:
        result = run(dry_run, config_path, run_path, creds_path)
        if not result:
            break

        total_sleep = 0
        mod_interval = (interval * 0.5) + int(random.uniform(0, interval))
        logging.info(f'Sleeping for {mod_interval} minutes...')
        while total_sleep < mod_interval * 60:
            if exit_flag['flag']:
                break
            time.sleep(1)
            total_sleep += 1

    logging.info('Exit')


@click.group()
def automation():
    pass


@automation.command()
@click.option('--daemon/--no-daemon', default=False, help='Run as a daemon.')
@click.option('--logfile', type=click.Path(), default=None, help='Path to the logfile.')
@click.option(
    '--interval',
    type=int,
    default=120,
    help='Interval in minutes between executions (default: 120).',
)
@click.option(
    '--dry-run/--no-dry-run', default=True, help='Enable or disable dry run mode.'
)
@config_path_option
@run_path_option
@creds_path_option
def start(daemon, logfile, interval, dry_run, config_path, run_path, creds_path):
    if os.path.exists(pidfile_path):
        try:
            with open(pidfile_path, 'r') as f:
                pid = int(f.read())
            # Check if the process is running
            os.kill(pid, 0)
        except OSError:
            # Process is not running
            print('PID file exists but no process is running. Removing stale PID file.')
            os.remove(pidfile_path)
        else:
            print(f'Daemon is already running with PID {pid}.')
            sys.exit(1)

    exit_flag = {'flag': False}

    if daemon:
        if not logfile:
            logfile = './flickr-daemon.log'
            print(f'No logfile specified. Defaulting to {logfile}')

        logfile_dir = os.path.dirname(logfile) or '.'
        if not os.access(logfile_dir, os.W_OK):
            print(f'Cannot write to logfile {logfile}. Please check permissions.')
            sys.exit(1)

        logger = create_logger(logfile)
        preserve_fds = [handler.stream.fileno() for handler in logger.handlers]

        pidfile = PIDLockFile(pidfile_path)
        with DaemonContext(
            detach_process=True,
            pidfile=pidfile,
            files_preserve=preserve_fds,
            working_directory='./',
        ) as context:
            loop(interval, exit_flag, dry_run, config_path, run_path, creds_path)
    else:
        logger = create_logger(logfile)

        with open(pidfile_path, 'w') as f:
            f.write(str(os.getpid()))

        try:
            loop(interval, exit_flag, dry_run, config_path, run_path, creds_path)
        finally:
            if os.path.exists(pidfile_path):
                os.remove(pidfile_path)


@automation.command()
def stop():
    if os.path.exists(pidfile_path):
        with open(pidfile_path, 'r') as f:
            pid = int(f.read())
        try:
            os.kill(pid, signal.SIGTERM)
            print(f'Sent SIGTERM to process {pid}.')
            time.sleep(1)
        except ProcessLookupError:
            print('No process found with PID from PID file. Removing stale PID file.')
        except PermissionError:
            print(f'Permission denied when trying to stop process {pid}.')
            sys.exit(1)
        finally:
            if os.path.exists(pidfile_path):
                os.remove(pidfile_path)
    else:
        print('No daemon is running.')


@automation.command()
def terminate():
    if os.path.exists(pidfile_path):
        with open(pidfile_path, 'r') as f:
            pid = int(f.read())
        try:
            os.kill(pid, signal.SIGTERM)
            print(f'Sent SIGTERM to process {pid}.')
            time.sleep(1)
            os.kill(pid, signal.SIGTERM)
            print(f'Sent SIGTERM to process {pid}.')
            time.sleep(1)
        except ProcessLookupError:
            print('No process found with PID from PID file. Removing stale PID file.')
        except PermissionError:
            print(f'Permission denied when trying to stop process {pid}.')
            sys.exit(1)
        finally:
            if os.path.exists(pidfile_path):
                os.remove(pidfile_path)
    else:
        print('No daemon is running.')

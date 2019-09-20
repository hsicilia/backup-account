#!/usr/bin/env python3
"""
A Python3 script to backup copies of local or remote directories
and MySQL/MariaDB databases

Script URL: https://github.com/hsicilia/backup-account

This source code Form is subject to the terms of the GNU Affero
General Public License, version 3 (AGPLv3).
If a copy of the AGPLv3 was not distributed with this file, you can
obtain one at https://www.gnu.org/licenses/agpl-3.0.html.
"""

import logging
import shutil

import constants as const
import log


def config_log():
    # Empty last log file
    with open(env['log_last'], 'w'):
        pass

    logger.setLevel(env['error_level'])

    fh_last = logging.FileHandler(env['log_last'])
    formatter_last = logging.Formatter('%(levelname)s:%(message)s')
    fh_last.setFormatter(formatter_last)
    logger.addHandler(fh_last)


def log_start():
    log_separator(const.LOG_LEVEL_PRIMARY, 'BACKUP BEGIN')

    # Log parameters
    logger.debug('Script directory: ' + env['dir_script'])
    logger.debug('Exclude file: ' + env['exclude_file'])
    logger.debug('Backup directory: ' + env['dir_backup'])
    logger.debug('Log directory: ' + env['dir_log'])
    logger.debug('Last log file: ' + env['log_last'])
    logger.debug('Full log file: ' + env['log_full'])
    logger.debug('Base directory: ' + env['dir_base'])
    logger.debug('Sync directory: ' + env['dir_sync'])
    logger.debug('Diff directory: ' + env['dir_diff'])

    if args.db_server is not None:
        logger.debug('Database directory: ' + env['dir_db'])
        logger.debug('Database filename: ' + env['db_filename'])
        logger.debug('Database full path: ' + env['db_url'])


def log_end():
    log_separator(const.LOG_LEVEL_PRIMARY, 'BACKUP END')
    logger.info('')

    # # Concat log_last with log_full
    with open(env['log_full'], "a+") as dest_file:
        with open(env['log_last'], "r") as source_file:
            shutil.copyfileobj(source_file, dest_file)


def log_separator(level, text):
    if level == const.LOG_LEVEL_PRIMARY:
        separator = '====='
    else:
        separator = '+++'

    logger.info(separator + ' ' + env['date'] + ' - ' +
                args.name + ' - ' + text + ' ' + separator)
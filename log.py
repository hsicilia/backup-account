#!/usr/bin/env python3
"""
Log functions

This source code Form is subject to the terms of the GNU Affero
General Public License, version 3 (AGPLv3).
If a copy of the AGPLv3 was not distributed with this file, you can
obtain one at https://www.gnu.org/licenses/agpl-3.0.html.
"""

import logging
import shutil

import config as cfg


logger = logging.getLogger(__name__)


def config_log():
    """ Config the log to save the information in the selected file """

    # Empty last log file
    with open(cfg.env['log_last'], 'w'):
        pass

    logger.setLevel(cfg.env['error_level'])

    fh_last = logging.FileHandler(cfg.env['log_last'])
    formatter_last = logging.Formatter('%(levelname)s:%(message)s')
    fh_last.setFormatter(formatter_last)
    logger.addHandler(fh_last)


def log_start():
    """ Save init values in the log file """
    log_separator(cfg.LOG_LEVEL_PRIMARY, 'BACKUP BEGIN')

    # Log parameters
    logger.debug('Script directory: ' + cfg.env['dir_script'])
    logger.debug('Exclude file: ' + cfg.env['exclude_file'])
    logger.debug('Backup directory: ' + cfg.env['dir_backup'])
    logger.debug('Log directory: ' + cfg.env['dir_log'])
    logger.debug('Last log file: ' + cfg.env['log_last'])
    logger.debug('Full log file: ' + cfg.env['log_full'])
    logger.debug('Base directory: ' + cfg.env['dir_base'])
    logger.debug('Sync directory: ' + cfg.env['dir_sync'])
    logger.debug('Diff directory: ' + cfg.env['dir_diff'])

    if cfg.args.db_server is not None:
        logger.debug('Database directory: ' + cfg.env['dir_db'])
        logger.debug('Database filename: ' + cfg.env['db_filename'])
        logger.debug('Database full path: ' + cfg.env['db_url'])


def log_end():
    """ Save final values in the log file """
    log_separator(cfg.LOG_LEVEL_PRIMARY, 'BACKUP END')
    logger.info('')

    # # Concat log_last with log_full
    with open(cfg.env['log_full'], "a+") as dest_file:
        with open(cfg.env['log_last'], "r") as source_file:
            shutil.copyfileobj(source_file, dest_file)


def log_separator(level, text):
    """ Save separator line in the log file """
    if level == cfg.LOG_LEVEL_PRIMARY:
        separator = '====='
    else:
        separator = '+++'

    logger.info(separator + ' ' + cfg.env['date'] + ' - ' +
                cfg.args.name + ' - ' + text + ' ' + separator)


if __name__ == "__main__":
    print(cfg.ERROR_WRONG_MODULE)

#!/usr/bin/env python3
"""
Syncronize and backup files functions

This source code Form is subject to the terms of the GNU Affero
General Public License, version 3 (AGPLv3).
If a copy of the AGPLv3 was not distributed with this file, you can
obtain one at https://www.gnu.org/licenses/agpl-3.0.html.
"""

import logging
import os

import config as cfg
import log


logger = logging.getLogger(__name__)


def backup_sync():
    """ Syncronize files using rsync """

    log.log_separator(cfg.LOG_LEVEL_SECUNDARY, 'rsync copy')

    command = ("rsync -azh -e 'ssh -p " + str(cfg.args.port)
               + "' --exclude-from=" + cfg.env['exclude_file']
               + ' --delete-after --force --stats '
               + cfg.args.user + '@' + cfg.args.serv + ':'
               + cfg.args.copy_dir + ' '
               + cfg.env['dir_sync'] + ' >> '
               + cfg.env['log_last'] + ' 2>&1')

    logger.debug(command)
    os.system(command)


def backup_files():
    """ Backup files using rdiff-backup """
    log.log_separator(cfg.LOG_LEVEL_SECUNDARY, 'rdiff-backup copy')

    if cfg.args.type == cfg.LOCAL_TYPE:
        dir_source = cfg.args.copy_dir
    elif cfg.args.type == cfg.REMOTE_TYPE:
        dir_source = cfg.env['dir_sync']

    command = ('rdiff-backup --print-statistics ' + dir_source + ' '
               + cfg.env['dir_diff'] + ' >> ' + cfg.env['log_last'] + ' 2>&1')
    logger.debug(command)
    os.system(command)

    logger.info('-- ' + cfg.env['date'] + ' '
                + cfg.args.name + ' - Deleting old rdiff-backup copies')
    command = ('rdiff-backup --remove-older-than $(('
               + str(cfg.env['backup_days'])
               + '))D --force ' + cfg.env['dir_diff'] + ' >> '
               + cfg.env['log_last'] + ' 2>&1')
    logger.debug(command)
    os.system(command)


if __name__ == "__main__":
    print(cfg.ERROR_WRONG_MODULE)

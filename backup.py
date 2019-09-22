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

__version__ = '0.5'

import logging

import config as cfg
import databases
import files
import init
import log


if __name__ == "__main__":

    # Store script parameters
    init.process_parameters()

    # Store configuration and other calculated fields at "env" dictionary
    init.process_env()

    # Initializing log
    logger = logging.getLogger(__name__)
    log.config_log()

    init.check_directories()

    log.log_start()

    if cfg.args.db_server is not None:
        databases.backup_db()

    if cfg.args.type == cfg.REMOTE_TYPE:
        files.backup_sync()

    files.backup_files()

    log.log_end()

    exit(0)

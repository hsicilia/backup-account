#!/usr/bin/env python3
"""
Databases functions

This source code Form is subject to the terms of the GNU Affero
General Public License, version 3 (AGPLv3).
If a copy of the AGPLv3 was not distributed with this file, you can
obtain one at https://www.gnu.org/licenses/agpl-3.0.html.
"""

import logging
import os
import tarfile

import config as cfg
import log


logger = logging.getLogger(__name__)


def backup_db():
    """ Dump database and rotate backup files """

    log.log_separator(cfg.LOG_LEVEL_SECUNDARY,
                      cfg.env['db_system'] + ' Backup')

    if cfg.args.db_server == cfg.DB_MYSQL:
        command = backup_mysql()
    elif cfg.args.db_server == cfg.DB_POSTGRESQL:
        command = backup_postgresql()

    command = complete_command(command)

    logger.debug(command)
    exit_value = os.system(command)
    logger.debug('EXIT:' + str(exit_value))

    if (exit_value == cfg.EXIT_NO_ERROR):
        rotate_db_files()


def backup_mysql():
    """ Dump MySQL/MariaDB databases and rotate backup files """

    # Dump MySQL databases
    command = 'nice -n 20 mysqldump --all-databases --opt'

    # If cfg.args.db_user or cfg.args.db_pass are empty the script
    # take the values from some of the default .cnf files:
    # ~/.my.cnf or ~/.mylogin.cnf
    # See: https://dev.mysql.com/doc/refman/8.0/en/option-files.html
    if cfg.args.db_user is not None:
        command = command + ' -u ' + cfg.args.db_user
    if cfg.args.db_pass is not None:
        command = command + ' -p' + cfg.args.db_pass

    return command


def backup_postgresql():
    """ Dump PostgreSQL databases and rotate backup files """

    # Dump MySQL databases
    command = 'nice -n 20 pg_dump ' + cfg.args.db_name

    # If cfg.args.db_user is empty the script takes the value
    # from .pgpass file
    # See: https://www.postgresql.org/docs/9.3/libpq-pgpass.html
    if cfg.args.db_user is not None:
        command = command + ' -U ' + cfg.args.db_user

    return command


def complete_command(command):
    """ Wrap a command to run it on the remote server """

    if cfg.args.type == cfg.LOCAL_TYPE:
        command = command + ' > ' + cfg.env['db_url']
    elif cfg.args.type == cfg.REMOTE_TYPE:
        command = ('ssh -p ' + str(cfg.args.port) + ' '
                   + cfg.args.user + '@' + cfg.args.serv
                   + ' ' + command + ' > ' + cfg.env['db_url'])
    return command


def rotate_db_files():  # Split parameters WORKING HERE
    """ Rotate db backup files """

    # First delete the last backup
    db_last = (cfg.env['db_url']
               + '.' + str(cfg.env['backup_days']) + cfg.EXT_COMPRESS_FILE)
    if os.path.exists(db_last):
        os.remove(db_last)
    # Rotate the rest of backups
    for i in range(cfg.env['backup_days'] - 1, 0, -1):
        db_source = cfg.env['db_url'] + '.' + str(i) + cfg.EXT_COMPRESS_FILE
        db_destination = (cfg.env['db_url'] + '.' + str(i + 1)
                          + cfg.EXT_COMPRESS_FILE)
        if os.path.exists(db_source):
            os.rename(db_source, db_destination)

    # Compress the sql file
    tar = tarfile.open(cfg.env['db_url'] + '.1'
                       + cfg.EXT_COMPRESS_FILE, 'w:gz')
    os.chdir(cfg.env['dir_db'])
    tar.add(cfg.env['db_filename'])
    tar.close()

    os.system('ls -lh ' + cfg.env['db_url'] + ' ' + cfg.env['db_url'] +
              '.1.tar.gz >> ' + cfg.env['log_last'])


if __name__ == "__main__":
    print(cfg.ERROR_WRONG_MODULE)

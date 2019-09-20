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

import configparser
import logging
import os
import tarfile

import constants as const
import log


def backup_db():
    """ Dump database and rotate backup files """

    log.log_separator(const.LOG_LEVEL_SECUNDARY,
                  env['db_system'] + ' Backup')

    if args.db_server == const.DB_MYSQL:
        command = backup_mysql()
    elif args.db_server == const.DB_POSTGRESQL:
        command = backup_postgresql()

    command = complete_command(command)

    logger.debug(command)
    exit_value = os.system(command)
    logger.debug('EXIT:' + str(exit_value))

    if (exit_value == const.EXIT_NO_ERROR):
        rotate_db_files(args, env)


def backup_mysql():
    """ Dump MySQL/MariaDB databases and rotate backup files """

    # Dump MySQL databases
    command = 'nice -n 20 mysqldump --all-databases --opt'

    # If args.db_user or args.db_pass are empty the script take the values
    # from some of the default .cnf files: ~/.my.cnf or ~/.mylogin.cnf
    # See: https://dev.mysql.com/doc/refman/8.0/en/option-files.html
    if args.db_user is not None:
        command = command + ' -u ' + args.db_user
    if args.db_pass is not None:
        command = command + ' -p' + args.db_pass

    return command


def backup_postgresql():
    """ Dump PostgreSQL databases and rotate backup files """

    # Dump MySQL databases
    command = 'nice -n 20 pg_dump ' + args.db_name

    # If args.db_user is empty the script takes the value
    # from .pgpass file
    # See: https://www.postgresql.org/docs/9.3/libpq-pgpass.html
    if args.db_user is not None:
        command = command + ' -U ' + args.db_user

    return command


def complete_command(command):
    if args.type == const.LOCAL_TYPE:
        command = command + ' > ' + env['db_url']
    elif args.type == const.REMOTE_TYPE:
        command = ('ssh -p ' + str(args.port) + ' '
                   + args.user + '@' + args.serv
                   + ' ' + command + ' > ' + env['db_url'])
    return command


def rotate_db_files():  # Split parameters WORKING HERE
    # Rotate db backup files
    # First delete the last backup
    db_last = (env['db_url']
               + '.' + str(env['backup_days']) + const.EXT_COMPRESS_FILE)
    if os.path.exists(db_last):
        os.remove(db_last)
    # Rotate the rest of backups
    for i in range(env['backup_days'] - 1, 0, -1):
        db_source = env['db_url'] + '.' + str(i) + const.EXT_COMPRESS_FILE
        db_destination = (env['db_url'] + '.' + str(i + 1)
                          + const.EXT_COMPRESS_FILE)
        if os.path.exists(db_source):
            os.rename(db_source, db_destination)

    # Compress the sql file
    tar = tarfile.open(env['db_url'] + '.1' + const.EXT_COMPRESS_FILE, 'w:gz')
    os.chdir(env['dir_db'])
    tar.add(env['db_filename'])
    tar.close()

    os.system('ls -lh ' + env['db_url'] + ' ' + env['db_url'] +
              '.1.tar.gz >> ' + env['log_last'])


if __name__ == "__main__":
    pass

#!/usr/bin/env python3
"""
A Python3 script to backup copies of local or remote directories
and MySQL/MariaDB databases

This source code Form is subject to the terms of the GNU Affero
General Public License, version 3 (AGPLv3).
If a copy of the AGPLv3 was not distributed with this file, you can
obtain one at https://www.gnu.org/licenses/agpl-3.0.html.
"""

__version__ = '0.5'

import configparser
import logging
import os
import sys
from argparse import ArgumentParser
from datetime import datetime


def process_parameters():
    """ Process the command line arguments and show the help """

    description = 'Make a backup of selected type.'

    parser = ArgumentParser(description=description)
    parser.add_argument('type', help='type of backup',
                        choices=TYPES)
    parser.add_argument('-n', '--name',
                        help='copy name', required=True)
    parser.add_argument('-s', '--serv',
                        help='remote server URL')
    parser.add_argument('-u', '--user',
                        help='remote server user')
    parser.add_argument('-p', '--port', type=int,
                        help='remote server port', default=22)
    parser.add_argument('-c', '--copy-dir',
                        help='copy directory', required=True)
    parser.add_argument('-d', '--database',
                        help='activate database backup and select '
                             'database server',
                        choices=DATABASES)
    parser.add_argument('-e', '--db-user',
                        help='database user')
    parser.add_argument('-w', '--db-pass',
                        help='database password')

    try:
        args = parser.parse_args()
    except IOError as msg:
        parser.error(str(msg))
        sys.exit(EXIT_ARGPARSE_ERROR)

    # "remote" option require --serv and --user
    if args.type == REMOTE_TYPE:
        if (args.serv is None or args.user is None):
            parser.error('For "remote" type the parameters --serv '
                         'and --user are required')
            exit(EXIT_ARGPARSE_ERROR)

    if (args.database is None
        and (args.db_user is not None
             or args.db_pass is not None)):
        parser.error('Parameters --db-user or --db-pass '
                     'are not allowed if --database is not present')
        exit(EXIT_ARGPARSE_ERROR)

    return parser, args


def check_directories(*directories):
    """ If directory doesn't exist, create it """

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def log_header(level, text):
    if level == 1:
        separator = '====='
    else:
        separator = '+++'

    logger.info(separator + ' ' + date + ' - ' +
                args.name + ' - ' + text + ' ' + separator)


def backup_mysql(parser, args):
    """ Dump MySQL/MariaDB databases and rotate backup files """

    log_header(LOG_LEVEL_SECUNDARY, 'MySQL Backup')

    # Dump MySQL databases
    command = 'nice -n 20 mysqldump --all-databases --opt'

    # If args.db_user or args.db-pass are void the script take the values
    # from some of the default .cnf files: ~/.my.cnf or ~/.mylogin.cnf
    # See: https://dev.mysql.com/doc/refman/8.0/en/option-files.html
    if args.db_user is not None:
        command = command + ' -u ' + args.db_user
    if args.db_pass is not None:
        command = command + ' -p' + args.db_pass
    logger.debug(command)

    if args.type == LOCAL_TYPE:
        command = command + ' > ' + mysql_file
    elif args.type == REMOTE_TYPE:
        command = ('ssh -p ' + str(args.port) + ' '
                   + args.user + '@' + args.serv
                   + ' ' + command + ' > ' + mysql_file)

    logger.debug(command)
    exit_value = os.system(command)
    logger.debug('EXIT:' + str(exit_value))

    if (exit_value == EXIT_NO_ERROR):
        # Rotate backup files
        # First delete the last backup
        mysql_last = mysql_file + '.' + str(backup_days) + '.tar.gz'
        if os.path.exists(mysql_last):
            os.remove(mysql_last)
        # Rotate the rest of backups
        for i in range(backup_days - 1, 0, -1):
            mysql_source = mysql_file + '.' + str(i) + '.tar.gz'
            mysql_destination = mysql_file + '.' + str(i + 1) + '.tar.gz'
            if os.path.exists(mysql_source):
                os.rename(mysql_source, mysql_destination)

        # Compress the sql file
        os.system('tar -czPf ' + mysql_file + '.1.tar.gz ' + mysql_file)
        os.system('ls -lh ' + mysql_file + ' ' + mysql_file +
                  '.1.tar.gz >> ' + log_last)


def backup_sync(parser, args):
    """Syncronize files"""

    log_header(LOG_LEVEL_SECUNDARY, 'rsync copy')

    command = ("rsync -azh -e 'ssh -p " + str(args.port) +
               "' --exclude-from=" + exclude_file +
               ' --delete-after --force --stats ' +
               args.user + '@' + args.serv + ':' + args.copy_dir + ' ' +
               dir_sync + ' >> ' + log_last + ' 2>&1')

    logger.debug(command)
    os.system(command)


def backup_files(parser, args):
    log_header(2, 'rdiff-backup copy')

    if args.type == LOCAL_TYPE:
        dir_source = args.copy_dir
    elif args.type == REMOTE_TYPE:
        dir_source = dir_sync

    command = ('rdiff-backup --print-statistics ' + dir_source + ' '
               + dir_diff + ' >> ' + log_last + ' 2>&1')
    logger.debug(command)
    os.system(command)

    logger.info('-- ' + date + ' ' + args.name + ' - Deleting old '
                'rdiff-backup copies')
    command = ('rdiff-backup --remove-older-than $((' + str(backup_days)
               + '))D --force ' + dir_diff + ' >> ' + log_last + ' 2>&1')
    logger.debug(command)
    os.system(command)


if __name__ == "__main__":
    # Constants
    TYPES = [LOCAL_TYPE, REMOTE_TYPE] = ['local', 'remote']
    DATABASES = [DB_MYSQL] = ['mysql']

    LOG_LEVEL_PRIMARY = 1
    LOG_LEVEL_SECUNDARY = 2

    EXIT_NO_ERROR = 0
    EXIT_ARGPARSE_ERROR = -1

    # Calculated
    date = datetime.now().strftime('%d/%m/%Y-%H:%M')
    file_date = datetime.now().strftime('%Y%m%d')
    dir_script = os.path.dirname(os.path.realpath(__file__))

    # Read configuration file
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config.read(os.path.join(dir_script, 'backup.ini'))

    # Log CONFIG
    backup_days = int(config.get('CONFIG', 'BackupDays'))
    exclude_file = os.path.join(dir_script, config.get('CONFIG',
                                                       'ExcludeFile'))
    if config.get('CONFIG', 'Develop').upper() in ['Y', 'YES', '1']:
        error_level = logging.DEBUG
    else:
        error_level = logging.INFO

    # Log DIR
    dir_backup = config.get('DIR', 'DirBackup')
    dir_log = config.get('DIR', 'DirLog')

    parser, args = process_parameters()
    dir_base = os.path.join(dir_backup, args.name)
    dir_mysql = os.path.join(dir_base, 'mysql')
    dir_sync = os.path.join(dir_base, 'sync')
    dir_diff = os.path.join(dir_base, 'diff')
    mysql_file = os.path.join(dir_mysql, args.name + '.sql')
    log_last = os.path.join(dir_log, args.name + '.log')
    log_full = os.path.join(dir_log, args.name + '.full.log')

    check_directories(dir_log, dir_base, dir_mysql, dir_diff)

    # Logging

    # Empty last file log
    with open(log_last, 'w'):
        pass

    logging.basicConfig(
        format='%(levelname)s:%(message)s',
        filename=log_last,
        level=error_level)
    logger = logging.getLogger(__name__)

    log_header(1, 'BACKUP BEGIN')

    logger.debug(dir_script)
    logger.debug(exclude_file)
    logger.debug(dir_backup)
    logger.debug(dir_log)
    logger.debug(dir_base)
    logger.debug(dir_mysql)
    logger.debug(mysql_file)
    logger.debug(log_last)
    logger.debug(log_full)

    # MySQL Backup
    if args.database == DB_MYSQL:
        backup_mysql(parser, args)

    if args.type == REMOTE_TYPE:
        backup_sync(parser, args)

    backup_files(parser, args)

    log_header(LOG_LEVEL_PRIMARY, 'BACKUP END')
    logger.info('')

    # Concat log_last with log_full
    os.system('cat ' + log_last + ' >> ' + log_full)

    exit(0)

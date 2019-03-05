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

import configparser
import logging
import os
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import datetime

import constants as const


def process_parameters():
    """ Process the command line arguments and show the help """

    parser = ArgumentParser(
        description=const.SCRIPT_DESCRIPION,
        epilog=const.SCRIPT_EPILOG,
        formatter_class=RawTextHelpFormatter)

    for arg in const.ARGUMENTS:
        # if arg doesn't start with a "-" it's a positional argument
        # and doesn't accept a long version of the argument
        if arg[0][0] != '-':
            parser.add_argument(arg[0], **arg[1])
        else:
            parser.add_argument(arg[0], arg[1], **arg[2])

    try:
        args = parser.parse_args()
    except IOError as msg:
        parser.error(str(msg))
        sys.exit(const.EXIT_ARGPARSE_ERROR)

    # "remote" option require --serv and --user
    if args.type == const.REMOTE_TYPE:
        if (args.serv is None or args.user is None):
            parser.error('For "remote" type the parameters --serv '
                         'and --user are required')
            exit(const.EXIT_ARGPARSE_ERROR)

    if (args.db_server is None
        and (args.db_user is not None
             or args.db_pass is not None)):
        parser.error('Parameters --db-user or --db-pass '
                     'are not allowed if --db-server is not present')
        exit(const.EXIT_ARGPARSE_ERROR)

    # PostgreSQL databases
    if (args.db_server == const.DB_POSTGRESQL):
        # --db-pass is not allowed
        if args.db_pass is not None:
            parser.error('if --db-server value is "postgresql" the --db-pass '
                         'parameter is not allowed. '
                         'You must use ".pgpass" file.')
            exit(const.EXIT_ARGPARSE_ERROR)

        # --db-pass is not allowed
        if args.db_user is None or args.db_name is None:
            parser.error('if --db-server value is "postgresql" the --db-user '
                         'and --db-name parameters are required.')
            exit(const.EXIT_ARGPARSE_ERROR)

    return parser, args


def process_config():
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config_file = os.path.join(dir_script, const.CONFIG_FILE)

    # Check if config file exists and is readable
    if (not (os.path.isfile(config_file) and os.access(config_file, os.R_OK))):
        print(const.CONFIG_ERROR)  # TODO: change this for log to sdtout
        exit(const.EXIT_CONFIG_ERROR)

    config.read(config_file)

    return config


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

    log_header(const.LOG_LEVEL_SECUNDARY, 'MySQL Backup')

    # Dump MySQL databases
    command = 'nice -n 20 mysqldump --all-databases --opt'

    # If args.db_user or args.db_pass are empty the script take the values
    # from some of the default .cnf files: ~/.my.cnf or ~/.mylogin.cnf
    # See: https://dev.mysql.com/doc/refman/8.0/en/option-files.html
    if args.db_user is not None:
        command = command + ' -u ' + args.db_user
    if args.db_pass is not None:
        command = command + ' -p' + args.db_pass
    logger.debug(command)

    command = complete_command(command, mysql_file)

    logger.debug(command)
    exit_value = os.system(command)
    logger.debug('EXIT:' + str(exit_value))

    if (exit_value == const.EXIT_NO_ERROR):
        rotate_logs(mysql_file)


def backup_postgresql(parser, args):
    """ Dump PostgreSQL databases and rotate backup files """

    log_header(const.LOG_LEVEL_SECUNDARY, 'PostgreSQL Backup')

    # Dump MySQL databases
    command = 'nice -n 20 pg_dump ' + args.db_name

    # If args.db_user is empty the script takes the value
    # from .pgpass file
    # See: https://www.postgresql.org/docs/9.3/libpq-pgpass.html
    if args.db_user is not None:
        command = command + ' -U ' + args.db_user
    logger.debug(command)

    command = complete_command(command, postgresql_file)

    logger.debug(command)
    exit_value = os.system(command)
    logger.debug('EXIT:' + str(exit_value))

    if (exit_value == const.EXIT_NO_ERROR):
        rotate_logs(postgresql_file)


def complete_command(command, db_file):
    if args.type == const.LOCAL_TYPE:
        command = command + ' > ' + db_file
    elif args.type == const.REMOTE_TYPE:
        command = ('ssh -p ' + str(args.port) + ' '
                   + args.user + '@' + args.serv
                   + ' ' + command + ' > ' + db_file)
    return command


def rotate_logs(db_file):
    # Rotate backup files
    # First delete the last backup
    db_last = db_file + '.' + str(backup_days) + '.tar.gz'
    if os.path.exists(db_last):
        os.remove(db_last)
    # Rotate the rest of backups
    for i in range(backup_days - 1, 0, -1):
        db_source = db_file + '.' + str(i) + '.tar.gz'
        db_destination = db_file + '.' + str(i + 1) + '.tar.gz'
        if os.path.exists(db_source):
            os.rename(db_source, db_destination)

    # Compress the sql file
    os.system('tar -czPf ' + db_file + '.1.tar.gz ' + db_file)
    os.system('ls -lh ' + db_file + ' ' + db_file +
              '.1.tar.gz >> ' + log_last)


def backup_sync(parser, args):
    """Syncronize files"""

    log_header(const.LOG_LEVEL_SECUNDARY, 'rsync copy')

    command = ("rsync -azh -e 'ssh -p " + str(args.port) +
               "' --exclude-from=" + exclude_file +
               ' --delete-after --force --stats ' +
               args.user + '@' + args.serv + ':' + args.copy_dir + ' ' +
               dir_sync + ' >> ' + log_last + ' 2>&1')

    logger.debug(command)
    os.system(command)


def backup_files(parser, args):
    log_header(2, 'rdiff-backup copy')

    if args.type == const.LOCAL_TYPE:
        dir_source = args.copy_dir
    elif args.type == const.REMOTE_TYPE:
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
    # Calculated
    date = datetime.now().strftime('%d/%m/%Y-%H:%M')
    file_date = datetime.now().strftime('%Y%m%d')
    dir_script = os.path.dirname(os.path.realpath(__file__))

    # Read configuration file
    config = process_config()

    try:
        # Log CONFIG
        backup_days = int(config.get('CONFIG', 'BackupDays'))
        exclude_file = os.path.join(dir_script, config.get('CONFIG',
                                                           'ExcludeFile'))
        if config.get('CONFIG', 'Develop').upper() in const.OPTION_YES:
            error_level = logging.DEBUG
        else:
            error_level = logging.INFO

        # Log DIR
        dir_backup = config.get('DIR', 'DirBackup')
        dir_log = config.get('DIR', 'DirLog')
    except configparser.Error as e:
        print(e.message)  # TODO: change this for log to sdtout
        exit(const.EXIT_CONFIG_ERROR)

    # Parameters
    parser, args = process_parameters()
    dir_base = os.path.join(dir_backup, args.name)
    dir_mysql = os.path.join(dir_base, 'mysql')
    dir_postgresql = os.path.join(dir_base, 'postgresql')
    dir_sync = os.path.join(dir_base, 'sync')
    dir_diff = os.path.join(dir_base, 'diff')
    mysql_file = os.path.join(dir_mysql, args.name + '.sql')
    postgresql_file = os.path.join(dir_postgresql, args.name + '.sql')
    log_last = os.path.join(dir_log, args.name + '.log')
    log_full = os.path.join(dir_log, args.name + '.full.log')

    check_directories(dir_log, dir_base, dir_mysql, dir_postgresql, dir_diff)

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
    if args.db_server == const.DB_MYSQL:
        backup_mysql(parser, args)
    elif args.db_server == const.DB_POSTGRESQL:
        backup_postgresql(parser, args)

    if args.type == const.REMOTE_TYPE:
        backup_sync(parser, args)

    backup_files(parser, args)

    log_header(const.LOG_LEVEL_PRIMARY, 'BACKUP END')
    logger.info('')

    # Concat log_last with log_full
    os.system('cat ' + log_last + ' >> ' + log_full)

    exit(0)

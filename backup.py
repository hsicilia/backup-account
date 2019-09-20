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
import databases
import log


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

    return args


def process_env():
    env = {}

    # General calculated fields
    env['date'] = datetime.now().strftime('%d/%m/%Y-%H:%M')
    env['file_date'] = datetime.now().strftime('%Y%m%d')
    env['dir_script'] = os.path.dirname(os.path.realpath(__file__))

    # Read configuration file
    config = read_config(env)

    try:
        env['backup_days'] = int(config.get('CONFIG', 'BackupDays'))
        env['exclude_file'] = os.path.join(env['dir_script'],
                                           config.get('CONFIG',
                                                      'ExcludeFile'))
        if config.get('CONFIG', 'Develop').upper() in const.OPTION_YES:
            env['error_level'] = logging.DEBUG
        else:
            env['error_level'] = logging.INFO

        env['dir_backup'] = config.get('DIR', 'DirBackup')
        env['dir_log'] = config.get('DIR', 'DirLog')
    except configparser.Error as e:
        print(const.CONFIG_ERROR + e.message)  # TODO: log to sdtout
        exit(const.EXIT_CONFIG_ERROR)

    # Calculated fields
    env['dir_base'] = os.path.join(env['dir_backup'], args.name)
    env['dir_mysql'] = os.path.join(env['dir_base'], 'mysql')
    env['dir_postgresql'] = os.path.join(env['dir_base'], 'postgresql')
    env['dir_sync'] = os.path.join(env['dir_base'], 'sync')
    env['dir_diff'] = os.path.join(env['dir_base'], 'diff')
    env['log_last'] = os.path.join(env['dir_log'], args.name + '.log')
    env['log_full'] = os.path.join(env['dir_log'], args.name + '.full.log')

    # Database fields
    if args.db_server == const.DB_MYSQL:
        env['dir_db'] = env['dir_mysql']
        env['db_system'] = 'MySQL'
    elif args.db_server == const.DB_POSTGRESQL:
        env['dir_db'] = env['dir_postgresql']
        env['db_system'] = 'PostgreSQL'

    if args.db_server is not None:
        env['db_filename'] = args.name + '.sql'
        env['db_url'] = os.path.join(env['dir_db'], env['db_filename'])

    return env


def read_config(env):
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config_file = os.path.join(env['dir_script'], const.CONFIG_FILE)

    # Check if config file exists and is readable
    if (not (os.path.isfile(config_file) and os.access(config_file, os.R_OK))):
        print(const.CONFIG_NOT_FOUND_ERROR)  # TODO: log to sdtout
        exit(const.EXIT_CONFIG_ERROR)

    try:
        config.read(config_file)
    except configparser.Error as e:
        print(const.CONFIG_ERROR + e.message)  # TODO: log to sdtout
        exit(const.EXIT_CONFIG_ERROR)

    return config


def check_directories():
    """ Check if all the necessary directories are created """

    create_directories(env['dir_log'],
                       env['dir_base'],
                       env['dir_diff'])

    if args.db_server is not None:
        create_directories(env['dir_db'])


def create_directories(*directories):
    """ If directory doesn't exist, create it """

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def backup_sync():
    """Syncronize files"""

    log.log_separator(const.LOG_LEVEL_SECUNDARY, 'rsync copy')

    command = ("rsync -azh -e 'ssh -p " + str(args.port) +
               "' --exclude-from=" + env['exclude_file'] +
               ' --delete-after --force --stats ' +
               args.user + '@' + args.serv + ':' + args.copy_dir + ' ' +
               env['dir_sync'] + ' >> ' + env['log_last'] + ' 2>&1')

    logger.debug(command)
    os.system(command)


def backup_files():
    log.log_separator(const.LOG_LEVEL_SECUNDARY, 'rdiff-backup copy')

    if args.type == const.LOCAL_TYPE:
        dir_source = args.copy_dir
    elif args.type == const.REMOTE_TYPE:
        dir_source = env['dir_sync']

    command = ('rdiff-backup --print-statistics ' + dir_source + ' '
               + env['dir_diff'] + ' >> ' + env['log_last'] + ' 2>&1')
    logger.debug(command)
    os.system(command)

    logger.info('-- ' + env['date'] + ' ' + args.name + ' - Deleting old '
                'rdiff-backup copies')
    command = ('rdiff-backup --remove-older-than $((' + str(env['backup_days'])
               + '))D --force ' + env['dir_diff'] + ' >> '
               + env['log_last'] + ' 2>&1')
    logger.debug(command)
    os.system(command)


if __name__ == "__main__":

    # Store script parameters
    args = process_parameters()

    # Store configuration and other calculated fields at "env" dictionary
    env = process_env()

    # Initializing log
    logger = logging.getLogger(__name__)
    log.config_log()

    check_directories()

    log.log_start()

    if args.db_server is not None:
        databases.backup_db()

    if args.type == const.REMOTE_TYPE:
        backup_sync()

    backup_files()

    log.log_end()

    exit(0)

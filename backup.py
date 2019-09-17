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
import shutil
import sys
import tarfile
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


def backup_db():
    """ Dump database and rotate backup files """

    log_separator(const.LOG_LEVEL_SECUNDARY,
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


def backup_sync():
    """Syncronize files"""

    log_separator(const.LOG_LEVEL_SECUNDARY, 'rsync copy')

    command = ("rsync -azh -e 'ssh -p " + str(args.port) +
               "' --exclude-from=" + env['exclude_file'] +
               ' --delete-after --force --stats ' +
               args.user + '@' + args.serv + ':' + args.copy_dir + ' ' +
               env['dir_sync'] + ' >> ' + env['log_last'] + ' 2>&1')

    logger.debug(command)
    os.system(command)


def backup_files():
    log_separator(const.LOG_LEVEL_SECUNDARY, 'rdiff-backup copy')

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
    config_log()

    check_directories()

    log_start()

    if args.db_server is not None:
        backup_db()

    if args.type == const.REMOTE_TYPE:
        backup_sync()

    backup_files()

    log_end()

    exit(0)

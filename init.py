#!/usr/bin/env python3
"""
Initialization functions

This source code Form is subject to the terms of the GNU Affero
General Public License, version 3 (AGPLv3).
If a copy of the AGPLv3 was not distributed with this file, you can
obtain one at https://www.gnu.org/licenses/agpl-3.0.html.
"""

import configparser
import logging
import os
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import datetime

import config as cfg


logger = logging.getLogger(__name__)


def process_parameters():
    """ Process the command line arguments, store them at cfg.args
       and show the help """

    parser = ArgumentParser(
        description=cfg.SCRIPT_DESCRIPION,
        epilog=cfg.SCRIPT_EPILOG,
        formatter_class=RawTextHelpFormatter)

    for arg in cfg.ARGUMENTS:
        # if arg doesn't start with a "-" it's a positional argument
        # and doesn't accept a long version of the argument
        if arg[0][0] != '-':
            parser.add_argument(arg[0], **arg[1])
        else:
            parser.add_argument(arg[0], arg[1], **arg[2])

    try:
        cfg.args = parser.parse_args()
    except IOError as msg:
        parser.error(str(msg))
        sys.exit(cfg.EXIT_ERROR_ARGPARSE)

    # "remote" option require --serv and --user
    if cfg.args.type == cfg.REMOTE_TYPE:
        if (cfg.args.serv is None or cfg.args.user is None):
            parser.error(cfg.ARGPARSE_ERROR_PARAMS_REQUIRED_REMOTE)
            exit(cfg.EXIT_ERROR_ARGPARSE)

    if (cfg.args.db_server is None
        and (cfg.args.db_user is not None
             or cfg.args.db_pass is not None)):
        parser.error(cfg.ARGPARSE_ERROR_PARAMS_NOT_ALLOWED_SERVER)
        exit(cfg.EXIT_ERROR_ARGPARSE)

    # PostgreSQL databases
    if (cfg.args.db_server == cfg.DB_POSTGRESQL):
        # --db-pass is not allowed
        if cfg.args.db_pass is not None:
            parser.error(cfg.ARGPARSE_ERROR_DBPASS_NOT_ALLOWED_POSTGRESQL)
            exit(cfg.EXIT_ERROR_ARGPARSE)

        # --db-pass is not allowed
        if cfg.args.db_user is None or cfg.args.db_name is None:
            parser.error(cfg.ARGPARSE_ERROR_PARAMS_REQUIRED_POSTGRESQL)
            exit(cfg.EXIT_ERROR_ARGPARSE)


def process_env():
    """ Store configuration and other calculated fields at cfg.env """

    # General calculated fields
    cfg.env['date'] = datetime.now().strftime('%d/%m/%Y-%H:%M')
    cfg.env['file_date'] = datetime.now().strftime('%Y%m%d')
    cfg.env['dir_script'] = os.path.dirname(os.path.realpath(__file__))

    # Read configuration file
    config = read_config_file()

    try:
        cfg.env['backup_days'] = int(config.get('CONFIG', 'BackupDays'))
        cfg.env['exclude_file'] = os.path.join(cfg.env['dir_script'],
                                               config.get('CONFIG',
                                                          'ExcludeFile'))
        if config.get('CONFIG', 'Develop').upper() in cfg.OPTION_YES:
            cfg.env['error_level'] = logging.DEBUG
        else:
            cfg.env['error_level'] = logging.INFO

        cfg.env['dir_backup'] = config.get('DIR', 'DirBackup')
        cfg.env['dir_log'] = config.get('DIR', 'DirLog')
    except configparser.Error as e:
        print(cfg.ERROR_CONFIG + e.message)  # TODO: log to sdtout
        exit(cfg.EXIT_CONFIG_ERROR)

    # Calculated fields
    cfg.env['dir_base'] = os.path.join(cfg.env['dir_backup'], cfg.args.name)
    cfg.env['dir_mysql'] = os.path.join(cfg.env['dir_base'], 'mysql')
    cfg.env['dir_postgresql'] = os.path.join(cfg.env['dir_base'], 'postgresql')
    cfg.env['dir_sync'] = os.path.join(cfg.env['dir_base'], 'sync')
    cfg.env['dir_diff'] = os.path.join(cfg.env['dir_base'], 'diff')
    cfg.env['log_last'] = os.path.join(cfg.env['dir_log'],
                                       cfg.args.name + '.log')
    cfg.env['log_full'] = os.path.join(cfg.env['dir_log'],
                                       cfg.args.name + '.full.log')

    # Database fields
    if cfg.args.db_server == cfg.DB_MYSQL:
        cfg.env['dir_db'] = cfg.env['dir_mysql']
        cfg.env['db_system'] = 'MySQL'
    elif cfg.args.db_server == cfg.DB_POSTGRESQL:
        cfg.env['dir_db'] = cfg.env['dir_postgresql']
        cfg.env['db_system'] = 'PostgreSQL'

    if cfg.args.db_server is not None:
        cfg.env['db_filename'] = cfg.args.name + '.sql'
        cfg.env['db_url'] = os.path.join(cfg.env['dir_db'],
                                         cfg.env['db_filename'])


def read_config_file():
    """ Process config file parameters """

    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    config_file = os.path.join(cfg.env['dir_script'], cfg.CONFIG_FILE)

    # Check if config file exists and is readable
    if (not (os.path.isfile(config_file) and os.access(config_file, os.R_OK))):
        print(cfg.ERROR_CONFIG_NOT_FOUND)  # TODO: log to sdtout
        exit(cfg.EXIT_ERROR_CONFIG)

    try:
        config.read(config_file)
    except configparser.Error as e:
        print(cfg.ERROR_CONFIG + e.message)  # TODO: log to sdtout
        exit(cfg.EXIT_ERROR_CONFIG)

    return config


def check_directories():
    """ Check if all the necessary directories are created """

    create_directories(cfg.env['dir_log'],
                       cfg.env['dir_base'],
                       cfg.env['dir_diff'])

    if cfg.args.db_server is not None:
        create_directories(cfg.env['dir_db'])


def create_directories(*directories):
    """ If directory doesn't exist, create it """

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


if __name__ == "__main__":
    print(cfg.ERROR_WRONG_MODULE)

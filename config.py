#!/usr/bin/env python3
"""
Program configuration variables and constants.

This source code Form is subject to the terms of the GNU Affero
General Public License, version 3 (AGPLv3).
If a copy of the AGPLv3 was not distributed with this file, you can
obtain one at https://www.gnu.org/licenses/agpl-3.0.html.
"""

args = None  # Store script parameters

env = {}  # Store configuration and other calculated fields


# --Constants--

# -Log-
LOG_LEVEL_PRIMARY = 1
LOG_LEVEL_SECUNDARY = 2

# -Config-
CONFIG_FILE = 'backup.ini'

# Options
OPTION_YES = ['Y', 'YES', '1']

# -Argparse-
SCRIPT_DESCRIPION = ('Decremental backup of directories and '
                     'databases from local or remote server.')
SCRIPT_EPILOG = ('''
Consult README.md for a more detailed description.
Web: https://github.com/hsicilia/backup-account
                 ''')

TYPES = [LOCAL_TYPE, REMOTE_TYPE] = ['local', 'remote']
DATABASES = [DB_MYSQL, DB_POSTGRESQL] = ['mysql', 'postgresql']

# List of argparse arguments
# [short, large, {named arguments}]
ARGUMENTS = [
    ['type', {'help': 'type of backup', 'choices': TYPES}],
    ['-n', '--name', {'help': 'copy name', 'required': True}],
    ['-s', '--serv', {'help': 'remote server URL'}],
    ['-u', '--user', {'help': 'remote server user'}],
    ['-p', '--port',
        {'help': 'remote server port', 'type': int, 'default': 22}],
    ['-c', '--copy-dir', {'help': 'copy directory', 'required': True}],
    ['-b', '--db-server',
        {'help': 'activate database backup and select database server',
            'choices': DATABASES}],
    ['-e', '--db-user', {'help': 'database user'}],
    ['-w', '--db-pass', {'help': 'database user password'}],
    ['-d', '--db-name', {'help': 'database name'}]
]

# Argparse errors
ARGPARSE_ERROR_PARAMS_REQUIRED_REMOTE = ('For "remote" type the parameters '
                                        '--serv and --user are required')
ARGPARSE_ERROR_PARAMS_NOT_ALLOWED_SERVER = ('Parameters --db-user or '
                                            '--db-pass are not allowed if '
                                            '--db-server is not present')
ARGPARSE_ERROR_DBPASS_NOT_ALLOWED_POSTGRESQL = ('if --db-server value is '
                                                '"postgresql" the --db-pass '
                                                'parameter is not allowed. '
                                                'You must use ".pgpass" file.')
ARGPARSE_ERROR_PARAMS_REQUIRED_POSTGRESQL = ('if --db-server value is '
                                             '"postgresql" the --db-user '
                                             'and --db-name parameters are'
                                             'required.')

# -Exit codes-
EXIT_NO_ERROR = 0
EXIT_ERROR_ARGPARSE = -1
EXIT_ERROR_CONFIG = -2

# -Error messages-
ERROR_CONFIG_NOT_FOUND = ('ERROR. Config file "' + CONFIG_FILE
                          + '" not found (or not readable). '
                          + 'You can copy "' + CONFIG_FILE + '.dist" to "'
                          + CONFIG_FILE
                          + '" and edit it.')
ERROR_CONFIG = 'ERROR. Config file error: '
ERROR_WRONG_MODULE = "ERROR. Thie module can't be the main one"


# -File constants-

EXT_COMPRESS_FILE = '.tar.gz'


if __name__ == "__main__":
    print(ERROR_WRONG_MODULE)

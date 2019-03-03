#!/usr/bin/env python3
"""
Program constants.

This source code Form is subject to the terms of the GNU Affero
General Public License, version 3 (AGPLv3).
If a copy of the AGPLv3 was not distributed with this file, you can
obtain one at https://www.gnu.org/licenses/agpl-3.0.html.
"""

# Constants
TYPES = [LOCAL_TYPE, REMOTE_TYPE] = ['local', 'remote']
DATABASES = [DB_MYSQL, DB_POSTGRESQL] = ['mysql', 'postgresql']

LOG_LEVEL_PRIMARY = 1
LOG_LEVEL_SECUNDARY = 2

EXIT_NO_ERROR = 0
EXIT_ARGPARSE_ERROR = -1

# Options
OPTION_YES = ['Y', 'YES', '1']

# Argparse

SCRIPT_DESCRIPION = ('Decremental backup of directories and '
                     'databases from local or remote server.')
SCRIPT_EPILOG = ('''
Consult README.md for a more detailed description.
Web: https://github.com/hsicilia/backup-account
                 ''')
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

if __name__ == "__main__":
    print("Error. This module can't be the main one")

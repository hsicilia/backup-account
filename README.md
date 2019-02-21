# backup-account

A Python3 script to backup copies of local or remote directories and MySQL/MariaDB databases.

## Getting Started

### Prerequisites

  - Python3
  - ssh
  - rsync
  - [rdiff-backup](https://github.com/sol1/rdiff-backup)

### Installing

  * Install prerequisites and clone the repository.
  * Copy *backup.ini.dist* to *backup.ini* and modify the options.
  * If you want to exclude files from backup: uncomment the option in *backup.ini* and create an exclude file or copy *exclude-file.dist* to *exclude-file*.
  * For remote backup you must check that the *ssh* connection to the remote server is available with a key, without any password.

## Use
  * Execute *./backup.py* with the following arguments:
    * Type of backup:
      * **local** or **remote**: select one of them
    * Remote arguments:
      * **-s**/**--server**: remote server URL
      * **-u**/**--user**: remote server user
      * **-p**/**--port**: remote server port
    * Common arguments:
      * **-n**/**--name**: backup destination directory name
      * **-d**/**--copy-dir**: backup source directory to copy
      * **-h**/**--help**: show the help
    * MySQL arguments:
      * **-m**/**--mysql-user**: MySQL user
      * **-w**/**--mysql-pass**: MySQL password
  * Example of local backup: *./backup.py local -n localcopy -d /home/user/dirtocopy*
  * Example of local backup with MySQL: *./backup.py local -n localcopy -d /home/user/dirtocopy -m mysqluser -w mysqlpassword*
  * Example of remote backup with MySQL: *./backup.py remote -n localcopy -s server.com -u user -p 22 -d /home/user/dirtocopy -m mysqluser -w mysqlpassword*

## Author

* **Héctor Sicilia** - [hsicilia](https://github.com/hsicilia)

## License

This project is licensed under the *GNU Affero General Public License, version 3* - see the [LICENSE.md](LICENSE.md) file for details

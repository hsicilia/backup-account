# backup-account

A Python3 script to backup copies of local or remote directories and MySQL/MariaDB and PostgreSQL databases.

## Getting Started

### Prerequisites

- Python3
- ssh
- rsync
- [rdiff-backup](https://github.com/rdiff-backup/rdiff-backup)

### Installing

- Install prerequisites and clone the repository.
- Copy *backup.ini.dist* to *backup.ini* and modify the options.
- If you want to exclude files from backup: uncomment the option in *backup.ini* and create an exclude file or copy 
*exclude-file.dist* to *exclude-file*.
- For remote backup you must check that the *ssh* connection to the remote server is available with a key, without any
password.

## Use

- Execute *./backup.py* with the following arguments:
  - Type of backup:
    - **local** or **remote**: select one of them
  - Common arguments:
    - **-n**/**--name**: backup destination directory name
    - **-c**/**--copy-dir**: backup source directory to copy
    - **-h**/**--help**: shows the help
  - Remote arguments (use only with *remote* backup):
    - **-s**/**--server**: remote server URL
    - **-u**/**--user**: remote server user
    - **-p**/**--port**: remote server port
  - Database arguments:
    - **-b**/**--db-server** <database server>: can be *mysql* or *postgresql*.
    - **-d**/**--db-name**: Database name
    - **-e**/**--db-user**: Database user
    - **-w**/**--db-pass**: Database user password
- Example of local backup: *./backup.py local -n localcopy -c /home/user/dirtocopy*
- Example of local backup with MySQL: *./backup.py local -n localcopy -c /home/user/dirtocopy -b mysql -m mysqluser -w mysqlpassword*
- Example of remote backup with MySQL and *.cnf* configuration file: *./backup.py remote -n remotecopy -s server.com -u user -p 22 -c /home/user/dirtocopy -b mysql*
- Example of remote backup with PostgreSQL and *.pgpass* file: *./backup.py remote -n remotecopy -s server.com -u user -p 22 -c /home/user/dirtocopy -b postgresql -d database*

### Databases

There are four parameters that controls the database backup:

- **-b**/**--db-server**: *mysql* or *postgresql*. Is mandatory if you want to make a database backup.

#### MySQL/MariaDB

- **-e**/**--db-user** and **-w**/**--db-pass**: optionals. If you don't add any of them *mysqldump* will try to get the
 information automatically from the files *~/.my.cnf* or *~/.mylogin.cnf*.
- **-d**/**--db-name**: optional. If you don't add it *mysqldump* try to backup all databases from this user.

*.my.cnf* file must be in the user's home directory (local or remote, depending on the type of backup) and the content should look similar to this:

~~~~cnf
[mysqldump]
user=myuser
password="mypassword"
~~~~

#### PostgreSQL

- **-d**/**--db-name**: required
- **-e**/**--db-user**: required

With PostgreSQL database you must use a *.pgpass* file. It must be in the user's home directory (local or remote, depending on the type of backup) with
 0600 permission and the content should looks similar to this:

~~~~postgresql
localhost:5432:db_name:user:password
~~~~

where *localhost* is the server and *5432* the standard PostgreSQL port.

[More information](https://www.postgresql.org/docs/11/libpq-pgpass.html) about pgpass file.

## Author

- **Héctor Sicilia** - [hsicilia](https://github.com/hsicilia)

## License

This project is licensed under the *GNU Affero General Public License, version 3* - see the [LICENSE.md](LICENSE.md) file for details

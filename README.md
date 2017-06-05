# WIP: Pipper

__This is a Work In Progress. Stay tuned if you're interested.__

An experimental Python package manager wrapped around pip for lightweight
management of non-public packages with an AWS S3 static backend. Requires no
server or database resources, only a private S3 bucket that stores the pipper
packages. Authentication is handled using standard AWS Identity and Access
Management (IAM) users, roles and policies.


## Installing pipper

The pipper package can be installed by pip:

    $ pip install pipper


## Basic Usage

Pipper is primarily used from the command line and consists of multiple 
sub-command actions. The general format of a pipper command is:

    $ pipper <ACTION> <REQUIRED_ARGS> --flag=<VALUE> --other-flag ...

The available actions are:

 * [install](#install-action): add or update new packages
 * [download](#download-action): save remote packages locally
 * [info](#info-action): information on a specific package
 * [bundle](#bundle-action): bundle a package for publishing
 * [publish](#publish-action): release a new or updated package
 * [authorize](#authorize-action): create a pre-authorized url for download

    
## AWS Credentials

Pipper uses AWS credentials for authentication. These credentials can be 
specified in a number of ways. There are two command flags for specifying 
credentials:

* `-p --profile <AWS_PROFILE_NAME>`

    Use AWS credentials to authorize the package download. The
    'default' profile will be used if this flag is not specified.

* `-c --credentials <AWS_ACCESS_KEY_ID> <AWS_SECRET> <AWS_SESSION_TOKEN>`

    Allows you to specify the AWS credentials directly instead of by
    a named profile. Useful for situations where profiles are not
    initialized or undesirable. If your credentials do not require a session
    token, use a `*` character for the `<AWS_SESSION_TOKEN>` argument.
    
If neither of these flags is specified, pipper will look for the credentials
in pipper-specific environmental variables `PIPPER_AWS_ACCESS_KEY_ID`, 
`PIPPER_AWS_SECRET_ACCESS_KEY`  and `PIPPER_AWS_SESSION_TOKEN`. If those 
environmental variables do not exist, pipper will attempt to use the standard
AWS environmental variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and 
`AWS_SESSION_TOKEN`. If neither set of environmental variables exist, pipper
will fallback to using the _default_ profile credentials if they exist.


## Install Action

The pipper command can be used to install packages directly from the command
lin in much the same way you install packages with pip. The command is
followed by one or more packages to install. Specific package versions can be
downloaded by appending the version to package names with a colon separator.

    $ pipper install <PACKAGE_NAME[:VERSION]> <PACKAGE_NAME[:VERSION]>

There are a number of flags available to modify how the install command
functions:

* `-b --bucket <BUCKET_NAME>`

    Name of the S3 bucket where the remote pipper files are stored.

* `-i --input <INPUT_FILE>`

    Allows you to load one or more packages from a pipper-formatted
    JSON file. Use this in place of specifying the packages directly
    in the command when convenient.
    
* `-u --upgrade`

    When specified currently installed packages will be updated to the latest
    version. If this flag is not specified the installation process will
    ignore already installed packages, even if a newer version is available.

When installing pipper packages, pipper dependencies are handled recursively as
long as the dependency packages have a properly configured pipper.json file
located at the top-level of the repository.

### Installation Examples

    $ pipper install foo --bucket my_bucket --profile my_profile

Installs the `foo` package using the default AWS credentials associated with
the _my_profile_ AWS profile from the _my_bucket_ S3 bucket.


## Download Action

The download action can be used to download pipper packages for later use. This
can be helpful if you want to make packages available while offline or when
AWS credentials are unavailable.

    $ pipper download <PACKAGE_NAME[:VERSION]>

* `-b --bucket <BUCKET_NAME>`

    Name of the S3 bucket where the remote pipper files are stored.

* `-d --directory`

    The directory where the pipper bundle file for the package should be
    saved to when downloaded.

* `-i --input <INPUT_FILE>`

    Allows you to download one or more packages from a pipper-formatted
    JSON file. Use this in place of specifying the packages directly
    in the command when convenient.


## Authorize Action

There are times when having AWS credentials available isn't practical. To get
around those you can create pre-authorized URLs for downloading and installing
packages that can be used where credentials are not available.

    $ pipper authorize <PACKAGE_NAME[:VERSION]> ...
    
* `-b --bucket <BUCKET_NAME>`

    Name of the S3 bucket where the remote pipper files are stored.

* `-i --input <INPUT_FILE>`

    Allows you to load one or more packages from a pipper-formatted
    JSON file. Use this in place of specifying the packages directly
    in the command when convenient.

* `-o --ouput <OUTPUT_FILE>`

    If specified, a pre-authorized pipper config file will be written that
    can be used later by download and installation commands.


## Info Action

Prints information on the locally installed and remote versions of the 
specified package. Also, informs you if there is a newer version of the package
available for upgrade.

    $ pipper info <PACKAGE_NAME>

* `-l --local`

    Only display local package information, which can be useful if you're
    just looking for what is installed locally and don't want to provide
    AWS credential information as well.

* `-b --bucket <BUCKET_NAME>`

    Name of the S3 bucket where the remote pipper files are stored. This
    flag is needed unless the local flag is used, which does not communicate
    with the remote S3 files.


## Bundle Action

Creates a pipper package distribution file that can be installed directly or
published to a remote S3 bucket for distribution.

    $ pipper bundle <PACKAGE_DIRECTORY>
    
* `-o --output <OUTPUT_DIRECTORY>`

    The directory where the pipper bundle should be saved. Defaults to the 
    current working directory.
    
    
## Publish Action

Deploys a pipper bundle file to a remote S3 bucket for distribution.

    $ pipper publish <PIPPER_FILENAME>
    
If you specify a directory instead of a filename, pipper will search for a
pipper file in that directory and upload it. If multiple pipper files are
found, the most recently created one will be uploaded.
    
    $ pipper publish <DIRECTORY_CONTAINING_PIPPER_FILE>

* `-b --bucket <BUCKET_NAME>`
    
    Name of the S3 bucket where the package will be published.

* `-f --force`
    
    Unless this flag is specified, publishing a package will be skipped if an
    identical version of the package has already been published.

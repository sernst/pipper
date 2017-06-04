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

 * [install](#Install-Action): add or update new packages
 * [download](#Download-Action): save remote packages locally
 * [info](#Info-Action): information on a specific package
 * [bundle](#Bundle-Action): bundle a package for publishing
 * [publish](#Publish-Action): release a new or updated package

    pipper download some_package
    pipper download -i pipper.json
        -d ~/target/directory

    pipper info PACKAGE_NAME

    pipper bundle .

    pipper publish

    
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
in the environmental variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` 
and `AWS_SESSION_TOKEN`. If those environmental variables do not exist, pipper
will fallback to using the _default_ profile credentials if they exist.


## Install Action

The pipper command can be used to install packages directly from the command
lin in much the same way you install packages with pip. The command is
followed by one or more packages to install. Specific package versions can be
downloaded by appending the version to package names with a colon separator.

    $ pipper install <PACKAGE_NAME[:VERSION]> <PACKAGE_NAME[:VERSION]>

There are a number of flags available to modify how the install command
functions:

* `-i --input <INPUT_FILE>`

    Allows you to load one or more packages from a pipper-formatted
    JSON file. Use this in place of specifying the packages directly
    in the command when convenient.

When installing pipper packages, pipper dependencies are handled recursively as
long as the dependency packages have a properly configured pipper.json file
located at the top-level of the repository.

### Installation Examples

```bash
$ pipper install foo
```
Installs the `foo` package using the default AWS credentials


Use credentials from within container when calling pipper
TODO: pipper should allow env variables in addition to profile
Install during docker build

Install during Gitlab CI


## Bundle Action


    $ pipper bundle <PACKAGE_DIRECTORY>
    
* `-o --output <OUTPUT_DIRECTORY>`

    The directory where the pipper bundle should be saved. Defaults to the 
    current working directory.
    
## Publish Action

    $ pipper publish <PIPPER_FILENAME>
    
    $ pipper publish <DIRECTORY_CONTAINING_PIPPER_FILE>


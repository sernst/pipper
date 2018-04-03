# Pipper

__Private Python package manager on an S3 bucket__

An experimental Python package manager wrapped around pip for lightweight
management of non-public packages with an AWS S3 static backend. Requires no
server or database resources, only a private S3 bucket that stores the pipper
packages. Authentication is handled using standard AWS Identity and Access
Management (IAM) users, roles and policies.


## Installing pipper

The pipper package can be installed using pip:

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
 * [repository](#repository-action): Modify pre-defined pipper repositories

    
## AWS Credentials

Pipper uses AWS credentials for authentication. To maximize flexibility, the 
AWS credentials can be specified in a myriad of ways. Pipper will try to
identify credentials in the following order:

__1. Explicit Credentials:__ You can specify the AWS credentials directly on
the command line with the `--credentials` flag:

* `-c --credentials <AWS_ACCESS_KEY_ID> <AWS_SECRET> <AWS_SESSION_TOKEN>`

This can be useful for situations where profiles are not initialized or 
undesirable. If your credentials do not require a session token, which is
usually the case, that argument can be omitted. It's also possible to specify
a missing token using a `0` value for the `<AWS_SESSION_TOKEN>` argument for
simplicity in cases where omitting the value is more difficult than including
it with an explicit ignore value.


__2. Pipper Configuration:__ Using pipper's _repository_ command action, you can store credentials and
remote information in a pipper config file. If you do create a pipper
repository configuration, which stores AWS credentials, you can reference
that repository configuration by name to provide credentials to the 
various commands with the `--repository` command flag:

* `-r --repository <PIPPER_REPOSITORY_NAME>`

For more information on how to specify repository configurations for use with
this flag, see the [repository](#repository-action). This is the recommended
way to specify credentials for persistent environments like your local computer.

__3. AWS Profiles:__ Standard AWS profile-based credentials can be used as 
well. Use the `--profile` flag to specify the name of the profile you wish
to use:

* `-p --profile <AWS_PROFILE_NAME>`
 
__4. Pipper Environmental Variables:__ If none of the previous forms of 
credentials are provided, pipper will try to use pipper-specific environmental 
variables:

`PIPPER_AWS_ACCESS_KEY_ID`
     
`PIPPER_AWS_SECRET_ACCESS_KEY`  

`PIPPER_AWS_SESSION_TOKEN`

__5. AWS Environmental Variables:__ If none of the previous forms of credentials
are provided, pipper will attempt to use the standard AWS environmental 
variables:

`AWS_ACCESS_KEY_ID` 

`AWS_SECRET_ACCESS_KEY`

`AWS_SESSION_TOKEN`

If neither set of environmental variables exist, pipper
will fallback to using the _default_ profile credentials if they exist.

__6. Default Pipper Repository Configuration:__ If none of the other 
credentials are specified, pipper will try to use the default repository
configuration if one exists.

__7. System-level credentials:__ In the end, pipper will try to use the 
default system-level credentials, which is useful in situations like EC2
instances where the credentials are baked into the instance. However, on
remote systems the lack of specified credentials will likely result in 
authorization exceptions.


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

* `-d --directory <DIRECTORY_NAME>`

    The directory where the pipper bundle file for the package should be
    saved to when downloaded.

* `-i --input <INPUT_FILE>`

    Allows you to download one or more packages from a pipper-formatted
    JSON file. Use this in place of specifying the packages directly
    in the command when convenient.

* `-e --extract`

    When specified, the downloaded pipper files will be immediately extracted
    into their consituent wheel and metadata files. Useful if you want to 
    install directly with pip using advanced options such as installing to
    a specific directly.


## Repository Action

The repository action allows you to create and managed named repositories, 
which can be used to simplify the management of credentials within the 
command line. The repository command action has a number of sub-actions:


### Repository: add

    $ pipper repository add <REPOSITORY_NAME>

Adds a new repository configuration with the specified name. Use the 
`-p --profile` or `-c --credentials` flag to specify the AWS credentials to
be used by this repository. The _add_ sub-action has other flags:

* `-b --bucket <BUCKET_NAME>`

    Name of the S3 bucket where the remote pipper files are stored for this
    configuration. If the bucket is set in the repository configuration, it
    will automatically be used by pipper.

* `-d --default`

    If this flag is set, this repository configuration will be the default one
    used when no credentials or other information is specified.


### Repository: modify

    $ pipper repostory modify <EXISTING_REPOSITORY_NAME>

Modifies an existing repository configuration with new values. This sub-action
has the same flags as the _add_ sub-action. Any flags that you set will be
used to replace existing values. Any omitted flags will retain their existing
values.


### Repository: remove

    $ pipper repository remove <EXISTING_REPOSITORY_NAME>
    
Removes an existing repository configuration from the configuration storage.


### Repository: list

    $ pipper repository list

Use this command to list the currently stored repository configurations. It
also lets you know which of the configurations is set to the default value.


### Repository: exists

    $ pipper repository exists

Displays information on whether or not a repository configuration currently 
exists.


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

* `-e --expires <EXPIRES_IN>`

    How long the authorized URL is valid before it expires. The format
    should be `<NUMBER><UNIT>`, where the number is a positive integer and
    the unit can be hours, minutes or seconds. Units can be abbreviated, e.g.:
    
    * _12mins_: 12 minutes
    * _130m_: 130 minutes
    * _18s_: 18 seconds
    * _3hr_: 3 hours


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


## Version Locking

Pipper supports version matching/locking in a similar fashion to pip. However,
the syntax is a little bit stricter. Values must conform to semantic
versions. Consider a library `foo`. A specific version can be installed using
any of the following statements:

- `foo` no version will install latest
- `foo:1.2.3` that specific version
- `foo:=1.2.3` that specific version
- `foo:==1.2.3` that specific version
- `foo:1.2.*` the latest revision of `1.2.x`
- `foo:1.*.*` the latest minor version and revision of `1.x.x`
- `foo:<1.2.3` any version below the specified one
- `foo:<=1.2.3` any version equal to or below the specified one
- `foo:>1.2.3` any version above the specified one
- `foo:>=1.2.3` any version equal to or above the specified one

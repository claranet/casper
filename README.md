Casper
======

Casper is a command line tool that interacts with Cloud Deploy (Ghost project).

Cloud Deploy documentation is available here : [https://docs.cloudeploy.io](https://docs.cloudeploy.io)

Installation
------------
With [pip](https://pip.pypa.io) (in a [virtualenv](https://virtualenv.pypa.io) or not)

```
pip install git+ssh://github.com/claranet/casper
```

Usage
-----
Usage documentation is embedded in command.
```
casper --help
```

Configuration
-------------
Location and credentials to access the Cloud Deploy instance are prompted if needed.

Configuration details can also be specified in a `.casper` configuration file.
The command will look for this file in the current directory and the user home directory, in this order.
Also, the configuration file can be specified with the `--config-file` option.

The configuration file can contain many profiles, the default one is named `default` and is mandatory. The profile can be chosen with the `--profile` option.

Here is an example of a configuration file :

```
[default]
endpoint=https://my_instance.cloudeploy.io
username=casper

[customer_x]
endpoint=https://customer-x.cloudeploy.io
username=casper
password=XXXXXX
```

Any missing information for a profile will be prompted.

Enable autocompletion
---------------------

Bash user:

```bash
_CASPER_COMPLETE=source casper >> ~/.bash_completion
```


Zsh user :

Put the following content to the following path ~/.zshrc

```bash
autoload bashcompinit
bashcompinit
eval "$(_CASPER_COMPLETE=source casper)"
```

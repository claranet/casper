# Changelog

## Unreleased
## v2.2.1
### bugfixes
* GHOST-706/707: Fix job log command with `--no-color` flag may fail
* GHOST-630/711: Update pip dependencies and use PEP 508 custom url format (needed to be compatible with pip >= 19.0)

## v2.2.0
### features
* GHOST-623 Handle application `description` field
* GHOST-657 Uses common Pyhon SDK Client
* GHOST-603 Implement deployments and jobs filtering
* GHOST-523 See and download job logs
* GHOST-529 See job logs in realtime
* GHOST-552 Support websocket authentication
* GHOST-640 Real time logs when launching a command
* GHOST-526 Implement application creation/update

## v2.1.0
### features
* GHOST-568 Implement applications filtering
* GHOST-546 Document how to use revision in deploy command
* GHOST-524 Implement blue/green commands
* GHOST-550 Implement recreateinstances command
* GHOST-528 Added autocomplete instructions
* GHOST-597 Update pip dependencies
### bugfixes
* GHOST-630 Dependencies are not installed

## v2.0.1
### bugfixes
* GHOST-618 executescript command doesn't work

## v2.0.0
* Complete rewrite of the code
* Usage modifications
* Package install with pip

## v1.0.0
* First version

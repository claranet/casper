import configparser

import click
import os

from click import Group

from casper.ghost_api_client import AppsApiClient, JobsApiClient, DeploymentsApiClient


class Context():
    def __init__(self):
        self.verbose = False
        self._api_username = None
        self._api_password = None
        self._api_endpoint = None
        self._apps = None
        self._deployments = None
        self._jobs = None

    @property
    def apps(self):
        if self._apps is None:
            self._apps = AppsApiClient(self.api_endpoint, self.api_username, self.api_password)
        return self._apps

    @property
    def jobs(self):
        if self._jobs is None:
            self._jobs = JobsApiClient(self.api_endpoint, self.api_username, self.api_password)
        return self._jobs

    @property
    def deployments(self):
        if self._deployments is None:
            self._deployments = DeploymentsApiClient(self.api_endpoint, self.api_username, self.api_password)
        return self._deployments

    @property
    def api_username(self):
        if self._api_username is None:
            self._api_username = click.prompt('Cloud deploy username')
        return self._api_username

    @property
    def api_password(self):
        if self._api_password is None:
            self._api_password = click.prompt('Cloud deploy password', hide_input=True)
        return self._api_password

    @property
    def api_endpoint(self):
        if self._api_endpoint is None:
            self._api_endpoint = click.prompt('Cloud deploy endpoint')
        return self._api_endpoint


context = click.make_pass_decorator(Context, ensure=True)


class NamedGroups(Group):
    # TODO implement dynamic command fetching here instead of __init__ file
    # TODO split objects management and commands in help
    pass


CONFIG_FILE_PATHS = (os.path.expanduser('~/.casper'), os.path.join(os.getcwd(), '.casper'))


@click.command(cls=NamedGroups)
@click.option('--verbose', is_flag=True)
@click.option('--profile', default="default")
@click.option('--config-file', type=click.Path(exists=True))
@context
def cli(context, verbose, profile, config_file):
    context.verbose = verbose

    config = configparser.ConfigParser()
    parsed_configs = config.read(config_file if config_file else CONFIG_FILE_PATHS)
    if not parsed_configs:
        click.echo(click.style(
            'No valid config files found, Cloud Deploy credentials info will be prompted', fg='yellow'), err=True)

    if profile in config:
        config_section = config[profile]
        context._api_username = config_section.get('username', None)
        context._api_password = config_section.get('password', None)
        context._api_endpoint = config_section.get('endpoint', None)
    else:
        click.echo(click.style('No section "{}" found in configuration'.format(profile), fg='yellow'), err=True)

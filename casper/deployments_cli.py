from datetime import datetime

import click
import pytz
import yaml
from click import ClickException
from tabulate import tabulate

from casper import utils
from casper.ghost_api_client import ApiClientException
from casper.main import cli, context


@cli.group('deployment', help="Manage deployments")
def deployments():
    pass


@deployments.command('ls', help="List the deployments")
@click.option('--nb', default=10, help="Number of deployments to fetch (default 10)")
@click.option('--page', default=1, help="Page to fetch (default 1)")
@context
def deployments_list(context, nb, page):
    try:
        deployments, max_results, total, cur_page = context.deployments.list(nb=nb, page=page)
    except ApiClientException as e:
        raise ClickException(e) from e

    if max_results >= total:
        click.echo('Showing all the {} deployments'.format(total))
    else:
        click.echo('Showing {} on {} deployments - Page {}'.format(max_results, total, cur_page))
    click.echo(tabulate(
        [[
            dep['_id'],
            dep.get('job_id', {}).get('_id'),
            dep['app_id']['name'] if dep.get('app_id') else '',
            dep['module'],
            dep['commit'], dep.get('job_id', {}).get('user'),
            datetime.fromtimestamp(dep['timestamp'], pytz.UTC).strftime(utils.RFC1123_DATE_FORMAT)
         ] for dep in deployments],
        headers=['ID', 'Job ID', 'Application name', 'Module', 'Commit', 'User', 'Date']
    ))


@deployments.command('show', short_help="Show the details of a deployment")
@click.argument('deployment-id')
@context
def deployment_show(context, deployment_id):
    try:
        app = context.deployments.retrieve(deployment_id)
    except ApiClientException as e:
        raise ClickException(e) from e

    click.echo(yaml.safe_dump(app, indent=4, allow_unicode=True, default_flow_style=False))

from datetime import datetime

import click
import pytz
from click import ClickException
from tabulate import tabulate

from casper import utils
from casper.ghost_api_client import ApiClientException
from casper.main import cli, context


@cli.group('deployment')
def deployments():
    pass


@deployments.command('ls')
@click.option('--nb', default=10)
@click.option('--page', default=1)
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

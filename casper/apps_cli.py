import click
import yaml
from click import ClickException
from tabulate import tabulate

from casper.ghost_api_client import ApiClientException
from casper.main import cli, context


@cli.group('app')
def apps():
    pass


@apps.command('ls')
@click.option('--nb', default=10)
@click.option('--page', default=1)
@context
def apps_list(context, nb, page):
    try:
        apps, max_results, total, cur_page = context.apps.list(nb=nb, page=page)
    except ApiClientException as e:
        raise ClickException(e) from e

    if max_results >= total:
        click.echo('Showing all the {} applications'.format(total))
    else:
        click.echo('Showing {} on {} applications - Page {}'.format(max_results, total, cur_page))
    click.echo(tabulate(
        [[
            app['_id'],
            app['name'],
            app['env'],
            app['role'],
            '{} ({})'.format(app['blue_green']['color'], 'Online' if app['blue_green']['is_online'] else 'Offline')
            if app.get('blue_green', {}).get('enable_blue_green', False) else ''
         ] for app in apps],
        headers=['ID', 'Name', 'Environment', 'Role', 'Color']
    ))


@apps.command('show')
@click.argument('application-id')
@context
def app_show(context, application_id):
    try:
        app = context.apps.retrieve(application_id)
    except ApiClientException as e:
        raise ClickException(e) from e

    click.echo(yaml.safe_dump(app, indent=4, allow_unicode=True, default_flow_style=False))

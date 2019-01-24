import json

import click
import yaml
from click import BadParameter, ClickException
from tabulate import tabulate

from casper.main import cli, context
from pyghost.api_client import ApiClientException
from .utils import regex_validate


@cli.group('app', help="Manage applications")
def apps():
    pass


@apps.command('ls', help="List the applications")
@click.option('--nb', default=10, help="Number of applications to fetch (default 10)")
@click.option('--page', default=1, help="Page to fetch (default 1)")
@click.option('--name', help="Filter list by application name (regex usage possible)")
@click.option('--env', help="Filter by application environment", callback=regex_validate('^[a-z0-9\-_]*$'))
@click.option('--role', help="Filter by application role", callback=regex_validate('^[a-z0-9\-_]*$'))
@context
def apps_list(context, nb, page, name, env, role):
    try:
        apps, max_results, total, cur_page = context.apps.list(nb=nb, page=page, name=name, env=env, role=role)
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
            if app.get('blue_green', {}).get('enable_blue_green', False) else '',
            app.get('description', ''),
         ] for app in apps],
        headers=['ID', 'Name', 'Environment', 'Role', 'Color', 'Description']
    ))


@apps.command('show', short_help="Show the details of an application",
              help="Show the details of the application APPLICATION_ID")
@click.option('--format', type=click.Choice(['yaml', 'json']), default='yaml',
              help="Output format")
@click.option('--export', help="Output path to export", type=click.File('w'))
@click.argument('application-id')
@context
def app_show(context, application_id, format, export):
    try:
        app = context.apps.retrieve(application_id)
    except ApiClientException as e:
        raise ClickException(e) from e

    if format == 'yaml':
        dump = yaml.safe_dump(app, indent=4, allow_unicode=True, default_flow_style=False)
    else:
        dump = json.dumps(app, sort_keys=True, indent=4)
    click.echo(dump)

    if export is not None:
        del app['_created'], app['_etag'], app['_updated'], app['pending_changes'], app['user']
        if format == 'yaml':
            dump = yaml.safe_dump(app, indent=4, allow_unicode=True, default_flow_style=False)
        else:
            dump = json.dumps(app, sort_keys=True, indent=4)
        export.write(dump)


@apps.command('create', short_help="Create an application",
              help="Create an application from a JSON/YAML file")
@click.option('--format', type=click.Choice(['yaml', 'json']), default='yaml',
              help="Input format")
@click.argument('filename', type=click.File())
@context
def app_create(context, filename, format):
    file_content = filename.read()
    if format == 'yaml':
        try:
            app = yaml.load(file_content)
        except Exception as e:
            raise ClickException('Invalid YAML file.') from e
    else:
        try:
            app = json.loads(file_content)
        except Exception as e:
            raise ClickException('Invalid JSON file.') from e
    try:
        context.apps.validate_schema(app)
        app_id = context.apps.create(app)
        click.echo("Application creation OK - ID : {}".format(app_id))
    except Exception as e:
        raise ClickException('Cannot create your application. API Exception.\n{}'.format(e)) from e


@apps.command('update', short_help="Update an application",
              help="Update an application from a JSON/YAML file")
@click.option('--format', type=click.Choice(['yaml', 'json']), default='yaml',
              help="Input format")
@click.option('--etag', help="Application last version etag")
@click.option('--force', help="Force application update by fetching etag", is_flag=True)
@click.argument('filename', type=click.File())
@context
def app_update(context, filename, format, etag, force):
    if etag is None and force is False:
        raise BadParameter('You need specify an etag or use --force flag to fetch the latest etag value',
                           param_hint='etag')
    file_content = filename.read()
    if format == 'yaml':
        try:
            app = yaml.load(file_content)
        except Exception as e:
            raise ClickException('Invalid YAML file.') from e
    else:
        try:
            app = json.loads(file_content)
        except Exception as e:
            raise ClickException('Invalid JSON file.') from e
    try:
        app_id = context.apps.validate_schema(app, True)
        if force:
            etag = context.apps.retrieve(app_id).get('_etag')
        app['_id'] = app_id
        result_id = context.apps.update(app, etag)
        click.echo("Application update OK - ID : {}".format(result_id))
    except Exception as e:
        raise ClickException('Cannot update your application. API Exception.\n{}'.format(e)) from e

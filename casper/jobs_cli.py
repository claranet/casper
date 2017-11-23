import click
from click import ClickException
from tabulate import tabulate

from casper.ghost_api_client import ApiClientException
from .main import cli, context


@cli.group('job')
def jobs():
    pass


@jobs.command('ls')
@click.option('--nb', default=10)
@click.option('--page', default=1)
@context
def jobs_list(context, nb, page):
    try:
        jobs, max_results, total, cur_page = context.jobs.list(nb=nb, page=page)
    except ApiClientException as e:
        raise ClickException(e) from e

    if max_results >= total:
        click.echo('Showing all the {} jobs'.format(total))
    else:
        click.echo('Showing {} on {} jobs - Page {}'.format(max_results, total, cur_page))
    click.echo(tabulate(
        [[
            job['_id'], job['app_id']['name'] if job.get('app_id') else '',
            job['command'], job['status'], job['user'], job['_created']
         ] for job in jobs],
        headers=['ID', 'Application name', 'Command', 'Status', 'User', 'Date']
    ))

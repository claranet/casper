import click
import yaml
from click import ClickException
from tabulate import tabulate

from pyghost.api_client import ApiClientException
from casper.main import cli, context


@cli.group('job', help="Manage jobs")
def jobs():
    pass


@jobs.command('ls', help="List the jobs")
@click.option('--nb', default=10, help="Number of jobs to fetch (default 10)")
@click.option('--page', default=1, help="Page to fetch (default 1)")
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


@jobs.command('show', short_help="Show the details of a job")
@click.argument('job-id')
@context
def job_show(context, job_id):
    try:
        app = context.jobs.retrieve(job_id)
    except ApiClientException as e:
        raise ClickException(e) from e

    click.echo(yaml.safe_dump(app, indent=4, allow_unicode=True, default_flow_style=False))

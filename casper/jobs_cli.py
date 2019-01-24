import click
import yaml
from click import ClickException
from tabulate import tabulate

from casper.main import cli, context
from pyghost.api_client import ApiClientException, JobCommands, JobStatuses
from .utils import regex_validate


@cli.group('job', help="Manage jobs")
def jobs():
    pass


@jobs.command('ls', help="List the jobs")
@click.option('--nb', default=10, help="Number of jobs to fetch (default 10)")
@click.option('--page', default=1, help="Page to fetch (default 1)")
@click.option('--application', help="Filter list by application name (regex usage possible)")
@click.option('--env', help="Filter by application environment", callback=regex_validate('^[a-z0-9\-_]*$'))
@click.option('--role', help="Filter by application role", callback=regex_validate('^[a-z0-9\-_]*$'))
@click.option('--command', help="Filter by job command", type=click.Choice(list(map(str, JobCommands))))
@click.option('--status', help="Filter by job status", type=click.Choice(list(map(str, JobStatuses))))
@click.option('--user', help="Filter by job user")
@context
def jobs_list(context, nb, page, application, env, role, command, status, user):
    try:
        job_list, max_results, total, cur_page = context.jobs.list(nb=nb, page=page,
                                                                   application=application, env=env, role=role,
                                                                   command=command, status=status, user=user)
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
        ] for job in job_list],
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


@jobs.command('log', help="Show the logs of a job")
@click.argument('job-id')
@click.option('--output', help="Path of output log file", type=click.File('w'))
@click.option('--no-color', help="Remove ANSI color from output", is_flag=True)
@click.option('--waitstart', help="Wait for job to start if applicable", is_flag=True)
@context
def job_log(context, job_id, output, no_color, waitstart):
    job_log_handler(context, job_id, output, no_color, waitstart)


def job_log_handler(context, job_id, output, no_color, waitstart):
    def success_handler(log):
        click.echo(log, nl=False)
        if output is not None:
            output.write(log.decode('utf-8'))

    def exception_handler(e):
        raise ClickException('Error while retrieving logs: {}'.format(str(e))) from e

    try:
        context.jobs.get_logs_async(job_id, success_handler, exception_handler, wait_for_start=waitstart, no_color=no_color)
    except ApiClientException as e:
        raise ClickException('Error while retrieving logs: {}'.format(str(e))) from e

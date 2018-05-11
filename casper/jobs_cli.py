import base64
import click
import re
import requests
import yaml
from click import ClickException
from tabulate import tabulate
from .utils import regex_validate

from pyghost.api_client import ApiClientException, JobCommands, JobStatuses
from casper.main import cli, context

from socketIO_client import SocketIO


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
        jobs, max_results, total, cur_page = context.jobs.list(nb=nb, page=page, application=application, env=env, role=role, command=command, status=status, user=user)
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


@jobs.command('log', help="Show the logs of a job")
@click.argument('job-id')
@click.option('--output', help="Path of downloaded log file", type=click.File('w'))
@context
def job_log(context, job_id, output):
    def job_handler(args):
        if 'error' in args:
            raise ClickException(args['error'])
        if 'raw' not in args:
            data = re.sub('<[^<]+?>', '', args['html'].replace('</div><div class="panel panel-default">', "\n"))+"\n"
        else:
            try:
                data = base64.b64decode(args['raw'])
            except TypeError as e:
                raise ClickException(e) from e
        click.echo(data, nl=False)
        if output is not None:
            output.write(data.decode('utf-8'))

    try:
        job = context.jobs.retrieve(job_id)
        if job['status'] == JobStatuses.STARTED.value:
            check_ws = requests.get('{}/socket.io/'.format(context._api_endpoint))
            if check_ws.status_code == 200:
                with SocketIO(context._api_endpoint, verify=False) as socketIO:
                    socketIO.emit('job_logging', {'log_id': job_id, 'last_pos': 0, 'raw_mode': True})
                    socketIO.on('job', job_handler)
                    while job['status'] == JobStatuses.STARTED.value:
                        socketIO.wait(seconds=3)
                        job = context.jobs.retrieve(job_id)
            else:
                raise ClickException('Websocket server is unavailable.')
        elif job['status'] == JobStatuses.INIT.value:
            raise ClickException('The job has not started yet.')
        else:
            data = context.jobs.get_logs(job_id)
            click.echo(data, nl=False)
            if output is not None:
                output.write(data)
    except ApiClientException as e:
        raise ClickException(e) from e

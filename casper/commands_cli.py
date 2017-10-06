import click

from casper.main import cli, context


@cli.command('deploy')
@click.argument('application-id')
@context
def deploy(context, application_id):
    pass

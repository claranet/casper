import click
from click import ClickException, BadParameter, MissingParameter

from casper.ghost_api_client import ApiClientException
from casper.ghost_api_client import DEPLOYMENT_STRATEGIES, SAFE_DEPLOYMENT_STRATEGIES
from casper.ghost_api_client import SCRIPT_EXECUTION_STRATEGY_SERIAL, SAFE_DEPLOYMENT_STRATEGY_ONE_BY_ONE
from casper.ghost_api_client import SCRIPT_EXECUTION_STRATEGIES
from casper.main import cli, context


@cli.command('deploy')
@click.argument('application-id')
@click.option('--module', '-m', multiple=True)
@click.option('--all-modules', is_flag=True)
@click.option('--strategy', type=click.Choice(DEPLOYMENT_STRATEGIES))
@click.option('--safe-deploy-strategy', type=click.Choice(SAFE_DEPLOYMENT_STRATEGIES))
@context
def deploy(context, application_id, module, all_modules, strategy, safe_deploy_strategy):
    # TODO find a "clicker" way to do this parameter validation
    if not module and not all_modules:
        raise MissingParameter('You must have one (and only one) from --module and --all-modules parameters',
                               param_hint='module', param_type='parameter')
    if module and all_modules:
        raise BadParameter(
            'You must have only one from --module and --all-modules parameters', param_hint='module')

    if all_modules:
        app = context.apps.retrieve(application_id)
        module = [m["name"] for m in app["modules"]]

    modules = []
    for m in module:
        name, rev = m.split(':') if ':' in m else (m, None)
        mod = {"name": name}
        if rev:
            mod["rev"] = rev
        modules.append(mod)

    try:
        job_id = context.jobs.command_deploy(application_id, modules, strategy, safe_deploy_strategy)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('redeploy')
@click.argument('application-id')
@click.argument('deployment-id')
@click.option('--strategy', type=click.Choice(DEPLOYMENT_STRATEGIES))
@click.option('--safe-deploy-strategy', type=click.Choice(SAFE_DEPLOYMENT_STRATEGIES))
@context
def redeploy(context, application_id, deployment_id, strategy, safe_deploy_strategy):
    try:
        job_id = context.jobs.command_redeploy(application_id, deployment_id, strategy, safe_deploy_strategy)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('executescript')
@click.argument('application-id')
@click.argument('script-file', type=click.File(mode='r'))
@click.option('--strategy', type=click.Choice(SCRIPT_EXECUTION_STRATEGIES), default=SCRIPT_EXECUTION_STRATEGY_SERIAL)
@click.option('--safe-deploy-strategy',
              type=click.Choice(SAFE_DEPLOYMENT_STRATEGIES), default=SAFE_DEPLOYMENT_STRATEGY_ONE_BY_ONE)
@click.option('--instance-ip')
@click.option('--module-context')
@context
def executescript(context, application_id, script_file, strategy, safe_deploy_strategy, instance_ip, module_context):
    try:
        script_content = script_file.read()
        job_id = context.jobs.command_executescript(
            application_id, script_content, strategy, safe_deploy_strategy, instance_ip, module_context)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('buildimage')
@click.argument('application-id')
@click.option('--instance-type')
@click.option('--skip-bootstrap', type=bool)
@context
def buildimage(context, application_id, instance_type, skip_bootstrap):
    try:
        job_id = context.jobs.command_buildimage(application_id, instance_type, skip_bootstrap)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('createinstance')
@click.argument('application-id')
@click.option('--subnet-id')
@click.option('--private-ip-address')
@context
def createinstance(context, application_id, subnet_id, private_ip_address):
    try:
        job_id = context.jobs.command_createinstance(application_id, subnet_id, private_ip_address)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('destroyallinstances')
@click.argument('application-id')
@context
def destroyallinstances(context, application_id):
    try:
        job_id = context.jobs.command_destroyallinstances(application_id)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('updatelifecyclehooks')
@click.argument('application-id')
@context
def updatelifecyclehooks(context, application_id):
    try:
        job_id = context.jobs.command_updatelifecyclehooks(application_id)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('updateautoscaling')
@click.argument('application-id')
@context
def updateautoscaling(context, application_id):
    try:
        job_id = context.jobs.command_updateautoscaling(application_id)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e

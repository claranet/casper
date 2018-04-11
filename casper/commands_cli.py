import click
from click import ClickException, BadParameter, MissingParameter

from casper.ghost_api_client import ApiClientException
from casper.ghost_api_client import DEPLOYMENT_STRATEGIES, DEPLOYMENT_STRATEGY_SERIAL, SAFE_DEPLOYMENT_STRATEGIES
from casper.ghost_api_client import SCRIPT_EXECUTION_STRATEGY_SERIAL, SAFE_DEPLOYMENT_STRATEGY_ONE_BY_ONE
from casper.ghost_api_client import SCRIPT_EXECUTION_STRATEGIES
from casper.main import cli, context


@cli.command('deploy', short_help='Create a "deploy" job',
             help="Create a job that deploys APPLICATION_ID application")
@click.argument('application-id')
@click.option('--module', '-m', multiple=True, help="Module(s) name(s) to deploy")
@click.option('--all-modules', is_flag=True, help="Flag for all modules deployment")
@click.option('--strategy', type=click.Choice(DEPLOYMENT_STRATEGIES),
              help="Deployment strategy (default {})".format(DEPLOYMENT_STRATEGY_SERIAL))
@click.option('--safe-deploy-strategy', type=click.Choice(SAFE_DEPLOYMENT_STRATEGIES),
              help="Safe deployment strategy (default none)")
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


@cli.command('redeploy', short_help='Create a "redeploy" job',
             help="Create a job that redeploys APPLICATION_ID application from previous deployment DEPLOYMENT_ID")
@click.argument('application-id')
@click.argument('deployment-id')
@click.option('--strategy', type=click.Choice(DEPLOYMENT_STRATEGIES),
              help="Deployment strategy (default {})".format(DEPLOYMENT_STRATEGY_SERIAL))
@click.option('--safe-deploy-strategy', type=click.Choice(SAFE_DEPLOYMENT_STRATEGIES),
              help="Safe deployment strategy (default none)")
@context
def redeploy(context, application_id, deployment_id, strategy, safe_deploy_strategy):
    try:
        job_id = context.jobs.command_redeploy(application_id, deployment_id, strategy, safe_deploy_strategy)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('executescript', short_help='Create an "executescript" job',
             help="Create a job that executes the script SCRIPT_FILE for APPLICATION_ID application")
@click.argument('application-id')
@click.argument('script-file', type=click.File())
@click.option('--strategy', type=click.Choice(SCRIPT_EXECUTION_STRATEGIES), default=SCRIPT_EXECUTION_STRATEGY_SERIAL,
              help="Script execution strategy (default {})".format(SCRIPT_EXECUTION_STRATEGY_SERIAL))
@click.option('--safe-deploy-strategy',
              type=click.Choice(SAFE_DEPLOYMENT_STRATEGIES), default=SAFE_DEPLOYMENT_STRATEGY_ONE_BY_ONE,
              help="Safe deployment strategy (default {})".format(SAFE_DEPLOYMENT_STRATEGY_ONE_BY_ONE))
@click.option('--instance-ip', help="Instance IP for only one instance execution (default none)")
@click.option('--module-context', help="Force script working dir from module context (default none)")
@context
def executescript(context, application_id, script_file, strategy, safe_deploy_strategy, instance_ip, module_context):
    try:
        script_content = script_file.read()
        job_id = context.jobs.command_executescript(
            application_id, script_content, strategy, safe_deploy_strategy, instance_ip, module_context)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('buildimage', short_help='Create a "buildimage" job',
             help="Create a job that builds an image for APPLICATION_ID application")
@click.argument('application-id')
@click.option('--instance-type', help="Force instance type for build")
@click.option('--skip-bootstrap', type=bool, help="Force skipping the provisioner bootstrap")
@context
def buildimage(context, application_id, instance_type, skip_bootstrap):
    try:
        job_id = context.jobs.command_buildimage(application_id, instance_type, skip_bootstrap)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('createinstance', short_help='Create a "createinstance" job',
             help="Create a job that creates an instance for APPLICATION_ID application")
@click.argument('application-id')
@click.option('--subnet-id', help="Force instance subnet id")
@click.option('--private-ip-address', help="Force private IP address")
@context
def createinstance(context, application_id, subnet_id, private_ip_address):
    try:
        job_id = context.jobs.command_createinstance(application_id, subnet_id, private_ip_address)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('destroyallinstances', short_help='Create a "destroyallinstances" job',
             help="Create a job that destroys all instances for APPLICATION_ID application")
@click.argument('application-id')
@context
def destroyallinstances(context, application_id):
    try:
        job_id = context.jobs.command_destroyallinstances(application_id)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('updatelifecyclehooks', short_help='Create a "updatelifecyclehooks" job',
             help="Create a job that updates lifecycle hooks APPLICATION_ID application")
@click.argument('application-id')
@context
def updatelifecyclehooks(context, application_id):
    try:
        job_id = context.jobs.command_updatelifecyclehooks(application_id)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('updateautoscaling', short_help='Create a "updateautoscaling" job',
             help="Create a job that updates auto scaling for APPLICATION_ID application")
@click.argument('application-id')
@context
def updateautoscaling(context, application_id):
    try:
        job_id = context.jobs.command_updateautoscaling(application_id)
        click.echo("Job creation OK - ID : {}".format(job_id))
    except ApiClientException as e:
        raise ClickException(e) from e

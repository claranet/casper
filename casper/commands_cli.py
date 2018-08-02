import click
from click import ClickException, BadParameter, MissingParameter

from casper.jobs_cli import job_log_handler
from casper.main import cli, context
from pyghost.api_client import ApiClientException
from pyghost.api_client import BLUEGREEN_SWAP_STRATEGIES, BLUEGREEN_SWAP_STRATEGY_OVERLAP
from pyghost.api_client import DEPLOYMENT_STRATEGIES, DEPLOYMENT_STRATEGY_SERIAL
from pyghost.api_client import ROLLING_UPDATE_STRATEGIES, SAFE_DEPLOYMENT_STRATEGIES
from pyghost.api_client import SAFE_DEPLOYMENT_STRATEGY_ONE_BY_ONE, SCRIPT_EXECUTION_STRATEGIES
from pyghost.api_client import SCRIPT_EXECUTION_STRATEGY_SERIAL


@cli.command('deploy', short_help='Create a "deploy" job',
             help="Create a job that deploys APPLICATION_ID application")
@click.argument('application-id')
@click.option('--module', '-m', multiple=True, help="Module(s) name(s) to deploy, revision can be set by "
                                                    "suffixing with :rev. (example: my_module:v1)")
@click.option('--all-modules', is_flag=True, help="Flag for all modules deployment")
@click.option('--strategy', type=click.Choice(DEPLOYMENT_STRATEGIES),
              help="Deployment strategy (default {})".format(DEPLOYMENT_STRATEGY_SERIAL))
@click.option('--safe-deploy-strategy', type=click.Choice(SAFE_DEPLOYMENT_STRATEGIES),
              help="Safe deployment strategy (default none)")
@click.option('--live-logs', help="Wait for job starting and output logs", is_flag=True)
@click.option('--output', help="Path of output log file", type=click.File('w'))
@click.option('--no-color', help="Remove ANSI color from output", is_flag=True)
@context
def deploy(context, application_id, module, all_modules, strategy, safe_deploy_strategy, live_logs, output, no_color):
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
        handle_job_creation(context, job_id, live_logs, output, no_color)
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
@click.option('--live-logs', help="Wait for job starting and output logs", is_flag=True)
@click.option('--output', help="Path of output log file", type=click.File('w'))
@click.option('--no-color', help="Remove ANSI color from output", is_flag=True)
@context
def redeploy(context, application_id, deployment_id, strategy, safe_deploy_strategy, live_logs, output, no_color):
    try:
        job_id = context.jobs.command_redeploy(application_id, deployment_id, strategy, safe_deploy_strategy)
        handle_job_creation(context, job_id, live_logs, output, no_color)
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
@click.option('--live-logs', help="Wait for job starting and output logs", is_flag=True)
@click.option('--output', help="Path of output log file", type=click.File('w'))
@click.option('--no-color', help="Remove ANSI color from output", is_flag=True)
@context
def executescript(context, application_id, script_file, strategy, safe_deploy_strategy, instance_ip, module_context, live_logs, output, no_color):
    try:
        script_content = script_file.read()
        job_id = context.jobs.command_executescript(
            application_id, script_content, strategy, safe_deploy_strategy, instance_ip, module_context)
        handle_job_creation(context, job_id, live_logs, output, no_color)
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('buildimage', short_help='Create a "buildimage" job',
             help="Create a job that builds an image for APPLICATION_ID application")
@click.argument('application-id')
@click.option('--instance-type', help="Force instance type for build")
@click.option('--skip-bootstrap', type=bool, help="Force skipping the provisioner bootstrap")
@click.option('--live-logs', help="Wait for job starting and output logs", is_flag=True)
@click.option('--output', help="Path of output log file", type=click.File('w'))
@click.option('--no-color', help="Remove ANSI color from output", is_flag=True)
@context
def buildimage(context, application_id, instance_type, skip_bootstrap, live_logs, output, no_color):
    try:
        job_id = context.jobs.command_buildimage(application_id, instance_type, skip_bootstrap)
        handle_job_creation(context, job_id, live_logs, output, no_color)
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('createinstance', short_help='Create a "createinstance" job',
             help="Create a job that creates an instance for APPLICATION_ID application")
@click.argument('application-id')
@click.option('--subnet-id', help="Force instance subnet id")
@click.option('--private-ip-address', help="Force private IP address")
@click.option('--live-logs', help="Wait for job starting and output logs", is_flag=True)
@click.option('--output', help="Path of output log file", type=click.File('w'))
@click.option('--no-color', help="Remove ANSI color from output", is_flag=True)
@context
def createinstance(context, application_id, subnet_id, private_ip_address, live_logs, output, no_color):
    try:
        job_id = context.jobs.command_createinstance(application_id, subnet_id, private_ip_address)
        handle_job_creation(context, job_id, live_logs, output, no_color)
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('destroyallinstances', short_help='Create a "destroyallinstances" job',
             help="Create a job that destroys all instances for APPLICATION_ID application")
@click.argument('application-id')
@click.option('--live-logs', help="Wait for job starting and output logs", is_flag=True)
@click.option('--output', help="Path of output log file", type=click.File('w'))
@click.option('--no-color', help="Remove ANSI color from output", is_flag=True)
@context
def destroyallinstances(context, application_id, live_logs, output, no_color):
    try:
        job_id = context.jobs.command_destroyallinstances(application_id)
        handle_job_creation(context, job_id, live_logs, output, no_color)
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('recreateinstances', short_help='Create a "recreateinstances" job',
              help="Create a job that renews all the instances for APPLICATION_ID application")
@click.argument('application-id')
@click.option('--strategy', type=click.Choice(ROLLING_UPDATE_STRATEGIES),
              help="Rolling-update strategy")
@click.option('--live-logs', help="Wait for job starting and output logs", is_flag=True)
@click.option('--output', help="Path of output log file", type=click.File('w'))
@click.option('--no-color', help="Remove ANSI color from output", is_flag=True)
@context
def recreateinstances(context, application_id, strategy, live_logs, output, no_color):
    try:
        job_id = context.jobs.command_recreateinstances(application_id, strategy)
        handle_job_creation(context, job_id, live_logs, output, no_color)
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('updatelifecyclehooks', short_help='Create a "updatelifecyclehooks" job',
             help="Create a job that updates lifecycle hooks APPLICATION_ID application")
@click.argument('application-id')
@click.option('--live-logs', help="Wait for job starting and output logs", is_flag=True)
@click.option('--output', help="Path of output log file", type=click.File('w'))
@click.option('--no-color', help="Remove ANSI color from output", is_flag=True)
@context
def updatelifecyclehooks(context, application_id, live_logs, output, no_color):
    try:
        job_id = context.jobs.command_updatelifecyclehooks(application_id)
        handle_job_creation(context, job_id, live_logs, output, no_color)
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('updateautoscaling', short_help='Create a "updateautoscaling" job',
             help="Create a job that updates auto scaling for APPLICATION_ID application")
@click.argument('application-id')
@click.option('--live-logs', help="Wait for job starting and output logs", is_flag=True)
@click.option('--output', help="Path of output log file", type=click.File('w'))
@click.option('--no-color', help="Remove ANSI color from output", is_flag=True)
@context
def updateautoscaling(context, application_id, live_logs, output, no_color):
    try:
        job_id = context.jobs.command_updateautoscaling(application_id)
        handle_job_creation(context, job_id, live_logs, output, no_color)
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('preparebluegreen', short_help='Create a "preparebluegreen" job',
             help="Create a job that prepares the blue-green environment for APPLICATION_ID application")
@click.argument('application-id')
@click.option('--copy-ami', type=bool, help="Copy the AMI from the online application if true.", default=False)
@click.option('--attach-elb', type=bool, help="Create a temporary ELB to attach to the Auto Scaling group if true.",
              default=True)
@click.option('--live-logs', help="Wait for job starting and output logs", is_flag=True)
@click.option('--output', help="Path of output log file", type=click.File('w'))
@click.option('--no-color', help="Remove ANSI color from output", is_flag=True)
@context
def preparebluegreen(context, application_id, copy_ami, attach_elb, live_logs, output, no_color):
    try:
        job_id = context.jobs.command_preparebluegreen(application_id, copy_ami, attach_elb)
        handle_job_creation(context, job_id, live_logs, output, no_color)
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('purgebluegreen', short_help='Create a "purgebluegreen" job',
             help="Create a job that purges the offline blue-green environment for APPLICATION_ID application")
@click.argument('application-id')
@click.option('--live-logs', help="Wait for job starting and output logs", is_flag=True)
@click.option('--output', help="Path of output log file", type=click.File('w'))
@click.option('--no-color', help="Remove ANSI color from output", is_flag=True)
@context
def purgebluegreen(context, application_id, live_logs, output, no_color):
    try:
        job_id = context.jobs.command_purgebluegreen(application_id)
        handle_job_creation(context, job_id, live_logs, output, no_color)
    except ApiClientException as e:
        raise ClickException(e) from e


@cli.command('swapbluegreen', short_help='Create a "swapbluegreen" job',
             help="Create a job that swaps the blue-green environment for APPLICATION_ID application")
@click.argument('application-id')
@click.option('--strategy', type=click.Choice(BLUEGREEN_SWAP_STRATEGIES), default=BLUEGREEN_SWAP_STRATEGY_OVERLAP,
              help="Blue-green swap strategy (default {})".format(BLUEGREEN_SWAP_STRATEGY_OVERLAP))
@click.option('--live-logs', help="Wait for job starting and output logs", is_flag=True)
@click.option('--output', help="Path of output log file", type=click.File('w'))
@click.option('--no-color', help="Remove ANSI color from output", is_flag=True)
@context
def swapbluegreen(context, application_id, strategy, live_logs, output, no_color):
    try:
        job_id = context.jobs.command_swapbluegreen(application_id, strategy)
        handle_job_creation(context, job_id, live_logs, output, no_color)
    except ApiClientException as e:
        raise ClickException(e) from e


def handle_job_creation(context, job_id, live_logs=None, output=None, no_color=None):
  click.echo("Job creation OK - ID : {}".format(job_id))
  if live_logs:
    click.echo("Waiting for job logs...")
    job_log_handler(context, job_id, output, no_color, True)

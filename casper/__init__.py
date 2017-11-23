from .main import cli

# Because of the decorator behavior (I think), discovery of one command in a module discover all of them
from .apps_cli import apps
from .jobs_cli import jobs
from .deployments_cli import deployments
from .commands_cli import deploy

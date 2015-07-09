import argparse
import ConfigParser, os
from prettytable import PrettyTable
import requests
import json

login = ""
password = ""
endpoint = ""

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

def load_conf():
	config = ConfigParser.ConfigParser()
	config.read([os.path.expanduser('~/.casper')])
	try:
		login = config.get('Default', 'login')
		password = config.get('Default', 'password')
		endpoint = config.get('Default', 'endpoint')
	except ConfigParser.NoSectionError:
		print("Configuration file not containing Default section")
		exit(-1)

	return config


def parse_cmdline():
	parser = argparse.ArgumentParser(description="Casper command line")
	#group = parser.add_mutually_exclusive_group(required=True)

	parser.add_argument('--configure', action='store_true')
	parser.add_argument('--debug', action='store_true')

	subparsers = parser.add_subparsers(dest='action', help='actions help')

	parser_list_apps = subparsers.add_parser('list-apps', help='list applications')

	parser_list_modules = subparsers.add_parser('list-modules', help='list modules')
	parser_list_modules.add_argument('--app_id', required=True)

	parser_list_jobs = subparsers.add_parser('list-jobs', help='list jobs')
	parser_list_jobs.add_argument('--app_id')
	
	parser_deploy = subparsers.add_parser('deploy', help='deploy module')
	parser_deploy.add_argument('--app_id', required=True)
	parser_deploy.add_argument('--module_name', required=True)
	parser_deploy.add_argument('--revision')

	parser_rollback = subparsers.add_parser('rollback', help='rollback module')
	parser_rollback.add_argument('--app_id', required=True)
	parser_rollback.add_argument('--deployment_id', required=True)

	return parser.parse_args()

def handle_response_status_code(result):
	if result.status_code >= 300:
		print("Error: {0} - {1}".format(result.status_code, result.text))
		exit(-1)

def list_apps(cmd, config):
	print('Listing applications...')
	url = config.get('Default', 'endpoint') + '/apps' + '?sort=-_updated'
	print('URL: {0}'.format(url))
	result = requests.get(url, headers=headers, auth=(config.get('Default', 'login'), config.get('Default', 'password')))
	handle_response_status_code(result)
	apps = result.json().get('_items', [])

	x = PrettyTable(["ID", "Name", "Role", "Environment", "Modules"])
	for app in apps:
		modules_str = ","
		mod_array = []
		for module in app.get('modules'):
			mod_array.append(module.get('name'))
		modules = modules_str.join(mod_array)
		x.add_row([app.get('_id'), app.get('name'), app.get('role'), app.get('env'), modules])
	print(x)

def list_jobs(cmd, config):
	print('Listing jobs...')
	url = config.get('Default', 'endpoint') + '/jobs' + '?max_results=50' + '&sort=-_updated'
	print('URL: {0}'.format(url))
	result = requests.get(url, headers=headers, auth=(config.get('Default', 'login'), config.get('Default', 'password')))
	handle_response_status_code(result)
	jobs = result.json().get('_items', [])

	x = PrettyTable(["Command", "Application", "Created", "Status", "Module"])
	for job in jobs:
		module = {}
		if job.get('modules') and len(job.get('modules')) > 0:
			module = job.get('modules')[0]
		module_str = "module: {0}, revision: {1}, deployment_id: {2}".format(module.get('name'),module.get('rev'), module.get('deploy_id'))
		x.add_row([job.get('command'), job.get('app_id'), job.get('_created'), job.get('status'), module_str])
	print(x)

def list_modules(cmd, config):
	print('listing modules')

def deploy(cmd, config):
	print("Deploying to app_id: {0}, module: {1}, in revision {2}...".format(cmd.app_id, cmd.module_name, cmd.revision or 'HEAD'))
	url = config.get('Default', 'endpoint') + '/jobs' 
	job = {}
	job['command'] = 'deploy'
	job['app_id'] = cmd.app_id
	job['modules'] = [{'name': cmd.module_name, 'rev': cmd.revision or 'HEAD'}]
	result = requests.post(url, data=json.dumps(job), headers=headers, auth=(config.get('Default', 'login'), config.get('Default', 'password')))
	handle_response_status_code(result)
	print(result.text)

def rollback(cmd, config):
	print('Rollbacking to deployment_id: {0}'.format(cmd.deployment_id))
	url = config.get('Default', 'endpoint') + '/jobs' 
	job = {}
	job['app_id'] = cmd.app_id
	job['command'] = 'rollback'
	job['options'] = [cmd.deployment_id]
	result = requests.post(url, data=json.dumps(job), headers=headers, auth=(config.get('Default', 'login'), config.get('Default', 'password')))
	handle_response_status_code(result)
	print(result.text)	

def execute_action(cmd, config):
	actions = { 'list-apps': list_apps, 'list-jobs': list_jobs, 'list-modules': list_modules, 'deploy': deploy, 'rollback': rollback }
	actions[cmd.action](cmd, config)


if __name__ == '__main__':
	config = load_conf()
	cmd = parse_cmdline()
	execute_action(cmd, config)


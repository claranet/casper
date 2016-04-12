#!/usr/bin/env python
import argparse
import ConfigParser, os
from prettytable import PrettyTable
import requests
import json
import re
import sys
import getpass

login = ""
password = ""
endpoint = ""
filename = '~/.casper'

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

ansi_regex = re.compile(r'\x1b[^m]*m')
def ansi_escape(string):
    return ansi_regex.sub('', string)

def load_conf(cmd):
    config = ConfigParser.ConfigParser()
    if config.read([os.path.expanduser(filename)]) is "":
       print("No Configuration file found with Default section")
       return config
    try:
        login = config.get('Default', 'login')
    except:
        if cmd.debug:
           print("Configuration file found with Default section but no login specify")
        pass
    try:
        endpoint = config.get('Default', 'endpoint')
    except:
        if cmd.debug:
           print("Configuration file found with Default section but no endpoint specify")
        pass
    try:
        password = config.get('Default', 'password')
    except:
        if cmd.debug:
           print("Configuration file found with Default section but no password specify")
        pass
    return config

def get_endpoint(cmd, config):
    endpoint = cmd.endpoint
    if cmd.endpoint == None:
       config.read([os.path.expanduser(filename)])
       try:
           endpoint = config.get('Default', 'endpoint')
       except ConfigParser.NoSectionError:
           endpoint = raw_input('Please specify endpoint : ')
           pass
    endpoint = endpoint.replace(" ","")
    return endpoint

def get_login(cmd, config):
    login = cmd.login
    if cmd.login == None:
       config.read([os.path.expanduser(filename)])
       try:
           login = config.get('Default', 'login')
       except ConfigParser.NoSectionError:
           login = raw_input('Please specify login : ')
           pass
    login = login.replace(" ","")
    return login

def get_password(cmd, config):
    password = cmd.password
    if cmd.password == None:
       config.read([os.path.expanduser(filename)])
       try:
           password = config.get('Default', 'password')
       except ConfigParser.NoSectionError:
           password = getpass.getpass()
           pass
    return password

def parse_cmdline():
    parser = argparse.ArgumentParser(description="Casper command line")
    #group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument('--configure', action='store_true')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--login')
    parser.add_argument('--password')
    parser.add_argument('--endpoint')

    subparsers = parser.add_subparsers(dest='action', help='actions help')

    parser_list_apps = subparsers.add_parser('list-apps', help='list applications')

    parser_list_modules = subparsers.add_parser('list-modules', help='list modules')
    parser_list_modules.add_argument('--app_id', required=True)

    parser_list_jobs = subparsers.add_parser('list-jobs', help='list jobs')
    parser_list_jobs.add_argument('--app_id')

    parser_deployments = subparsers.add_parser('list-deployments', help='list deployments')
    parser_deployments.add_argument('--app_id', required=True)
    parser_deployments.add_argument('--module_name', required=True)

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
    url = get_endpoint(cmd, config) + '/apps' + '?sort=-_updated'
    print('URL: {0}'.format(url))
    result = requests.get(url, headers=headers, auth=(get_login(cmd, config), get_password(cmd, config)))
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
    url = get_endpoint(cmd, config) + '/jobs' + '?max_results=50' + '&sort=-_updated'
    print('URL: {0}'.format(url))
    result = requests.get(url, headers=headers, auth=(get_login(cmd, config), get_password(cmd, config)))
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

def list_deployments(cmd, config):
    print("Listing deployments...")
    url = get_endpoint(cmd, config) + '/deployments?max_results=20&sort=-timestamp&where={"app_id":"' + cmd.app_id + '","module":"'+ cmd.module_name + '"}'
    print('URL: {0}'.format(url))
    result = requests.get(url, headers=headers, auth=(get_login(cmd, config), get_password(cmd, config)))
    handle_response_status_code(result)
    dhs = result.json().get('_items', [])

    x = PrettyTable(["Deploy ID", "Timestamp", "Application", "Module", "Revision", "Commit", "Last commit message"])
    for dh in dhs:
        x.add_row([dh.get('_id'), dh.get('timestamp'), dh.get('app_id'), dh.get('module'), dh.get('revision', ''), dh.get('commit'), ansi_escape(dh.get('commit_message', ''))[:32]])
    print(x)

def list_modules(cmd, config):
    print('listing modules')

def deploy(cmd, config):
    print("Deploying to app_id: {0}, module: {1}, in revision {2}...".format(cmd.app_id, cmd.module_name, cmd.revision or 'HEAD'))
    url = get_endpoint(cmd, config) + '/jobs' 
    job = {}
    job['command'] = 'deploy'
    job['app_id'] = cmd.app_id
    job['modules'] = [{'name': cmd.module_name, 'rev': cmd.revision or 'HEAD'}]
    result = requests.post(url, data=json.dumps(job), headers=headers, auth=(get_login(cmd, config), get_password(cmd, config)))
    handle_response_status_code(result)
    print(result.text)

def rollback(cmd, config):
    print('Rollbacking to deployment_id: {0}'.format(cmd.deployment_id))
    url = get_endpoint(cmd, config) + '/jobs' 
    job = {}
    job['app_id'] = cmd.app_id
    job['command'] = 'rollback'
    job['options'] = [cmd.deployment_id]
    result = requests.post(url, data=json.dumps(job), headers=headers, auth=(get_login(cmd, config), get_password(cmd, config)))
    handle_response_status_code(result)
    print(result.text)	

def execute_action(cmd, config):
    actions = { 'list-apps': list_apps, 'list-jobs': list_jobs, 
            'list-modules': list_modules, 'deploy': deploy, 'rollback': rollback,
            'list-deployments': list_deployments }
    actions[cmd.action](cmd, config)

if __name__ == '__main__':
    cmd = parse_cmdline()
    config = load_conf(cmd)
    execute_action(cmd, config)

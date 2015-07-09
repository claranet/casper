Casper is a command line tool that interacts with Ghost API
-----------------------------------------------------------
1) Setup credential file: ~/.casper

[Default]
endpoint=https://<client>.ghost.morea.fr
login=<yourlogin>
password=<yourpassword>

2) Install dependencies: 
pip install -r requirements.txt

3) Launch
python casper.py -h
usage: casper.py [-h] [--configure] [--debug]
                 {list-apps,list-modules,list-jobs,deploy,rollback} ...

Casper command line

positional arguments:
  {list-apps,list-modules,list-jobs,deploy,rollback}
                        actions help
    list-apps           list applications
    list-modules        list modules
    list-jobs           list jobs
    deploy              deploy module
    rollback            rollback module

optional arguments:
  -h, --help            show this help message and exit
  --configure
  --debug

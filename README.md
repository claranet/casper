Casper is a command line tool that interacts with Ghost API
-----------------------------------------------------------
1) Setup credential file: ~/.casper

    [Default]
    endpoint=https://<client>.ghost.morea.fr
    login=<yourlogin>
    password=<yourpassword>

2) Install dependencies:
    
    git clone casper 
    cd casper
    virtualenv casper_env
    source casper_env/bin/activate
    pip install -r requirements.txt
    deactivate

3) Launch:

    usage: casper.py [-h] [--configure] [--debug] [--login LOGIN]
                     [--password PASSWORD] [--endpoint ENDPOINT]
                     
                     {list-apps,list-modules,list-jobs,list-deployments,deploy,rollback}
                     ...
    
    Casper command line
    
    positional arguments:
      {list-apps,list-modules,list-jobs,list-deployments,deploy,rollback}
                            actions help
        list-apps           list applications
        list-modules        list modules
        list-jobs           list jobs
        list-deployments    list deployments
        deploy              deploy module
        rollback            rollback module
    
    optional arguments:
      -h, --help            show this help message and exit
      --configure
      --debug
      --login LOGIN
      --password PASSWORD
      --endpoint ENDPOINT

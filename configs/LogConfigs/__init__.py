import os,logging

choice  = int(os.getenv('LOG_CONFIG',1))
logfile = 'logs/logs.log'

if (choice != 1):
    raise NotImplementedError("Logging level unimplemented!")
else:
    logging.basicConfig(filename=logfile,level=logging.INFO)
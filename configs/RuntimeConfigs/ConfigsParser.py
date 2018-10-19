import hashlib, json

DEFAULT_algorithm   = hashlib.md5()
DEFAULT_numiter     = 100
DEFAULT_multicore   = False
DEFAULT_run_on_gpu  = False
DEFAULT_num_threads = 1
DEFAULT_saltsize    = 0
DEFAULT_saltspace   = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
DEFAULT_pw_space    = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
DEFAULT_pw_len      = 8

algorithm   = DEFAULT_algorithm
multicore   = DEFAULT_multicore
run_on_gpu  = DEFAULT_run_on_gpu
num_threads = DEFAULT_num_threads
saltsize    = DEFAULT_saltsize
saltspace   = DEFAULT_saltspace
numiter     = DEFAULT_numiter
pw_space    = DEFAULT_pw_space
pw_len      = DEFAULT_pw_len

def parseConfigs(configfile):
    with open(configfile,'r') as cfg_file:
        cfg = json.load(cfg_file)
    
    algo = cfg.get('algorithm','DEFAULT').lower()
    if algo == "sha1":
        algorithm = hashlib.sha1()
    elif algo == "sha256":
        algorithm = hashlib.sha256()
    elif algo == "sha384":
        algorithm = hashlib.sha384()
    elif algo == "sha512":
        algorithm = hashlib.sha512()
    else:
        algorithm = DEFAULT_algorithm
    
    multicore   = ( cfg.get("multicore" ,str(DEFAULT_multicore)).lower()    == "true" )
    run_on_gpu  = ( cfg.get("run_on_gpu",str(DEFAULT_run_on_gpu)).lower()   == "true" )
    num_threads = int   ( cfg.get( "num_threads"    , DEFAULT_num_threads   ))
    saltsize    = int   ( cfg.get( "saltsize"       , DEFAULT_saltsize      ))
    saltspace   = str   ( cfg.get( "saltspace"      , DEFAULT_saltspace     ))
    numiter     = int   ( cfg.get( "numiter"        , DEFAULT_numiter       ))
    pw_space    = str   ( cfg.get( "pw_space"       , DEFAULT_pw_space      ))
    pw_len      = int   ( cfg.get( "pw_len"         , DEFAULT_pw_len        ))

    return [algorithm,multicore,run_on_gpu,num_threads,saltsize,saltspace,numiter,pw_space,pw_len]

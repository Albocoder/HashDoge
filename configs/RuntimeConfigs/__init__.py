import os
import ConfigsParser
configfile = str(os.getenv('RUN_CONFIG','configs/RuntimeConfigs/configuration/config.json'))
[algorithm,multicore,run_on_gpu,num_threads,saltsize,saltspace] = ConfigsParser.parseConfigs(configfile)
ConfigsParser.algorithm     = algorithm
ConfigsParser.multicore     = multicore
ConfigsParser.run_on_gpu    = run_on_gpu
ConfigsParser.num_threads   = num_threads
ConfigsParser.saltsize      = saltsize
ConfigsParser.saltspace     = saltspace
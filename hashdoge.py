from rbt_gen_master import RbtGenMaster
from pwc_master import PwcMaster
from configs.LogConfigs import logfile
import argparse

### Clear logs
open(logfile, 'w').close()

parser = argparse.ArgumentParser( description='Welcome to `HashDoge`. Much hashes, such wow!' , epilog='Tool written by Erin "Albocoder" Avllazagaj. Highly recommended if you want slow CPU cracking.')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--crack_pws','-cpws',    nargs=1,             help='Cracks hash lists from hashes folder. Must specify rainbowtables\' folder name inside rainbowtables folder.',metavar=('RBT_FOLDER_NAME'))
group.add_argument('--create_rbts','-crbts', action='store_true', help='Creates rainbow tables from words in wordlists folder')
group.add_argument('--pipeline','-pip',      action='store_true', help='Runs full pipeline. Creates rainbow tables from wordlists folder then cracks hashes from hashes folder.')
parser.add_argument('--print_stats','-stats',action='store_true', help='Prints statistics in the end of each action taken')
# parser.add_argument('--plot_graph','-plot',  action='store_true', help='Plots graphs of results for each step of the process to show success rate')

# args = vars(parser.parse_args())

def run_rbt():
    rbt_master = RbtGenMaster()
    rbt_master.generateRbts()
    rbt_master.saveRbts()
    return rbt_master

def run_pwc(rbts):
    pwc_master = PwcMaster( rbts=rbts )
    pwc_master.crackPws()
    pwc_master.savePws()
    return pwc_master

def run_pwc_folder(fname):
    pwc_master = PwcMaster( foldername=fname )
    pwc_master.crackPws()
    pwc_master.savePws()
    return pwc_master

# if (args['pipeline']):
rbt_master = run_rbt()
    # if(args['print_stats']):
    #     print "========================== Rainbow Table Generation ===========================\n\n"
    #     rbt_master.showStatistics()
    #     print "\n\n===============================================================================\n"

pwc_master = run_pwc(rbt_master.getRbts())
    # if(args['print_stats']):
    #     print "================================ Hash cracking ===================================\n\n"
    #     pwc_master.showStatistics()
    #     print "\n\n===============================================================================\n"

# elif (args['create_rbts']):
#     rbt_master = run_rbt()
#     if(args['print_stats']):
#         print "========================== Rainbow Table Generation ===========================\n\n"
#         rbt_master.showStatistics()
#         print "\n\n===============================================================================\n"
# else:
#     rbt_fname = args['crack_pws'][0]
#     pwc_master = run_pwc_folder(rbt_fname)
#     if(args['print_stats']):
#         print "================================ Hash cracking ===================================\n\n"
#         pwc_master.showStatistics()
#         print "\n\n===============================================================================\n"
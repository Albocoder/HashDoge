from configs import *
from Queue import Queue
from rbt_gen_worker import RbtGenWorker
import random, string, os, json
import pandas as pd

class RbtGenMaster():

    def __init__(self):
        def foldername_generator(size=20, chars=string.ascii_uppercase + string.digits):
            return ''.join(random.choice(chars) for _ in range(size))
        self.WORKERS        = []
        self.queue          = Queue()
        self.log            = LogConfigs.logging.getLogger(__name__)
        self.foldername     = foldername_generator()
        self.save_path      = None
        while True:
            self.save_path = os.path.join( FileConfigs.RbTableConfigs.rbtable,self.foldername )
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
                break
            self.foldername = foldername_generator()

    def generateRbts(self):
        if(RuntimeConfigs.multicore):
            for i in range(0,RuntimeConfigs.num_threads):
                name            = "RbtWorker%d" %  (i+1)
                worker          = RbtGenWorker(self.queue,name)
                self.WORKERS.append(worker)
        else:
            worker              = RbtGenWorker(self.queue,__name__)
            self.WORKERS.append(worker)

        self.log.info( "RBT master has %d slaves" % len(self.WORKERS) )
        print( "RBT master has %d slaves" % len(self.WORKERS) )

        for w in self.WORKERS:
            print("RBT master lunched daemon[%s]" % w.getName())
            w.daemon = True
            w.start()

        self.numwords = 0
        for wl in FileConfigs.WordlistConfigs.getWordlists():
            with open(wl,'r') as pws:
                pw = pws.readline()
                while (pw):
                    pw = pw.strip()
                    self.queue.put(pw)
                    self.numwords += 1
                    pw = pws.readline()
        self.queue.join()

    def saveRbts(self):
        full_path = os.path.join(self.save_path,"rbtable."+FileConfigs.RbTableConfigs.ext)
        self.getRbts().to_json(full_path)

    def getSavePath(self):
        return self.save_path
    
    def getFolderName(self):
        return self.foldername
    
    def getRbts(self):
        combined_table = pd.concat([ w.getRainbowtable() for w in self.WORKERS ])
        combined_table = combined_table[~combined_table.index.duplicated(keep='first')]
        return combined_table

    def showStatistics(self):
        table_columns = len(self.getRbts().index)
        msg = "[i] Number of hashes in the rb table: %d" % table_columns
        print( msg )
        self.log.info( msg )
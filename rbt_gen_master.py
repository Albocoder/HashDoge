from configs import *
from Queue import Queue
from rbt_gen_worker import RbtGenWorker
import random, string, os, json

class RbtGenMaster():

    def __init__(self):
        def foldername_generator(size=20, chars=string.ascii_uppercase + string.digits):
            return ''.join(random.choice(chars) for _ in range(size))
        self.WORKERS        = []
        self.queue          = Queue()
        self.log            = LogConfigs.logging.getLogger(__name__)
        self.foldername    = foldername_generator()
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
        for w in self.WORKERS:
            self.log.info(  "%s hashed %d words." % (w.getName(),len(w.getRainbowtable().keys())) )
            if self.log.level == LogConfigs.logging.INFO:
                print(  "[i] %s hashed %d words." % (w.getName(),len(w.getRainbowtable().keys())) )
            with open(os.path.join(self.save_path,w.getName()+"_rbtable."+FileConfigs.RbTableConfigs.ext),'w') as saveout:
                json.dump(w.getRainbowtable(),saveout)

    def getSavePath(self):
        return self.save_path
    
    def getFolderName(self):
        return self.foldername
    
    def getRbts(self):
        return [ w.getRainbowtable() for w in self.WORKERS ]

    def showStatistics(self):
        self.numhashes = 0
        for w in self.WORKERS:
            self.numhashes += len(w.getRainbowtable().keys())
        msg = "[i] Number of hashes computed: %d" % self.numhashes
        print( msg )
        self.log.info( msg )
        msg = "[i] Total number of words: %d"  % self.numwords
        print( msg )
        self.log.info( msg )
        try:
            msg = "[i] Success rate: %f%%" % ( (100.0 * self.numwords) / float(self.numhashes) )
        except ZeroDivisionError as zde:
            msg = "[i] Success rate: 0.00%"
        print( msg )
        self.log.info( msg )
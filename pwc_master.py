from configs import FileConfigs, LogConfigs, RuntimeConfigs
from Queue import Queue
from pwc_worker import PwcWorker
from os import listdir
from os.path import isfile, join, abspath
import random, string, os, json

class PwcMaster():

    def __init__(self,foldername=None,rbts=None):
        def foldername_generator(size=20, chars=string.ascii_uppercase + string.digits):
            return ''.join(random.choice(chars) for _ in range(size))
        self.WORKERS    = []
        self.queue      = Queue()
        self.log        = LogConfigs.logging.getLogger(__name__)
        self.save_path  = None
        self.foldername = foldername

        if(rbts == None and foldername == None):
            raise Exception("Please declare the rainbow tables you want to use!")
        if(rbts == None):
            self.foldername = foldername
            self.log.info("Reading the rainbow tables!")
            rbpath = os.path.join(FileConfigs.RbTableConfigs.rbtable,foldername)
            self.save_path = os.path.join(FileConfigs.CrackedPwsConfigs.cracked,foldername)
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            self.rbts = []
            for f in listdir(rbpath):
                if ( isfile(join(rbpath, f)) and f[f.rindex(".")+1:] == FileConfigs.RbTableConfigs.ext ):
                    with open(join(rbpath, f),'r') as rbtfile:
                        self.rbts.append(json.load(rbtfile))
        else:
            self.rbts = rbts
            if (self.foldername == None):
                while True:
                    self.foldername = foldername_generator()
                    self.save_path = os.path.join( FileConfigs.CrackedPwsConfigs.cracked,self.foldername )
                    if not os.path.exists(self.save_path):
                        os.makedirs(self.save_path)
                        break
            else:
                self.save_path = os.path.join( FileConfigs.CrackedPwsConfigs.cracked,self.foldername )
        self.log.info("Password cracker ready to run!")

    def crackPws(self):
        if(RuntimeConfigs.multicore):
            for i in range(0,RuntimeConfigs.num_threads):
                name            = "PwcWorker%d" %  (i+1)
                worker          = PwcWorker(self.queue,self.rbts,name)
                self.WORKERS.append(worker)
        else:
            worker              = PwcWorker(self.queue,self.rbts,__name__)
            self.WORKERS.append(worker)

        self.log.info( "PWC master has %d slaves" % len(self.WORKERS) )
        print( "[i] PWC master has %d slaves" % len(self.WORKERS) )

        for w in self.WORKERS:
            print("[i] PWC master lunched daemon[%s]" % w.getName())
            w.daemon = True
            w.start()

        self.numhashes = 0
        for wl in FileConfigs.HashesConfigs.getHashFiles():
            with open(wl,'r') as hfile:
                hash_to_crack = hfile.readline()
                while (hash_to_crack):
                    hash_to_crack = hash_to_crack.strip()
                    self.queue.put(hash_to_crack.lower())
                    self.numhashes += 1
                    hash_to_crack = hfile.readline()
        self.queue.join()

    def savePws(self):
        for w in self.WORKERS:
            print(  "%s cracked %d hashes." % (w.getName(),len(w.getCrackedPws().keys())) )
            if self.log.level == LogConfigs.logging.INFO:
                print(  "[i] %s cracked %d hashes." % (w.getName(),len(w.getCrackedPws().keys())) )
            with open(os.path.join(self.save_path, w.getName()+"_pwcracks."+FileConfigs.CrackedPwsConfigs.ext),'w') as saveout:
                json.dump(w.getCrackedPws(),saveout)

    def getSavePath(self):
        return self.save_path
    
    def getCrackedPws(self):
        return [ w.getCrackedPws() for w in self.WORKERS ]
    
    def getFolderName(self):
        return self.foldername
    
    def showStatistics(self):
        self.numcracked = 0
        for w in self.WORKERS:
            self.numcracked += len(w.getCrackedPws().keys())
        msg = "[i] Number of hashes cracked: %d" % self.numcracked
        print( msg )
        self.log.info( msg )
        msg = "[i] Total number of hashes: %d"  % self.numhashes
        print( msg )
        self.log.info( msg )
        try:
            msg = "[i] Success rate: %f%%" % ((self.numcracked/float(self.numhashes))*100.0)
        except ZeroDivisionError as zde:
            msg = "[i] Success rate: 0.00%"
        print( msg )
        self.log.info( msg )
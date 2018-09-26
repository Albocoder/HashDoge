from configs import RuntimeConfigs,LogConfigs
from threading import Thread
from Queue import Queue
import hashlib


class PwcWorker(Thread):
    
    def __init__(self,queue,rbts,name="Random_PWC_Worker"):
        Thread.__init__(self)
        self.name           = name
        self.log            = LogConfigs.logging.getLogger("PWC_Worker["+name+"]")
        self.queue          = queue
        self.rainbowtables  = rbts
        self.cracked        = {}
    
    def run(self):
        while True:
            to_crack = self.queue.get()
            for rbt in self.rainbowtables:
                try:
                    cracked_pw = rbt[to_crack]
                    self.cracked[to_crack] = cracked_pw
                except:
                    pass
            self.queue.task_done()
    
    def getCrackedPws(self):
        self.log.info( "Returned back to master cracked list of size %d!" % len(self.cracked.keys()) )
        return self.cracked
    
    def getName(self):
        return self.name
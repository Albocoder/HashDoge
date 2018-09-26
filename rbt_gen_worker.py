from configs import RuntimeConfigs,LogConfigs
from threading import Thread
from Queue import Queue
import hashlib, itertools


class RbtGenWorker(Thread):
    
    def __init__(self,queue,name="Random_RBT_Worker"):
        Thread.__init__(self)
        self.name           = name
        self.log            = LogConfigs.logging.getLogger("RBT_Worker["+name+"]")
        self.queue          = queue
        self.rainbowtable   = {}
        self.salts          = []
        if( RuntimeConfigs.saltsize != 0 ):
            self.salts = [ ''.join(item) for item in itertools.product(RuntimeConfigs.saltspace, repeat=RuntimeConfigs.saltsize)]
    
    def run(self):
        while True:
            pw = self.queue.get()
            try:
                pw_encoded = pw.encode()
            except:
                self.log.error( "Failed to encode %s!" % pw )
                self.queue.task_done()
                continue

            for s in self.salts:
                sha1 = RuntimeConfigs.algorithm.copy()
                sha1.update((pw+s).encode())
                hashed = sha1.hexdigest()
                passwords = self.rainbowtable.get(hashed,[])
                passwords.append(pw)
                self.rainbowtable[hashed] = passwords

            sha1 = RuntimeConfigs.algorithm.copy()
            sha1.update(pw_encoded)
            hashed = sha1.hexdigest()
            passwords = self.rainbowtable.get(hashed,[])
            passwords.append(pw)
            self.rainbowtable[hashed] = passwords
            self.queue.task_done()
    
    def getRainbowtable(self):
        self.log.info( "Returned back to master rainbowtable of size %d!" % len(self.rainbowtable.keys()) )
        return self.rainbowtable
    
    def getName(self):
        return self.name
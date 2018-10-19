from configs import RuntimeConfigs,LogConfigs
from threading import Thread
from Queue import Queue
import hashlib, itertools
import pandas as pd

class RbtGenWorker(Thread):
    
    def __init__(self,queue,dataframe,name="Random_RBT_Worker"):
        Thread.__init__(self)
        self.name           = name
        self.log            = LogConfigs.logging.getLogger("RBT_Worker["+name+"]")
        self.queue          = queue
        self.rainbowtable   = []
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
                saltedpw = pw + s
                try:
                    salted_pw_encoded = saltedpw.encode()
                except:
                    self.log.error( "Failed to encode %s!" % saltedpw )
                    self.queue.task_done()
                    continue
                hashed = self.runChain(salted_pw_encoded)
                self.rainbowtable.append((hashed,saltedpw))
            
            hashed = self.runChain(pw_encoded)
            self.rainbowtable.append((hashed,pw))
            self.queue.task_done()
    
    def getRainbowtable(self):
        self.log.info( "[%s] - Returned back to master rainbowtable of size %d!" % 
            (self.name,len(self.rainbowtable)) )
        return pd.DataFrame(self.rainbowtable).rename({0:'hash',1:'password'},axis=1).set_index('hash')
    
    def getName(self):
        return self.name
    
    def runHasher(self,passw):
        hashing_function = RuntimeConfigs.algorithm.copy()
        hashing_function.update(passw.encode())
        hashed = hashing_function.hexdigest()
        return hashed

    def runReducer(self,someHash,colindex):
        results = []
        byteArray = self.getBytes(someHash)
        for i in range(RuntimeConfigs.pw_len):
            index = byteArray[(i + colindex) % len(byteArray)]
            newChar = RuntimeConfigs.pw_space[(index+i) % len(RuntimeConfigs.pw_space)]
            results.append(newChar)
        return str("".join(results))

    def runChain(self,pw_encoded):
        for col in range(RuntimeConfigs.numiter):
            hashed      = self.runHasher(pw_encoded)
            pwd         = self.runReducer(hashed, col)
            pw_encoded  = pwd.encode()
        return pwd
    
    # Copied from: https://github.com/jfmengels/rainbowtable-python/blob/master/rainbowGenerator.py
    def getBytes(self, hashV):
        results = []
        remaining = int(hashV, 16)
        while remaining > 0:
            results.append(remaining % 256)
            remaining //= 256
        return results
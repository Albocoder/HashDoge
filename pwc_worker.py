from configs import RuntimeConfigs,LogConfigs
from threading import Thread
from Queue import Queue
import hashlib
import pandas as pd


class PwcWorker(Thread):
    
    def __init__(self,queue,rbt,name="Random_PWC_Worker"):
        Thread.__init__(self)
        self.name           = name
        self.log            = LogConfigs.logging.getLogger("PWC_Worker["+name+"]")
        self.queue          = queue
        self.rainbowtable   = rbt
        self.cracked        = []
    
    def run(self):
        while True:
            to_crack = self.queue.get()
            cracked_pw = self.crackPw(to_crack)
            if(cracked_pw != None):
                self.cracked.append((to_crack,cracked_pw))
            self.queue.task_done()
    
    def crackPw(self,to_crack):
        if self.runReducer(to_crack,RuntimeConfigs.numiter-1) in self.rainbowtable.index:
            to_chain = self.rainbowtable[self.rainbowtable.index == self.runReducer(to_crack,RuntimeConfigs.numiter-1)]['password'][0]
            return self.runChain(to_chain,range(0,RuntimeConfigs.numiter-1))
        else:
            if RuntimeConfigs.numiter == 1:
                return None
            for i in range(RuntimeConfigs.numiter-2,-1,-1):
                reduction_in_ith_chain = self.runReducer(to_crack,i)
                result = self.runChain(reduction_in_ith_chain,range(i+1,RuntimeConfigs.numiter))
                if result in self.rainbowtable.index:
                    to_chain = self.rainbowtable[self.rainbowtable.index == result]['password'][0]
                    if(to_crack not in self.getHashesOfChain(to_chain)): # this removes false alarms
                        return None 
                    return self.runChain(to_chain,range(0,i))
            return None

    def getCrackedPws(self):
        if(self.cracked == []):
            self.log.info( "Returned back to master cracked list of size 0!" )
            return pd.DataFrame(columns=['hash','password']).set_index('hash')
        self.cracked = pd.DataFrame(self.cracked).rename({0:'hash',1:'password'},axis=1).set_index('hash') 
        self.log.info( "Returned back to master cracked list of size %d!" % len(self.cracked.index) )
        return self.cracked
    
    def getName(self):
        return self.name

    def runHasher(self,passw):
        hashing_function = RuntimeConfigs.algorithm.copy()
        hashing_function.update(passw.encode())
        hashed = hashing_function.hexdigest()
        return hashed

    def runChain(self,pw_encoded,indexrange):
        if indexrange == []:
            return pw_encoded
        for col in indexrange:
            hashed      = self.runHasher(pw_encoded)
            pwd         = self.runReducer(hashed, col)
            pw_encoded  = pwd.encode()
        return pwd
    
    def getHashesOfChain(self,pw_encoded):
        to_return = []
        for col in range(0,RuntimeConfigs.numiter):
            hashed      = self.runHasher(pw_encoded)
            pwd         = self.runReducer(hashed, col)
            pw_encoded  = pwd.encode()
            to_return.append(hashed)
        return to_return

    def runReducer(self,someHash,colindex):
        results = []
        byteArray = self.getBytes(someHash)
        for i in range(RuntimeConfigs.pw_len):
            index = byteArray[(i + colindex) % len(byteArray)]
            newChar = RuntimeConfigs.pw_space[(index+i) % len(RuntimeConfigs.pw_space)]
            results.append(newChar)
        return str("".join(results))
    
    # Copied from: https://github.com/jfmengels/rainbowtable-python/blob/master/rainbowGenerator.py
    def getBytes(self, hashV):
        results = []
        remaining = int(hashV, 16)
        while remaining > 0:
            results.append(remaining % 256)
            remaining //= 256
        return results
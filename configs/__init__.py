import LogConfigs
import FileConfigs
import RuntimeConfigs

log = LogConfigs.logging.getLogger("configurator")
log.info( "Hashes at: " + str(FileConfigs.HashesConfigs.getHashFiles()) )
log.info( "Wordlist at: " + str(FileConfigs.WordlistConfigs.getWordlists()) )
del log
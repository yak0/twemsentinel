import yaml
import redis
import threading
import logging
import os

class TwemSentinel(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.parseConfig()
        self.setLogger()
        try:
            self.redis = redis.StrictRedis(host=self.sentinel_ip, port=self.sentinel_port, db=0)
            self.pubsub = self.redis.pubsub()
            self.pubsub.subscribe(['+switch-master'])
        except:
            self.log.warn("Redis sentinel connection error")


    # Parse twemsentinel config file
    def parseConfig(self,):
        try:
            f = open("config.yml")
            configData = yaml.safe_load(f)
            self.sentinel_ip=configData["sentinel_ip"]
            self.sentinel_port=configData["sentinel_port"]
            self.config_file=configData["twemproxy_config_file"]
            self.restart_command=configData["nutcracker_restart_command"]
            self.log_file=configData["log_file"]
            f.close()
        except:
            self.log.warn("Config file could not open")

    # Updates the address of a server in the TwemProxy config
    def updateMasters(self,oldServer,oldPort,newServer,newPort):
        try:
            f = open(self.config_file)
            proxyData = yaml.safe_load(f)
            f.close()
        except:
            self.log.warn("Twemproxy config file could not open")
            return False
        changed=False
        for proxy in proxyData:
            for i,server in enumerate(proxyData[proxy]["servers"]):

                name=""
                try:
                    name = server.split(" ")[1]
                except:
                    pass
                host = server.split(" ")[0].split(":")[0]
                port = server.split(" ")[0].split(":")[1]
                number = server.split(" ")[0].split(":")[2]
                if str(host) == str(oldServer) and str(port) == str(oldPort):
                    host = newServer
                    port = newPort
                    number=1
                    proxyData[proxy]["servers"][i]=host+":"+str(port)+":"+str(number)+" "+name
                    changed=True
                    self.log.info('%s - %s:%s switch to %s:%s',name,oldServer,oldPort,host,port)

        try:
            f = open(self.config_file, "w")
            yaml.dump(proxyData, f, default_flow_style=False)
            f.close()
        except:
            self.log.warn('twemproxy config file could not update')
            return False
        return changed
    def setLogger(self):
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)
        handler = logging.FileHandler(self.log_file)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

    def run(self):
        for item in self.pubsub.listen():
            sentinel = str(item["data"]).split(" ")
            self.send(sentinel)
    def send(self,sentinel):
        if len(sentinel)>3:
            self.log.info('master changed')
            oldIp = sentinel[1]
            oldPort = sentinel[2]
            newIp = sentinel[3]
            newPort = sentinel[4]
            if(self.updateMasters(oldIp,oldPort,newIp,newPort)):
                self.restartTwemProxy()
        else:
            err = 'master update error (%s:%s --> %s:%s)' % (oldIp,oldPort,newIp,newPort)
            self.log.warn(err)

    def restartTwemProxy():
        os.system(self.restart_command)

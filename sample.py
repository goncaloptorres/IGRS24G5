## Kamailio - equivalent of routing blocks in Python
import sys
import Router.Logger as Logger
import KSR as KSR
from concurrent import futures
import logging

import grpc

def dumpObj(obj):
    for attr in dir(obj):
        # KSR.info("obj.%s = %s\n" % (attr, getattr(obj, attr)));
        Logger.LM_INFO("obj.%s = %s\n" % (attr, getattr(obj, attr)));

# global function to instantiate a kamailio class object
# -- executed when kamailio app_python module is initialized
def mod_init():
    KSR.info("===== from Python mod init\n")
    return kamailio();

# -- {start defining kamailio class}
class kamailio:
    def __init__(self):
        KSR.info('===== kamailio.__init__\n');
    
    # executed when kamailio child processes are initialized
    def child_init(self, rank):
        KSR.info('===== kamailio.child_init(%d)\n' % rank);
        return 0

    # SIP request routing
    # -- equivalent of request_route{}
    def ksr_request_route(self, msg):
        KSR.info("===== request - from kamailio python script\n")
        KSR.info("===== method [%s] r-uri [%s]\n" % (KSR.pv.get("$rm"),KSR.pv.get("$ru")))
        if KSR.is_REGISTER():
            KSR.registrar.save("location", 0)
      ## Kamailio - equivalent of routing blocks in Python
import sys
import Router.Logger as Logger
import KSR as KSR
from concurrent import futures
import logging

import grpc

def dumpObj(obj):
    for attr in dir(obj):
        # KSR.info("obj.%s = %s\n" % (attr, getattr(obj, attr)));
        Logger.LM_INFO("obj.%s = %s\n" % (attr, getattr(obj, attr)));

# global function to instantiate a kamailio class object
# -- executed when kamailio app_python module is initialized
def mod_init():
    KSR.info("===== from Python mod init\n")
    return kamailio();

# -- {start defining kamailio class}
class kamailio:
    def __init__(self):
        KSR.info('===== kamailio.__init__\n');
    
    # executed when kamailio child processes are initialized
    def child_init(self, rank):
        KSR.info('===== kamailio.child_init(%d)\n' % rank);
        return 0

    # SIP request routing
    # -- equivalent of request_route{}
    def ksr_request_route(self, msg):
        dominio = KSR.pv.get("$ru")
        KSR.info("===== request - from kamailio python script\n")
        KSR.info("===== method [%s] r-uri [%s]\n" % (KSR.pv.get("$rm"),KSR.pv.get("$ru")))
        
        if KSR.is_REGISTER() and dominio == "sip:acme.pt":
            KSR.registrar.save("location", 0)
            return 1
        else:
            KSR.info("===== Comparação Falhou: Dominio [%s], Esperado [sip:acme.pt] =====\n" % dominio)
        
        if KSR.registrar.lookup("location") == 1:
            KSR.info("=== Destination found. Fowarding the call =====\n")
            KSR.tm.t_relay()
            return 1
        else:
            KSR.info("===== Destination not found in location table =====\n")
            KSR.sl.send_reply(404, "User Not Found")
            return 1 
#ring ring
#fala baixo

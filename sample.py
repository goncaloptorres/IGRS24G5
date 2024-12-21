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
        
        # Regista Utilizadores com domínio "acme.pt"
        
        endereco = KSR.pv.get("$ru")
        KSR.info("===== request - from kamailio python script\n")
        KSR.info("===== method [%s] r-uri [%s]\n" % (KSR.pv.get("$rm"),KSR.pv.get("$ru")))
        if KSR.is_REGISTER() and endereco == "sip:acme.pt":
            KSR.registrar.save("location", 0)
            return 1
        else:
            KSR.info("===== Comparação Falhou: Endereco [%s], Esperado [sip:acme.pt] =====\n" % endereco)
        
        # Valida utilizadores com PIN
        
        if KSR.is_MESSAGE():
            val = KSR.pv.get("$ru")
            msg = KSR.pv.get("$rb")
            usr = KSR.pv.get("$fu")
            KSR.info("Destinatário: " + val + ", Mensagem: " + msg + ", Utilizador: " + usr)
            if val == "sip:validar@acme.pt" and msg == '0000':
                KSR.sl.send_reply(200, "PIN válido")
                KSR.info("PIN válido")
            else:
                KSR.sl.send_reply(403, "Forbidden - PIN inválido")
                
        
        # Realiza chamadas entre utilizadores registados
        
        if KSR.registrar.lookup("location") == 1:
            dominio = KSR.pv.get("$fd")
            if dominio != "acme.pt":
                KSR.info("===== Blocked because user belongs to external domain [%s] =====\n" % dominio)
                return 1
            KSR.info("=== Destination found. Fowarding the call [%s] =====\n" % dominio)
            KSR.tm.t_relay()
            return 1  
        else:
            KSR.info("===== Destination not found in location table =====\n")
            KSR.sl.send_reply(404, "User Not Found")
            
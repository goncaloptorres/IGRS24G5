## Kamailio - equivalent of routing blocks in Python
import sys
import Router.Logger as Logger
import KSR as KSR
from concurrent import futures
import logging
import grpc

conferencia = list()

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
        
        domain = KSR.pv.get("$fd")
        KSR.info("===== request - from kamailio python script\n")
        KSR.info("===== method [%s] r-uri [%s]\n" % (KSR.pv.get("$rm"),KSR.pv.get("$ru")))
        if KSR.is_REGISTER() and domain == "acme.pt":
            KSR.registrar.save("location", 0)
            KSR.sl.send_reply(200, "Utilizador registado")
            return 1
        else:
            KSR.info("===== Comparação Falhou: Endereco [%s], Esperado [acme.pt] =====\n" % domain)
            KSR.sl.send_reply(403, "Utilizador não foi registado. Domínio inválido")
        
        # Valida utilizadores com PIN
        
        if KSR.is_MESSAGE():
            val = KSR.pv.get("$ru")
            msg = KSR.pv.get("$rb").strip()
            usr = KSR.pv.get("$fu")
            KSR.info("Destinatário: " + val + ", Mensagem: " + msg + ", Utilizador: " + usr)
            KSR.info(msg == '0000')
            if val == "sip:validar@acme.pt" and msg == '0000':
                KSR.sl.send_reply(200, "PIN válido")
                KSR.info("PIN válido")
            else:
                KSR.sl.send_reply(403, "Forbidden - PIN inválido")
                
        # Realiza chamadas entre utilizadores registados
        
        if KSR.is_INVITE():
            KSR.info("Destino: " + (KSR.pv.get("$tu")))
            
            if KSR.pv.get("$tu") == "sip:conferencia@acme.pt":
                KSR.info("ENTREI")
                KSR.pv.sets("$ru", "sip:conferencia@127.0.0.1:5090")
                KSR.rr.record_route()
                KSR.tm.t_relay()
                return 1
                    
            if KSR.registrar.lookup("location") == 1:
            
                if domain != "acme.pt":
                    KSR.info("===== Blocked because user belongs to external domain [%s] =====\n" % domain)
                    KSR.sl.send_reply(403, "Bloqueado porque o utilizador não pertence ao domínio acme.pt")
                    return 1
            
                KSR.info("=== Destination found. Fowarding the call [%s] =====\n" % domain)
                KSR.tm.t_relay()
                KSR.sl.send_reply(200, "Destino encontrado. A reencaminhar a chamada")
                return 1  
        
        else:
            KSR.info("===== Destination not found in location table =====\n")
            KSR.sl.send_reply(404, "User Not Found")

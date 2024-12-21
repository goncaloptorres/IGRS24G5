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
        
        #Nao está tudo certo
        #Um utilizador nao registado consegue fazer chamadas para um registado
        
        if KSR.registrar.lookup("location") == 1:
            dominio = KSR.pv.get("$fd")
            
            if not dominio:
                KSR.err("===== Domain not found or invalid in destination =====\n")
                KSR.sl.send_reply(500, "Internal Server Error")
                return 1
    
            if dominio != "acme.pt":
                KSR.info("===== Blocked because user belongs to external domain [%s] =====\n" % dominio)
                return 1
            
            KSR.info("=== Destination found. Fowarding the call [%s] =====\n" % dominio)
            if not KSR.tm.t_relay():
                KSR.err("===== Failed to forward the call to [%s] =====\n" % dominio)
                KSR.sl.send_reply(500, "Internal Server Error")
                return 1
        else:
            KSR.info("===== Destination not found in location table =====\n")
            KSR.sl.send_reply(404, "User Not Found")
            return 1
        
        
        #Os utilizadores pretendem que seja feito o reencaminhamento avançado das suas chamadas cujo URI destino contenha o domínio acme.pt
        #Nada foi testado!
        
        #Validate the origin domain
def check_origin_domain(self):
    from_domain = KSR.pv.get("$fu")  # Get 'From' URI
    if "@acme.pt" in from_domain:
        KSR.info("===== Origin domain is valid: [%s] =====\n" % from_domain)
        return True
    else:
        KSR.info("===== Invalid origin domain: [%s] =====\n" % from_domain)
        return False

def handle_invite_request(self):
    if KSR.is_INVITE():
        KSR.info("===== Handling INVITE request =====\n")
        
        # Validate the origin domain
        if self.check_origin_domain():
            # Try to route the call
            if self.route_call():
                return 1
            else:
                KSR.sl.send_reply(404, "User Not Found")
                return 1
        else:
            # Invalid domain
            KSR.sl.send_reply(403, "Forbidden - Unauthorized Domain")
            return 1

def check_destination_availability(self, destination_uri):
    """
    Verifica se o destinatário está registado e disponível.
    """
    # Simula a verificação no registo SIP. Normalmente, isso seria uma consulta ao servidor de registo SIP.
    # Aqui estamos assumindo que KSR.pv.get(destination_uri) retorna o estado de registo.
    if KSR.pv.get(destination_uri):
        KSR.info("===== Destination [%s] is registered and available =====\n" % destination_uri)
        return True
    else:
        KSR.info("===== Destination [%s] is not registered or unavailable =====\n" % destination_uri)
        return False


#No caso do funcionário destino estar registado e disponível o pedido de sessão é reencaminhado de forma usual.
#O servidor SIP deverá efetuar este reencaminhamento como um proxy.

def route_call(self):
    """
    Reencaminha a chamada SIP para o destinatário, se estiver disponível.
    """
    destination_uri = self.get_destination_uri()  # Função que retorna o URI do destinatário da chamada
    if self.check_destination_availability(destination_uri):
        # Se o destinatário estiver disponível, reencaminha a chamada normalmente.
        KSR.send_to(destination_uri)  # Envia o pedido INVITE para o destinatário
        KSR.info("===== Call routed to: [%s] =====\n" % destination_uri)
        return True
    else:
        # Se o destinatário não estiver disponível, responde com erro adequado.
        KSR.sl.send_reply(404, "User Not Found")  # Resposta SIP 404
        return False

def handle_invite_request(self):
    if KSR.is_INVITE():
        KSR.info("===== Handling INVITE request =====\n")
        
        # Validar o domínio de origem
        if self.check_origin_domain():
            # Tentar reencaminhar a chamada
            if self.route_call():
                return 1
            else:
                # Caso o reencaminhamento falhe, a resposta já foi enviada dentro da função route_call.
                return 1
        else:
            # Resposta se o domínio de origem não for autorizado.
            KSR.sl.send_reply(403, "Forbidden - Unauthorized Domain")
            return 1

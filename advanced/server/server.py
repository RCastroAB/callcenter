from __future__ import annotations

from typing import Tuple, List, Dict, Union
from twisted.internet import reactor, protocol, endpoints
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
import string
import argparse
import cmd
import time
import json

def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument("--num_operators", '-n', type=int, default=2, help="Number of operators available")
    return args.parse_args()






class Operator:
    def __init__(self, id: str) -> None:
        self.id = id
        self.status = "available"
        self.call = None


class Queues:
    def __init__(self, num_operators: int) -> None:
        self.ascii_chars = string.ascii_uppercase
        self.num_operators = num_operators
        assert num_operators <= len(self.ascii_chars)
        self.operators: List[Operator] = []
        for i in range(num_operators):
            self.operators.append(Operator(string.ascii_uppercase[i]))
        self.call_map: Dict[int, int] = {}
        self.call_queue: List[int] = []


    def ring(self, opidx: int, call: int, server: Server) -> None:
        server.respondJSON(f"Call {call} ringing for operator {self.operators[opidx].id}")
        self.operators[opidx].status = "ringing"
        self.operators[opidx].call = call
        self.call_map[call] = opidx


    def receive_call(self, call: str, server: Server) -> None:
        server.respondJSON(f"Call {call} received")
        self.allocate_call(call, server)

    def allocate_call(self, call:str, server: Server) -> None:
        call = int(call)
        #iterate over all operators seeking first one available.
        for i in range(self.num_operators):
            if self.operators[i].status == "available":
                self.ring(i, call, server)
                return
        #No available operators
        self.call_queue.append(call)
        server.respondJSON(f"Call {call} waiting in queue")

    def answer_call(self, opid:str, server: Server) -> None:
        idx = list(self.ascii_chars).index(opid)
        operator = self.operators[idx]
        operator.status = "oncall"
        server.respondJSON(f"Call {operator.call} answered by operator {operator.id}")


    def hangup_call(self, call:str, server: Server) -> None:
        call = int(call)
        #if call was waiting, print missed
        if call in self.call_queue:
            self.call_queue.remove(call)
            server.respondJSON(f"Call {call} missed")
        elif self.operators[self.call_map[call]].status == "ringing":
            opidx = self.call_map[call]
            operator = self.operators[opidx]
            operator.status = "available"
            operator.call = None
            del self.call_map[call]
            server.respondJSON(f"Call {call} missed")
            if len(self.call_queue) > 0:
                self.ring(opidx, self.call_queue.pop(0), server)
        else:
            #else finish the call propperly
            opidx = self.call_map[call]
            operator = self.operators[opidx]
            operator.status = "available"
            operator.call = None
            del self.call_map[call]
            server.respondJSON(f"Call {call} finished and operator {operator.id} available")
            if len(self.call_queue) > 0:
                self.ring(opidx, self.call_queue.pop(0), server)

    def reject_call(self, opid: str, server: Server) -> None:
        idx = list(self.ascii_chars).index(opid)
        operator = self.operators[idx]
        call = operator.call
        operator.call = None
        operator.status = "available"
        server.respondJSON(f"Call {call} rejected by operator {operator.id}")
        self.allocate_call(call, server)





class Server(Protocol):
    def __init__(self, queues: Queues, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self.queues = queues

    def dataReceived(self, data):
        self.parse_command(data)

    def connectionMade(self):
        print("Connected ")

    def parse_command(self, data):
        commands = {
            'call': self.queues.receive_call,
            'answer': self.queues.answer_call,
            'hangup': self.queues.hangup_call,
            'reject': self.queues.reject_call,
        }
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            print("Error")
            return
        func = commands[data["command"]]
        func(data["id"], self)


    def respondJSON(self, message):
        data = {'response': message}
        data = json.dumps(data) + "\r\n"
        data =  bytes(data, 'utf-8')
        self.transport.write(data)

class ServerFactory(Factory):
    def __init__(self, queues, *args, **kwargs):
        super(ServerFactory, self).__init__(*args, **kwargs)
        self.queues = queues

    def buildProtocol(self, addr):
        return Server(self.queues)





def main():
    args = parse_args()
    queues = Queues(num_operators=args.num_operators)
    endpoint = endpoints.serverFromString(reactor, "tcp:5678").listen(ServerFactory(queues))
    reactor.run()
    # prompt = Prompt()
    # prompt.cmdloop()

if __name__=="__main__":
    main()

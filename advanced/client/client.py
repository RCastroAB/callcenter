# from __future__ import annotations
from typing import Tuple, List, Dict, Union
import string
import cmd
import json
from twisted.internet import protocol, reactor, endpoints




class Prompt(cmd.Cmd):
    intro = "Available Commands:\ncall <id>\nanswer <id>\nreject <id>\nhangup <id>\nexit"

    def sendJSON(self, command, id):
        data = {"command": command, "id": id}
        data = json.dumps(data)
        self.server.transport.write(bytes(data, "utf-8"))

    def do_call(self, args:str) -> None:
        self.sendJSON("call", args)

    def do_answer(self, args:str) -> None:
        self.sendJSON("answer", args)

    def do_reject(self, args:str) -> None:
        self.sendJSON("reject", args)


    def do_hangup(self, args:str) -> None:
        self.sendJSON("hangup", args)

    def do_EOF(self, args: str) -> None:
        print("\n", end="")
        return self.do_exit(args)
    def do_exit(self, args:str) -> bool:
        print("Goodbye")
        reactor.stop()


class Client(protocol.Protocol):
    def __init__(self, prompt: Prompt, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.prompt = prompt
        self.prompt.server = self

    def loop(self):
        print(self.prompt.prompt, end="")
        self.prompt.onecmd(input())

    def decodeResponse(self, data):
        data = json.loads(data)
        print(data['response'])

    def dataReceived(self, data):
        data = data.decode("utf-8").split('\n')[:-1]
        for datum in data:
            self.decodeResponse(datum)
        self.loop()

    def connectionMade(self):
        self.loop()

class ClientFactory(protocol.ClientFactory):
    def __init__(self, prompt: Prompt, *args, **kwargs):
        super(ClientFactory, self).__init__(*args, **kwargs)
        self.prompt = prompt


    def buildProtocol(self, addr):
        return Client(self.prompt)




def main():
    prompt = Prompt()
    print(prompt.intro)
    reactor.connectTCP("server", 5678, ClientFactory(prompt))
    reactor.run()

if __name__=="__main__":
    main()

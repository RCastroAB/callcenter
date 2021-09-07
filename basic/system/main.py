from typing import Tuple, List, Dict, Union
import string
import argparse
import cmd
import time

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


    def ring(self, opidx: int, call: int) -> None:
        print(f"Call {call} ringing for operator {self.operators[opidx].id}")
        self.operators[opidx].status = "ringing"
        self.operators[opidx].call = call
        self.call_map[call] = opidx


    def receive_call(self, call: int) -> None:
        #iterate over all operators seeking first one available.
        for i in range(self.num_operators):
            if self.operators[i].status == "available":
                self.ring(i, call)
                return
        #No available operators
        self.call_queue.append(call)
        print(f"Call {call} waiting in queue")

    def answer_call(self, opid:str) -> None:
        idx = list(self.ascii_chars).index(opid)
        operator = self.operators[idx]
        operator.status = "oncall"
        print(f"Call {operator.call} answered by operator {operator.id}")


    def hangup_call(self, call:int) -> None:
        #if call was waiting, print missed
        if call in self.call_queue:
            self.call_queue.remove(call)
            print(f"Call {call} missed")
        elif self.operators[self.call_map[call]].status == "ringing":
            opidx = self.call_map[call]
            operator = self.operators[opidx]
            operator.status = "available"
            operator.call = None
            del self.call_map[call]
            print(f"Call {call} missed")
        else:
            #else finish the call propperly
            opidx = self.call_map[call]
            operator = self.operators[opidx]
            operator.status = "available"
            operator.call = None
            del self.call_map[call]
            print(f"Call {call} finished and operator {operator.id} available")
            if len(self.call_queue) > 0:
                self.ring(opidx, self.call_queue.pop(0))

    def reject_call(self, opid: str) -> None:
        idx = list(self.ascii_chars).index(opid)
        operator = self.operators[idx]
        call = operator.call
        operator.call = None
        operator.status = "available"
        print(f"Call {call} rejected by operator {operator.id}")
        self.receive_call(call)






class Prompt(cmd.Cmd):
    intro = "Available Commands:\ncall <id>\nanswer <id>"

    def do_call(self, args:str) -> None:
        try:
            call = int(args)
        except ValueError:
            print(f"Unknown argument {args}")
        print(f"Call {call} received")
        operator = self.queues.receive_call(call)


    def do_answer(self, args:str) -> None:
        assert args in list(string.ascii_uppercase)
        self.queues.answer_call(args)

    def do_reject(self, args:str) -> None:
        assert args in list(string.ascii_uppercase)
        self.queues.reject_call(args)


    def do_hangup(self, args:str) -> None:
        try:
            call = int(args)
        except ValueError:
            print(f"Unknown argument {args}")
        self.queues.hangup_call(call)

    def do_EOF(self, args: str) -> None:
        print("\n", end="")
        return self.do_exit(args)
    def do_exit(self, args:str) -> bool:
        print("Goodbye")
        return True

def main():
    args = parse_args()
    prompt = Prompt()
    prompt.queues = Queues(num_operators=args.num_operators)
    prompt.cmdloop()

if __name__=="__main__":
    main()

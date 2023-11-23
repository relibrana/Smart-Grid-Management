from pade.misc.utility import display_message, start_loop
from pade.behaviours.protocols import TimedBehaviour
from pade.core.agent import Agent
from pade.acl.aid import AID
from threading import Thread
from sys import argv
import random
import sys
from gui import run_simple_screen


class PowerSourceTimedBehaviour(TimedBehaviour):
    def __init__(self, agent, time):
        super(PowerSourceTimedBehaviour, self).__init__(agent, time)

    def on_time(self):
        super(PowerSourceTimedBehaviour, self).on_time()
        self.agent.recharge()


class ConsumerTimedBehaviour(TimedBehaviour):
    def __init__(self, agent, time):
        super(ConsumerTimedBehaviour, self).__init__(agent, time)

    def on_time(self):
        super(ConsumerTimedBehaviour, self).on_time()
        self.agent.set_demand()


class SGMTimedBehaviour(TimedBehaviour):
    def __init__(self, agent, time):
        super(SGMTimedBehaviour, self).__init__(agent, time)

    def on_time(self):
        super(SGMTimedBehaviour, self).on_time()
        self.agent.distribute_power()
        self.agent.display_status()

class PowerSourceAgent(Agent):
    def __init__(self, aid, capacity):
        super().__init__(aid=aid)
        self.capacity = capacity
        self.available_capacity = capacity
        
        behaviour = PowerSourceTimedBehaviour(self, 10.0)
        self.behaviours.append(behaviour)

    def on_start(self):
        super().on_start()
        display_message(self.aid.localname, f"Power source started with capacity: {self.capacity}")

    def generate_power(self, amount):
        if amount <= self.available_capacity:
            self.available_capacity -= amount
            return amount
        else:
            generated_power = self.available_capacity
            self.available_capacity = 0
            return generated_power

    def recharge(self):
        self.available_capacity = self.capacity
        
    def on_time(self):
        super().on_time()
        display_message(self.aid.localname, "on time!")


class ConsumerAgent(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid)
        self.set_demand()
        
        behaviour = ConsumerTimedBehaviour(self, 5.0)
        self.behaviours.append(behaviour)

    def on_start(self):
        super().on_start()
        display_message(self.aid.localname, f"Consumer started with demand: {self.demand}")

    def consume_power(self, amount):
        self.demand -= amount
        if self.demand < 0:
            self.demand = 0

    def needs_power(self):
        return self.demand > 0
    
    def set_demand(self):
        self.demand = random.randint(20, 80)


class SmartGridAgent(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid)
        self.power_sources = []
        self.consumers = []
        
        behaviour = SGMTimedBehaviour(self, 5.0)
        self.behaviours.append(behaviour)

    def add_power_source(self, power_source_agent):
        self.power_sources.append(power_source_agent)

    def add_consumer(self, consumer_agent):
        self.consumers.append(consumer_agent)

    def distribute_power(self):
        for consumer_agent in self.consumers:
            if consumer_agent.needs_power():
                for power_source_agent in self.power_sources:
                    power_available = power_source_agent.generate_power(
                        consumer_agent.demand)
                    consumer_agent.consume_power(power_available)
                    if not consumer_agent.needs_power():
                        break

    def display_status(self):
        for power_source_agent in self.power_sources:
            display_message(power_source_agent.aid.localname, f"Available Capacity: {power_source_agent.available_capacity}")

        for consumer_agent in self.consumers:
            display_message(consumer_agent.aid.localname, f"Demand: {consumer_agent.demand}")


def agentsexec():
    start_loop(agents)


if __name__ == '__main__':
    # pygame_thread = Thread(target=run_simple_screen())
    # pygame_thread.start()
    
    c = 0
    agents = list()
    pws = list()
    cons = list()
    
    # set up power sources 
    sources = 20
    for i in range(sources):
        port = int(argv[1]) + c
        agent_name = 'powersource_agent_{}_{}@localhost:{}'.format(i, port, port)
        source_agent = PowerSourceAgent(AID(name=agent_name), random.randint(250, 350))
        agents.append(source_agent)
        pws.append(source_agent)
        c += 100

    # set up consumers
    consumers = 50
    for i in range(consumers):
        port = int(argv[1]) + c
        agent_name = 'consumer_agent_{}_{}@localhost:{}'.format(i, port, port)
        consumer_agent = ConsumerAgent(AID(name=agent_name))
        agents.append(consumer_agent)
        cons.append(consumer_agent)
        c += 100
        
    # set up smart grid management
    port = int(argv[1]) + c
    name = 'smartgrid_agent_{}@localhost:{}'.format(port, port)
    sgm = SmartGridAgent(AID(name=name))
    
    # add our agents to the management
    for i in pws:
        sgm.add_power_source(i)
        
    for i in cons:
        sgm.add_consumer(i)
        
    agents.append(sgm)
    
    agentsexec()
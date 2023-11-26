import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN
from pade.misc.utility import display_message, start_loop
from pade.behaviours.protocols import TimedBehaviour
from pade.core.agent import Agent
from pade.acl.aid import AID
from threading import Thread
from sys import argv
import random
import sys

# Constants
WHITE = (255, 255, 255)

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((600, 800))  # Ajustar el ancho de la ventana
pygame.display.set_caption("Smart Grid Visualization")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

# Headless mode flag
headless_mode = False

# Botón
button_rect = pygame.Rect(500, 10, 80, 30)
button_color = (0, 255, 0)  # Verde

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

        # Cargar imagen de fuente de energía
        self.image = pygame.image.load("vb_universal.jpg")
        self.image = pygame.transform.scale(self.image, (30, 30))

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

    def draw(self):
        transparency = 255  # Valor predeterminado (sin transparencia)

        if self.available_capacity <= 0:
            # Cambiar transparencia al 50%
            transparency = 128 

        # No es necesario ajustar las coordenadas, ya que estas dependen de la lógica de tu juego
        self.image.set_alpha(transparency)
       # screen.blit(self.image, (150, 400))

        text = font.render(f"{self.available_capacity}", True, WHITE)
       # screen.blit(text, (150, 380))
        

class ConsumerAgent(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid)
        self.set_demand()

        behaviour = ConsumerTimedBehaviour(self, 5.0)
        self.behaviours.append(behaviour)

        # Cargar imagen de consumidor con transparencia
        self.image = pygame.image.load("foquito.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))

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

    def draw(self):
        transparency = 255  # Valor predeterminado (sin transparencia)

        if self.demand <= 0:
            # Cambiar transparencia al 50%
            transparency = 128 

        # No es necesario ajustar las coordenadas, ya que estas dependen de la lógica de tu juego
        self.image.set_alpha(transparency)
        #screen.blit(self.image, (150, 400))

        text = font.render(f"{self.demand}", True, WHITE)
       # screen.blit(text, (150, 380))
        

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
                    power_available = power_source_agent.generate_power(consumer_agent.demand)
                    consumer_agent.consume_power(power_available)
                    if not consumer_agent.needs_power():
                        break

    def display_status(self):
        for power_source_agent in self.power_sources:
            display_message(power_source_agent.aid.localname, f"Available Capacity: {power_source_agent.available_capacity}")

        for consumer_agent in self.consumers:
            display_message(consumer_agent.aid.localname, f"Demand: {consumer_agent.demand}")

    def draw(self):
        row_spacing = 50  # Ajusta según tus preferencias

        for i, power_source_agent in enumerate(self.power_sources):
            row = i // 10
            col = i % 10
            screen.blit(power_source_agent.image, (50 + col * 40, 250 + row * (30 + row_spacing)))    
            text = font.render(f"{power_source_agent.available_capacity}", True, WHITE)
            screen.blit(text, (50 + col * 40, 230 + row * (30 + row_spacing)))

        for i, consumer_agent in enumerate(self.consumers):
            row = i // 10
            col = i % 10
            screen.blit(consumer_agent.image, (50 + col * 40, 400 + row * (30 + row_spacing)))
                   
            text = font.render(f"{consumer_agent.demand}", True, WHITE)
            screen.blit(text, (50 + col * 40, 380 + row * (30 + row_spacing)))




if __name__ == '__main__':
    c = 0
    agents = list()
    pws = list()
    cons = list()

    # set up power sources
    sources = 10
    for i in range(sources):
        port = int(argv[1]) + c
        agent_name = 'powersource_agent_{}_{}@localhost:{}'.format(i, port, port)
        source_agent = PowerSourceAgent(AID(name=agent_name), random.randint(250, 350))
        agents.append(source_agent)
        pws.append(source_agent)
        c += 100

    # set up consumers
    consumers = 30
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

    def agentsexec():
        start_loop(agents)

    pygame_thread = Thread(target=agentsexec)
    pygame_thread.start()

    while True:
        
       
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    headless_mode = not headless_mode

        screen.fill((0, 0, 0))
        
              #Draw legend
        text = font.render("Legend", True, WHITE)
        screen.blit(text, (20, 20))

        image = pygame.image.load("vb_universal.jpg")   
        image = pygame.transform.scale(image, (30, 30))
        screen.blit(image, (20, 50))
        text = font.render("Power Source", True, WHITE)
        screen.blit(text, (60, 50))

              
        image2 = pygame.image.load("foquito.png")
        image2 = pygame.transform.scale(image2, (30, 30))
        screen.blit(image2, (20, 100))
        text = font.render("Consumer", True, WHITE)
        screen.blit(text, (60, 100))

         # Dibujar el botón
        pygame.draw.rect(screen, button_color, button_rect)
        text = font.render(" ", True, WHITE)
        screen.blit(text, (button_rect.x + 10, button_rect.y + 8))

        if not headless_mode:
            for agent in agents:
                agent.draw()

        pygame.display.flip()
        clock.tick(30)

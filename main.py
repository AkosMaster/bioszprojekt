# Dúcz Ákos 2020

import pygame, sys, random, time, copy, math
from pygame.locals import *

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

# beállítások
fieldsize = 300;
fieldscale = 3;
BGCOLOR=(0,0,0);
ACTORCOLOR=(255,0,0);
FOODCOLOR=(207,184,118);
timestep = 0;
ticks_until_starvation = 3000;
starting_food_count = 20 * 3 * 3;
food_spawn_delay = 300 / 3 / 3; # 300

class actor():
    posX = 0;
    posY = 0;
    hunger = 0;

    #genetics
    speed = 1;
    is_carnivore = False;

    def __init__(self, x, y):
        self.posX = x;
        self.posY = y;

class food():
    posX = 0;
    posY = 0;

    def __init__(self, x, y):
        self.posX = x;
        self.posY = y;

# kezdeti lények és ételek elhelyezése
actors = [actor(fieldsize/2,fieldsize/2)];
foods = [];
while len(foods) < starting_food_count:
    posX = random.randint(0, fieldsize-1);
    posY = random.randint(0, fieldsize-1);
    foods.append(food(posX, posY));

tick_count = 0;
ticks_since_food_spawn = 0;

# grafikon
plt.ion();
plt.show();
plt.ylim(0, 10);
plt.xlabel('lépések száma');
plt.ylabel(' ');

last_values = {};
last_updated_graph = 0;

update_interval = 100
def plot_graph(value, line, _label):
    global last_updated_graph;

    #if last_updated_graph < update_interval:
    #    last_updated_graph += 1;
    #    return;

    if not tick_count % update_interval == 0:
        return;

    if not line in last_values:
        last_values[line] = 0;

    point1 = [tick_count-update_interval, last_values[line]];
    point2 = [tick_count, value];
    x_values = [point1[0], point2[0]];
    y_values = [point1[1], point2[1]];

    plt.figure(1);

    plt.plot(x_values, y_values, line, label = _label);

    #plt.figure(2);
    #plt.clf();
    #plt.hist(gethistogramdata(), bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);

    
    #last_updated_graph = 0;
    last_values[line] = value;

is_label_added = False;
def draw_graph():
    global is_label_added
    if not tick_count % update_interval == 0:
        return;

    if not is_label_added:
        plt.legend(loc="upper left")
        is_label_added = True;

    plt.draw();

    plt.pause(0.001);


def multiply_actor(_actor):
    new_actor = copy.copy(_actor);
    new_actor.speed = min(10, max(1, new_actor.speed + random.randint(-1, 1)));
    #new_actor.is_carnivore = min(10, max(0, new_actor.is_carnivore + random.randint(-1, 1)));
    if random.randint(0, 10) == 5:
        new_actor.is_carnivore = not new_actor.is_carnivore;

    actors.append(new_actor);

def simulation_step(): # egy "lépés" minden lénynek
    global food, actor, ticks_since_food_spawn, tick_count, actor_positions, food_positions;
    tick_count += 1;

    speed_sum = 0;
    carnivore_sum = 0;
    for _actor in actors:
        for stepcount in range(math.floor(_actor.speed)): # nagyobb sebesség = több mozgás / lépés
            _actor.posX += random.randint(-1, 1);
            _actor.posY += random.randint(-1, 1);

            if not _actor.is_carnivore:
                for _food in foods: # ha rajta áll egy ételen, éhség=0 illetve engedjük osztódni
                    if _actor.posX == _food.posX and _actor.posY == _food.posY:
                        foods.remove(_food);
                        #_actor.hunger -= _actor.hunger * ((10-_actor.is_carnivore)/10);
                        _actor.hunger = 0;
                        multiply_actor(_actor);
            else:
                for _actor2 in actors:
                    if not _actor2.is_carnivore and _actor != _actor2 and _actor.posX == _actor2.posX and _actor.posY == _actor2.posY:
                        actors.remove(_actor2);
                        #_actor.hunger -= _actor.hunger * ((_actor.is_carnivore)/10);
                        _actor.hunger = 0;
                        multiply_actor(_actor);

        if _actor.hunger > ticks_until_starvation: # ha éhség nagyobb mint x, a lény meghal
            actors.remove(_actor);
        _actor.hunger += 1 + (_actor.speed - 1) # + (_actor.is_carnivore - 1)/5; # növeljük az éhséget minden lépésben

        speed_sum += _actor.speed;
        carnivore_sum += _actor.is_carnivore;

    if len(actors) == 0:
        input("Population is 0. Press any key to exit.")
        exit(0)

    plot_graph(speed_sum/len(actors), "g-", "átlagsebesség"); # átlag sebesség rajzolása
    plot_graph(carnivore_sum/len(actors) * 5, "b-", "ragadozók aránya"); # carnivore % rajzolása
    plot_graph(len(actors)/100, "r-", "populáció"); # populáció rajzolása

    draw_graph();

    # étel lerakása véletlen helyre minden x lépés után (x=food_spawn_delay)
    ticks_since_food_spawn += 1;
    if ticks_since_food_spawn > food_spawn_delay:
        posX = random.randint(0, fieldsize-1);
        posY = random.randint(0, fieldsize-1);
        foods.append(food(posX, posY));
        ticks_since_food_spawn = 0;

    # ne hagyjuk lemenni a lényeket a pályáról
    for _actor in actors:
        _actor.posX = max(0, min(_actor.posX, fieldsize-1));
        _actor.posY = max(0, min(_actor.posY, fieldsize-1));


def gethistogramdata():
    data = [];
    
    for _actor in actors:
        data.append(_actor.is_carnivore);
    return data;

def main():
    global timestep;
    pygame.init();

    DISPLAY=pygame.display.set_mode((fieldsize * fieldscale,fieldsize * fieldscale),0,32);

    while True:
        for event in pygame.event.get():
            if event.type==QUIT:
                

                #plt.draw();

                pygame.quit();
                sys.exit();

        # pálya kirajzolása
        DISPLAY.fill(BGCOLOR);

        for _actor in actors:
            pygame.draw.rect(DISPLAY,(255,0,_actor.is_carnivore * 200),(_actor.posX * fieldscale,_actor.posY * fieldscale,fieldscale,fieldscale));
        for _food in foods:
            pygame.draw.rect(DISPLAY,FOODCOLOR,(_food.posX * fieldscale + 1,_food.posY * fieldscale + 1,fieldscale-2,fieldscale-2));
        pygame.display.update();

        # egy szimulációs lépés, majd szünet
        simulation_step();
        time.sleep(timestep);

main();
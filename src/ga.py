import copy
import heapq
import metrics
import multiprocessing.pool as mpool
import os
import random
import shutil
import time
import math

width = 200
height = 16

options = [
    "-",  # an empty space
    "X",  # a solid wall
    "?",  # a question mark block with a coin
    "M",  # a question mark block with a mushroom
    "B",  # a breakable block
    "o",  # a coin
    "|",  # a pipe segment
    "T",  # a pipe top
    "E",  # an enemy
    #"f",  # a flag, do not generate
    #"v",  # a flagpole, do not generate
    #"m"  # mario's start position, do not generate
]

# The level as a grid of tiles


class Individual_Grid(object):
    __slots__ = ["genome", "_fitness"]

    def __init__(self, genome):
        self.genome = copy.deepcopy(genome)
        self._fitness = None

    # Update this individual's estimate of its fitness.
    # This can be expensive so we do it once and then cache the result.
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Print out the possible measurements or look at the implementation of metrics.py for other keys:
        # print(measurements.keys())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Modify this, and possibly add more metrics.  You can replace this with whatever code you like.
        coefficients = dict(
            meaningfulJumpVariance=0.6,
            negativeSpace=0.5,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.5,
            solvability=2.0
        )
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients))
        return self

    # Return the cached fitness value or calculate it as needed.
    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    # Mutate a genome into a new genome.  Note that this is a _genome_, not an individual!
    def mutate(self, genome):
        # STUDENT implement a mutation operator, also consider not mutating this individual
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        new_genome = copy.deepcopy(genome)

        # mutate for each tile: pit, walls, pipe, blocks (coin, breakable, Mushroom), enemies, coins
        left = 10
        right = width - 10

        modifiable = list(range(left, right)) # don't modify the first and last ten tiles
        unmodifiable = modifiable


        for i in range(left, right): # refill pits
            new_genome[height - 1][i] = "X"

        counter = 0 # counter keeps track of position for modifiable's index

        # THIS LOOP GENERATES PITS
        while counter < len(modifiable):
            temp = modifiable[counter]
            if random.random() < temp * .25: # chance to create pit is based on progress
                tileNum = modifiable[counter]
                pitDistance = random.randrange(2, 6) # Pits are anywhere from 2 to 5 tiles long
                if tileNum + pitDistance > modifiable[-1]: # check if length is longer than modifiable
                    pitDistance = counter - modifiable[-1]
                for tiles in range(pitDistance): # Create a pit and remove it from modifiable
                    temp = modifiable.pop(counter)
                    new_genome[height - 1][temp] = "-"
                counter += 5 # at least five spaces to next pit
            else:
                counter += 1

        counter = 0

        """
        # THIS LOOP GENERATES WALLS
        while counter < len(modifiable):
            if random.random() < .25:
                tileNum = modifiable[counter]
                wallDistance = random.randrange(1, 5)
                for currentDistance in range(wallDistance):
                    if new_genome[height - 1][tileNum + currentDistance] != "-": # Check if there's not a pit
                        wallHeight = random.randrange(2, 5)
                        for currentHeight in range(wallHeight):
                            new_genome[height - (1 + currentHeight)][temp] = "X"
                counter += 5 # at least five spaces to next wall
            else:
                counter += 1
        """

        # THIS LOOP GENERATES PIPE HEADS
        for x in range(left, right):
            pipe_head_not_found = True
            for y in range(height):
                if new_genome[y][x] == "T" or new_genome[y][x + 1] == "T": # Check if we're not overlapping pipes
                    pipe_head_found = False
                    break
             
            if pipe_head_not_found == True:
                if random.random() < .25:
                    if random.random () < .5:
                        new_genome[random.randrange(2, 6)][x] = "T"
                    else:
                        new_genome[random.randrange(height - 6, height - 3)][x] = "T"


        # THIS LOOP FIXES PIPES
        for y in range(height):
            for x in range(left, right):
                # build a pipe
                if new_genome[y][x] == "T":
                    # check if there's an existing pipe body
                    if new_genome[y + 1][x] == "|": # if pipe body is below
                        for y2 in range(y + 1, height):
                            new_genome[y2][x] = "|"
                    elif new_genome[y - 1][x] == "|": # if pipe body is above
                        for y2 in range(0, y - 1):
                            new_genome[y2][x] = "|"

                    else:
                        if y > (height / 2):
                            # down pipe
                            for y2 in range(y + 1, height):
                                new_genome[y2][x] = "|"
                        else:
                            # up pipe
                            for y2 in range(0, y):
                                new_genome[y2][x] = "|"
        return new_genome

    # Create zero or more children from self and other
    def generate_children(self, other):
        new_genome = copy.deepcopy(self.genome)
        # Leaving first and last columns alone...
        # do crossover with other
        left = 1          # leftmost column of the level
        right = width - 1 # rightmost column of the level
        dadChance = 0
        dadChance = .58 if self._fitness > other._fitness else .42
        for y in range(height): # for each tile in height
            for x in range(left, right): # for each tile from (left, right)
                # STUDENT Which one should you take?  Self, or other?  Why?
                # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
                # compare fitness of both genomes
                new_genome[y][x] = self.genome[y][x] if random.random() < dadChance else other.genome[y][x]
        # do mutation; note we're returning a one-element tuple here
        new_genome = self.mutate(new_genome)
        return (Individual_Grid(new_genome), )

    # Turn the genome into a level string (easy for this genome)
    def to_level(self):
        return self.genome

    # These both start with every floor tile filled with Xs
    # STUDENT Feel free to change these
    @classmethod
    def empty_individual(cls):
        g = [["-" for col in range(width)] for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        for col in range(8, 14):
            g[col][-1] = "f"
        for col in range(14, 16):
            g[col][-1] = "X"
        return cls(g)

    @classmethod
    def random_individual(cls):
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        g = [random.choices(options, k=width) for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        g[8:14][-1] = ["f"] * 6
        g[14:16][-1] = ["X", "X"]
        return cls(g)


def offset_by_upto(val, variance, min=None, max=None):
    val += random.normalvariate(0, variance**0.5)
    if min is not None and val < min:
        val = min
    if max is not None and val > max:
        val = max
    return int(val)


def clip(lo, val, hi):
    if val < lo:
        return lo
    if val > hi:
        return hi
    return val

# Inspired by https://www.researchgate.net/profile/Philippe_Pasquier/publication/220867545_Towards_a_Generic_Framework_for_Automated_Video_Game_Level_Creation/links/0912f510ac2bed57d1000000.pdf


class Individual_DE(object):
    # Calculating the level isn't cheap either so we cache it too.
    __slots__ = ["genome", "_fitness", "_level"]

    # Genome is a heapq of design elements sorted by X, then type, then other parameters
    def __init__(self, genome):
        self.genome = list(genome)
        heapq.heapify(self.genome)
        self._fitness = None
        self._level = None

    # Calculate and cache fitness
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Add more metrics?
        # STUDENT Improve this with any code you like
        coefficients = dict(
            meaningfulJumpVariance=0.7,
            negativeSpace=0.6,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.2,
            solvability=2.0
        )
        penalties = 0
        # STUDENT For example, too many stairs are unaesthetic.  Let's penalize that
        if len(list(filter(lambda de: de[1] == "6_stairs", self.genome))) > 5:
            penalties -= 2
        # STUDENT If you go for the FI-2POP extra credit, you can put constraint calculation in here too and cache it in a new entry in __slots__.
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients)) + penalties
        return self

    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    def mutate(self, new_genome):
        # STUDENT How does this work?  Explain it in your writeup.
        # STUDENT consider putting more constraints on this, to prevent generating weird things
        if random.random() < 0.1 and len(new_genome) > 0:
            to_change = random.randint(0, len(new_genome) - 1)
            de = new_genome[to_change]
            new_de = de
            x = de[0]
            de_type = de[1]
            choice = random.random()
            if de_type == "4_block":
                y = de[2]
                breakable = de[3]
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    breakable = not de[3]
                new_de = (x, de_type, y, breakable)
            elif de_type == "5_qblock":
                y = de[2]
                has_powerup = de[3]  # boolean
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    has_powerup = not de[3]
                new_de = (x, de_type, y, has_powerup)
            elif de_type == "3_coin":
                y = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                new_de = (x, de_type, y)
            elif de_type == "7_pipe":
                h = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    h = offset_by_upto(h, 2, min=2, max=height - 4)
                new_de = (x, de_type, h)
            elif de_type == "0_hole":
                w = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    w = offset_by_upto(w, 4, min=1, max=width - 2)
                new_de = (x, de_type, w)
            elif de_type == "6_stairs":
                h = de[2]
                dx = de[3]  # -1 or 1
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    h = offset_by_upto(h, 8, min=1, max=height - 4)
                else:
                    dx = -dx
                new_de = (x, de_type, h, dx)
            elif de_type == "1_platform":
                w = de[2]
                y = de[3]
                madeof = de[4]  # from "?", "X", "B"
                if choice < 0.25:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.5:
                    w = offset_by_upto(w, 8, min=1, max=width - 2)
                elif choice < 0.75:
                    y = offset_by_upto(y, height, min=0, max=height - 1)
                else:
                    madeof = random.choice(["?", "X", "B"])
                new_de = (x, de_type, w, y, madeof)
            elif de_type == "2_enemy":
                pass
            new_genome.pop(to_change)
            heapq.heappush(new_genome, new_de)
        elif random.random() < 0.05:
            elt_count = random.randint(1,3)
            g = [random.choice([
                (random.randint(1, width - 2), "0_hole", random.randint(1, 8)),
                (random.randint(1, width - 2), "1_platform", random.randint(1, 8), random.randint(0, height - 1),
                 random.choice(["?", "X", "B"])),
                (random.randint(1, width - 2), "2_enemy"),
                (random.randint(1, width - 2), "3_coin", random.randint(0, height - 1)),
                (random.randint(1, width - 2), "4_block", random.randint(0, height - 1),
                 random.choice([True, False])),
                (random.randint(1, width - 2), "5_qblock", random.randint(0, height - 1),
                 random.choice([True, False])),
                (random.randint(1, width - 2), "6_stairs", random.randint(1, height - 4), random.choice([-1, 1])),
                (random.randint(1, width - 2), "7_pipe", random.randint(2, height - 4))
            ]) for i in range(elt_count)]

            for item in g:
                heapq.heappush(new_genome,item)

        print(new_genome)
        return new_genome

    def generate_children(self, other):
        # STUDENT How does this work?  Explain it in your writeup.
        pa = random.randint(0, len(self.genome) - 1) if len(self.genome) > 0 else 0
        pb = random.randint(0, len(other.genome) - 1) if len(other.genome) > 0 else 0  
        a_part = self.genome[:pa] if len(self.genome) > 0 else []
        b_part = other.genome[pb:] if len(other.genome) > 0 else []
        ga = a_part + b_part
        b_part = other.genome[:pb] if len(other.genome) > 0 else []
        a_part = self.genome[pa:] if len(self.genome) > 0 else []
        gb = b_part + a_part
        # do mutation
        return Individual_DE(self.mutate(ga)), Individual_DE(self.mutate(gb))

    # Apply the DEs to a base level.
    def to_level(self):
        if self._level is None:
            base = Individual_Grid.empty_individual().to_level()
            for de in sorted(self.genome, key=lambda de: (de[1], de[0], de)):
                # de: x, type, ...
                x = de[0]
                de_type = de[1]
                if de_type == "4_block":
                    y = de[2]
                    breakable = de[3]
                    base[y][x] = "B" if breakable else "X"
                elif de_type == "5_qblock":
                    y = de[2]
                    has_powerup = de[3]  # boolean
                    base[y][x] = "M" if has_powerup else "?"
                elif de_type == "3_coin":
                    y = de[2]
                    base[y][x] = "o"
                elif de_type == "7_pipe":
                    h = de[2]
                    base[height - h - 1][x] = "T"
                    for y in range(height - h, height):
                        base[y][x] = "|"
                elif de_type == "0_hole":
                    w = de[2]
                    for x2 in range(w):
                        base[height - 1][clip(1, x + x2, width - 2)] = "-"
                elif de_type == "6_stairs":
                    h = de[2]
                    dx = de[3]  # -1 or 1
                    for x2 in range(1, h + 1):
                        for y in range(x2 if dx == 1 else h - x2):
                            base[clip(0, height - y - 1, height - 1)][clip(1, x + x2, width - 2)] = "X"
                elif de_type == "1_platform":
                    w = de[2]
                    h = de[3]
                    madeof = de[4]  # from "?", "X", "B"
                    for x2 in range(w):
                        base[clip(0, height - h - 1, height - 1)][clip(1, x + x2, width - 2)] = madeof
                elif de_type == "2_enemy":
                    base[height - 2][x] = "E"
            self._level = base
        return self._level

    @classmethod
    def empty_individual(_cls):
        # STUDENT Maybe enhance this
        g = []
        return Individual_DE(g)

    @classmethod
    def random_individual(_cls):
        # STUDENT Maybe enhance this
        elt_count = random.randint(8, 128)
        g = [random.choice([
            (random.randint(1, width - 2), "0_hole", random.randint(1, 8)),
            (random.randint(1, width - 2), "1_platform", random.randint(1, 8), random.randint(0, height - 1), random.choice(["?", "X", "B"])),
            (random.randint(1, width - 2), "2_enemy"),
            (random.randint(1, width - 2), "3_coin", random.randint(0, height - 1)),
            (random.randint(1, width - 2), "4_block", random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "5_qblock", random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "6_stairs", random.randint(1, height - 4), random.choice([-1, 1])),
            (random.randint(1, width - 2), "7_pipe", random.randint(2, height - 4))
        ]) for i in range(elt_count)]
        return Individual_DE(g)


Individual = Individual_Grid


def generate_successors(population):
    # STUDENT Design and implement this
    # Hint: Call ren() on some individuals and fill up results.
    # 5% Elitist, 10% Random - 25% Elite (.025), 75% Roulette (.075)
    results = []            # returned list for genomes selected to carry over to next population
    elitePopulation = []    # list of genomes selected through elitist select; 5% of pop_limit
    roulettePopulation = [] # list of genomes selected through roulette wheel select; 10% of pop_limit, has half of elitePopulation
    pop_limit = len(population)
    sortedPopulation = sorted(population, key=lambda level: level._fitness * -1) # sort on fitness (most to least)
    for num in range(int(.05 * pop_limit)): # 5%, (weirdly) rounded to whole number (see doc)
        temp = sortedPopulation.pop(num)
        elitePopulation.append(temp) # append to elitePopulation while removing from sortedPopulation
        results.append(temp)

    elitePick = random.randrange(0, pop_limit - 1) # pick a random number from 0 to length of elitePopulation

    # if elitePick is even, append odd and vice-versa 
    if elitePick % 2 != 0:
        for item in range(0, len(elitePopulation), 2):
            roulettePopulation.append(elitePopulation[item])
    else:
        for item in range(1, len(elitePopulation), 2):
            roulettePopulation.append(elitePopulation[item])

    # select via roulette to fill roulettePopulation
    fitnessTotal = 0 # get total fitness of population
    for item in sortedPopulation:
        fitnessTotal += abs(item._fitness)

    for num in range(int(.075 * len(sortedPopulation))): # get 7.5% random
        rouletteSelect = random.randrange(0, int(fitnessTotal)) # rouletteSelect is a number between 0 and total fitness
        for item in range(len(sortedPopulation)):
            rouletteSelect -= abs(sortedPopulation[item]._fitness) # keep subtracting from the random roulette select number until it hits 0
            if (rouletteSelect <= 0): # if selected
                fitnessTotal -= sortedPopulation[item]._fitness # remove item from pool and append it
                roulettePopulation.append(sortedPopulation.pop(item))
                break
        if rouletteSelect > 0: # in case the selected number is more than the fitness, append last
            roulettePopulation.append(sortedPopulation.pop())

    for i in range(pop_limit - len(results)):
        child = random.choice(elitePopulation).generate_children(random.choice(roulettePopulation))
        results.append(child[0])

    # print("TESTING: ", len(results), results)
    return results


def ga():
    # STUDENT Feel free to play with this parameter
    pop_limit = 64
    # Code to parallelize some computations
    batches = os.cpu_count()
    if pop_limit % batches != 0:
        print("It's ideal if pop_limit divides evenly into " + str(batches) + " batches.")
    batch_size = int(math.ceil(pop_limit / batches))
    with mpool.Pool(processes=os.cpu_count()) as pool:
        init_time = time.time()
        # STUDENT (Optional) change population initialization
        """ Before
        population = [Individual.random_individual() if random.random() < 0.9
                      else Individual.empty_individual()
                      for _g in range(pop_limit)]"""

        population = [Individual.empty_individual() for _g in range(pop_limit)]

        # But leave this line alone; we have to reassign to population because we get a new population that has more cached stuff in it.
        population = pool.map(Individual.calculate_fitness,
                              population,
                              batch_size)
        init_done = time.time()
        print("Created and calculated initial population statistics in:", init_done - init_time, "seconds")
        generation = 0
        start = time.time()
        now = start
        print("Use ctrl-c to terminate this loop manually.")
        try:
            runs = 0
            # while runs == 0:
            while True:
                now = time.time()
                # Print out statistics
                if generation > 0:
                    best = max(population, key=Individual.fitness)
                    print("Generation:", str(generation))
                    print("Max fitness:", str(best.fitness()))
                    print("Average generation time:", (now - start) / generation)
                    print("Net time:", now - start)
                    with open("levels/last.txt", 'w') as f:
                        for row in best.to_level():
                            f.write("".join(row) + "\n")
                generation += 1
                # STUDENT Determine stopping condition
                stop_condition = False
                if stop_condition:
                    break
                # STUDENT Also consider using FI-2POP as in the Sorenson & Pasquier paper
                gentime = time.time()
                next_population = generate_successors(population)
                gendone = time.time()
                print("Generated successors in:", gendone - gentime, "seconds")
                # Calculate fitness in batches in parallel
                next_population = pool.map(Individual.calculate_fitness,
                                           next_population,
                                           batch_size)
                popdone = time.time()
                print("Calculated fitnesses in:", popdone - gendone, "seconds")
                population = next_population
                # runs += 1
        except KeyboardInterrupt:
            pass
    return population


if __name__ == "__main__":
    final_gen = sorted(ga(), key=Individual.fitness, reverse=True)
    best = final_gen[0]
    print("Best fitness: " + str(best.fitness()))
    now = time.strftime("%m_%d_%H_%M_%S")
     #STUDENT You can change this if you want to blast out the whole generation, or ten random samples, or...
    for k in range(0, 10):
        with open("levels/" + now + "_" + str(k) + ".txt", 'w') as f:
            for row in final_gen[k].to_level():
                f.write("".join(row) + "\n")
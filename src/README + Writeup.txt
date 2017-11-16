***WE WOULD LIKE TO PARTICIPATE IN THE COMETITION***

PARTNERS:
 Jonathan Alcantara
 Jolina Lam


CONTENT
 -Individual_Grid (changes we implemented to the template)
 -Favorite Level
 -Individual_DE (code explanation)
----------------------------------------------------------------------------------

INDIVIUAL_GRID
 Selection Strategies
  We implemented a combination of elitist and roulette selection. In total we chose 15% of the initial population to be parents of the next generation. Five percent of the initial population with the highest fitness would be chosen to be "elite", and the other 10% would be selected based on roulette in order to introduce some diversity, keep a relatively fit next generation without reaching a local maxima.

 Fitness Function
  We gave a higher coefficient to meaningfulJumpVariance and decreased the coefficient for negativeSpace. Our design goal was for the player to do more navigation in the level, so we wanted more obstacles for the player to be able to traverse over.

 Crossover Function
  We used uniform crossover that was weighted toward the parent with a higher fitness (58%, 42%) because we wanted both fit and diverse children, but favored fitness more than diversity. Since there was a chance that the "elitest" population could interbreed based on the way we implemented generate_successors, we decided to give diversity a higher chance of being prevalent in the children.

 Mutation Function
  In mutation, we mutate/generate elements in a certain order such that elements with more restrictions could be generated first and correctly, starting from pits, to pipes, blocks (mushroom, coin, breakable), enemies, and lastly coins.
  ★Pits:
    We created pits in the ground that were guaranteed to be longer than 1 block both for an aesthetically pleasing look and to provide a challenge for the player. After a pit is generated, there is guaranteed to be at least 5 landing tiles (either floor, pipes, or a combination of both) after it so the pit isn't impossible the cross. The pits are generated 10% of the time in the beginning of the level. As the player progresses, the frequency of pit generation increases to scale difficulty.
  ★Pipes:
    To generate pipes, we set restrictions such as requiring all pipes to have tops and be connected to either the ceiling or floor, and preventing other objects from being generated inside the pipes. There is a 5% chance that a pipe will be generated on the floor and the ceiling. Unfortunately, it still has a bug where it will generate an incomplete pipe sometimes.
  ★Blocks:
    Every few block clusters, a mushroom block is spawned for "fairness" (and so that you don't get a line of all mushroom blocks). Blocks are generated in clusters of 2-4. There's a 50% chance that a coin or breakable block is spawned if it is not a mushroom. We made it possible for blocks to stack on top of each other. There is a 50% chance that a block will be deleted if it exists so that future generations don't have too many blocks.
  ★Enemies:
    The frequency of enemies is generated like the pits in that more enemies spawn toward the end of the level. At least one enemy will be generated at every y height as long as there is a standable block under it. There is a 50% chance that an enemy will be deleted if it exists so that future generations aren't cluttered with enemies.
  ★Coins:
    For every empty space that's in a zone that the player could potentially be in, there is a 3% chance a coin will spawn. If there is a coin in the area, there is a 3% chance it will be removed. We made coins spawn at 3% to make them more valuable and to give the players an incentive to collect them (even though they don't have any value in this game).

**Other Notes
  -We changed the height of Mario in the Unity Prefabs to be 0.9 so that he can fit under the blocks when he's small.
  -The level generation pauses sometimes on the computer we develop on and we need to hit a button to make it continue. Not sure if this is a problem on our end with our hardware or software.

----------------------------------------------------------------------------------
FAVORITE LEVEL (Alcantara_Lam.txt)
 We chose this map as our favorite level because we really the sky pipes (it's a sick aesthetic even though it's not practical)! It has the right amount of elements to speed-run it and Jonathan (the Mario level tester pro on team) had a lot of fun with it since it was one of the few levels that he felt put him into the "flow" state. It has the right amount of challenge that scales up as he got closer to the goal (and you can tell that it gets harder as you progress), and there was 1 point where he had to strategize to get over one of the pits because of the layout of the obstacles.

----------------------------------------------------------------------------------
INDIVIDUAL_DE
 Crossover
  Individual_DE uses variable point crossover. It chooses a random index in both the of the parents' arrays to separate the arrays at. Then it generates 2 children by adding the front half of parent1's array with the back half of parent2's array and vice versa.

 Mutation
  The mutation function takes existing elements in the genome and modifies some property of it with a 10% chance. Depending on the element it randomly chooses to mutate, it will change the position, height, width, or block type of the object. The initial code doesn't create or destroy elements, but we modified it so that it has a 5% chance of adding a new item if it didn't modify anything (meaning that it was given an empty map) because we decided to make our initial maps empty.

 Fitness
  We the increased the jumpVariance and decreased the linearity because we wanted to see if it could make the maps look more like a maze.
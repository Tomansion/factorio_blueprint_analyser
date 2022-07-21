# Factorio blueprint bottle-neck analysis tool

![](./doc/images/ban.png)

## What is this tool?

This is a Python script that finds the bottleneck of a Factorio blueprint for you.

It also predicts:
- The entities that are the input or the output of the blueprint
- What item(s) each belts, inserters or any entity are excpected to transport
- The excepted amount of items that will be tranported by each entity
- The excepted usage percentage of each entity

## What is the bottleneck?

A bottleneck is, in a Factorio blueprint, the entity that limits the output of a production line because it is at maximum capacity. It can be a belt, an inserter or a assembly machine.

## In what way is this tool useful?

You can do what you want with the results of this tool, it can help programmers:
- Create blueprints with machine learning
- Create blueprints with genetic algorithms
- Create a dataset of efficient blueprints

You can use this tool to find bottlenecks in your blueprints without having to run ther in the game, or to create a mod that display the results ingame.

## Usage

```bash
# Clone the project
git clone https://github.com/Tomansion/factorio_blueprint_analyser.git
cd factorio_blueprint_analyser

# Start with a simple blueprint:
./blueprint_analyser -f -i examples/beltFac.json
```

This should open a Web browser with the results of the analysis as a node graph.

Given the example:

The result is:

## Output


## Known issues

## Limitations

## Contribution

## Credits

This tool is the result of an internship at the [Michigan State University](https://msu.edu/) and was made in collaboration with the **The factory must grow: automation in Factorio** team. You can find their first paper [here](https://arxiv.org/abs/2102.04871) and their second paper here.

Thanks to [DrKenReid](https://github.com/DrKenReid) and the whole **The factory must grow** team for the amaizing welcoming and for giving me the oportunity to have this wondeful experience!


Factorio blueprint decode and encode code from : https://gist.github.com/click0/46b0ff88361956e430bfcf1e88b5c351

Factorio vanilla data imported from : https://jackhugh.github.io/factorio-data-raw-visualiser/data-raw.json

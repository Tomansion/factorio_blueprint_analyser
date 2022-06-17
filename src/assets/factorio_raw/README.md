# The factorio data for the blueprint bottleneck analysis:

To process the blueprints, I need to have some knowledge about Factorio and each one of those entitys:

- The list of existing entitys
- The recipes
- The data of the entitys:
  - The dimension (size x and y)
  - speed of belts, arms and assembly machines

I don't want to write everything, so I imported all those data from : https://jackhugh.github.io/factorio-data-raw-visualiser/data-raw.json into the factorio_raw.json file.

But the file is to big, so I have filtered into a factorio_raw_min.json file to only include the data I need using the **exctract.py** script.
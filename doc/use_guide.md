# Bottle-neck analysis usage guide

## Command line

```bash
# If you haven't done it, init the project
git clone https://github.com/Tomansion/factorio_blueprint_analyser
cd factorio_blueprint_analyser
pip install -r requirements.txt

# Start the algorithm:
./blueprint_analyser -f -i examples/beltFac.json
```

### Parameters

```diff
./blueprint_analyser -h

+
+    usage: blueprint_analyser [-h] [-i [INPUT]] [-o [OUTPUT]] [-f]
+
+    Find the bottleneck in a Factorio blueprint
+
+    optional arguments:
+      -h, --help                     show this help message and exit
+      -i [INPUT], --input [INPUT]    Blueprint JSON or encoded file path
+      -o [OUTPUT], --output [OUTPUT] JSON File output for the analysed blueprint
+      -f, --force                    Force overwrite of existing result file
+

```

The default input is `examples/beltFac.json`

The default output is `analysed_blueprint.json`

### Options

If you need to tweak the algorithm, you can change the options in the `config/config_default.yaml` file.

```yaml
factorio:
  # Inserter_capacity_bonus
  # number between 0 and 7
  # (https://wiki.factorio.com/Inserter_capacity_bonus_(research))
  inserter_capacity_bonus: 0

  # The facorio data generated from the game files
  # This default data corresponds to the vanilla game
  # To set your own data, you can follow our mod guide
  # (Comming soon)
  data_file_path: "src/assets/factorio_raw/factorio_raw_min.json"

network:
  # The alogrithm will displat the
  # results on a web page in a node network
  # You can disable this feature by setting this to false
  display: true

# Verbose level
# 1: only errors
# 2: errors and warnings
# 3: errors, warnings and info
verbose_level: 3
```

## Imported as a module

Comming soon!

## Pip

Comming soon!
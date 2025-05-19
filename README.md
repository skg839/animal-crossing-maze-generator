# Animal Crossing: New Horizons Maze Generator

This Python project automatically generates a full maze-based map layout for **Animal Crossing: New Horizons**. It outputs `.nhl` acre files that can be imported into your save using NHSE (https://github.com/kwsch/NHSE).

![maze](https://github.com/user-attachments/assets/0c8228e6-a49d-4af1-af2b-6ef37ae9ce3e)

# Features

- Procedural maze generation
- Converts maze to image tiles
- Translates tiles into `.nhl` acre files
- Each `.nhl` file corresponds to an editable acre

# Prerequisites

- Python 3.x
- Required libraries:
  - `Pillow`
  - `OpenCV`
  - `NumPy`
  - `cairosvg`

You can install the dependencies with:

```bash
pip install -r requirements.txt
```

# How to Use

1) Run the maze generator:

```bash
python main.py
```
2) Navigate to the nhl folder to find your generated acre files.


# Importing into NHSE

1) Open NHSE.
2) Import your main.bat save file.
3) Go to Map > Edit Map > Edit Field Items.
4) Enable Snap to nearest Acre on click.
5) Click on any acre to see its name.
6) Navigate to that acre and click Remove Items > All.
7) Click Dump/Import > Import Acre.
8) Locate the matching .nhl file (e.g. C4-1.nhl) and import it.
9) Repeat for each acre as needed.

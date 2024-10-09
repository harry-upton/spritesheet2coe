# Spritesheet to .coe file converter

A simple python script for converting a spritesheet (in bitmap form) into .coe files for initialising FPGA memory blocks in the Vivado tools.

## Usecase

This script works for both single sprites and on spritesheets. It works for palletised bitmap images, exporting a colour palette file, as well as RGB bitmap images.

## Output format

For spritesheets, the sprites will be stored sequentially in memory, from left to right and top to bottom in the spritesheet. Pixels in the sprites are stored left to right, top to bottom.

## Instructions for use

The python script should be used by passing in arguments in the command line. For help you can run:

```python
python spritesheet2coe.py -h
```

## The Bitmap file format

A bit of a tutorial on how bitmap files are structured and what makes them so easy to read.

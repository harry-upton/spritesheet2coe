# Spritesheet to .coe file converter

A simple python script for converting a spritesheet (in bitmap form) into .coe files for initialising FPGA memory blocks in the Vivado tools. This script does not require you to install any extra modules. Feel free to contact me if there are any issues.

## Usecase

This script works for both single sprites and on spritesheets. It works for palletised bitmap images, exporting a colour palette file, as well as RGB bitmap images.

## Output format

For spritesheets, the sprites will be stored sequentially in memory, from left to right and top to bottom in the spritesheet. Pixels in the sprites are stored left to right, top to bottom.

## Instructions for use

The python script should be used by passing in arguments in the command line. For help you can run:

```sh
python spritesheet2coe.py -h
```

## The Bitmap file format

A bit of a tutorial on how bitmap files are structured and what makes them so easy to read.

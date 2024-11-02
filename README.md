# Spritesheet to .coe file converter

A simple python script for converting a spritesheet (in bitmap form) into .coe files for initialising FPGA memory blocks in the Vivado tools. This script does not require you to install any extra modules. Feel free to contact me if there are any issues.

## Usecase

This script works for both single sprites and on spritesheets. It works for palletised bitmap images, exporting a colour palette file, as well as RGB bitmap images. Palletised images have the benefit of taking up less space at the cost of a slightly more complicated decoding process.

If an RGB bitmap file is supplied, the output .coe file will be in an RGB format containing a series of 12/24-bit numbers corresponding to the colour of each pixel.

If a palletised bitmap file is supplied, the output .coe file will contain a series of numbers corresponding to the index of that pixel in the colour palette. The colour palette is outputted in a separate file, either as another .coe file or a Verilog script file containing a switch-case statement.

Using a program like GIMP you can specify which kind of bitmap you are exporting.

## Output format

### Byte Order

For spritesheets, the sprites will be stored sequentially in memory, from left to right and top to bottom in the spritesheet. Pixels in the sprites are stored left to right, top to bottom. For example, say you have a 32x32 spritesheet containing 16x16 sprites, meaning you essentially have a 2x2 grid of sprites. Looking at this image, the top-left sprite is sprite 1, the top-right sprite 2, bottom-left is sprite 3 and bottom-right is sprite 4 - this is the order they will appear in the output, the first 256 values correspond to sprite 1, the next 256 are sprite 2, etc. Within those 256 numbers, the first value is the colour of the top-left pixel in that sprite, the next is the 2nd pixel in the top row, and so forth from left to right and top to bottom.

### Colour Depth

By default in the bitmap file (at least the kinds that this script supports), each R,G, and B component of a pixel has 8-bits (so 24-bits of colour depth per pixel). By using the _-c_ or _--colour_depth_ flag you can specify the colour depth to be 24 bits or 12 bits (12 is the default). A colour depth of 12 means each of the R, G and B values are divided by 16 to reduce them to only 4 bits.

## Instructions for use

The python script should be used by passing in arguments in the command line. For help you can run:

```sh
python spritesheet2coe.py -h
```

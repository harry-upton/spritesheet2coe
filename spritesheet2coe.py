import struct
import argparse
import math

def main(args):
    bmp = open(args.input, 'rb')
    # Read the first 14 bytes - header
    file_type = bmp.read(2).decode()
    file_size = struct.unpack('I', bmp.read(4))
    bmp.read(4) # Read 4 reserved bytes
    offset = struct.unpack('I', bmp.read(4))

    if file_type != "BM":
        raise TypeError("Incorrect file format (header filetype not BM)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('input',
                    help='Input bitmap file path')
    parser.add_argument('sprite_size',
                    help='Sprite width/height in pixels. e.g. sprite_size=16 means 16x16 sprites')
    parser.add_argument('output_image',
                    help='Output image .coe file path')
    parser.add_argument('-m', '--mode', type=int,
                    help='Set the mode: 0=spritesheet (default), 1=single sprite',
                    choices=[0, 1])
    # parser.add_argument('-t', '--type', type=int,
    #                 help='Set the type of bitmap file: 0=RGB (default), 1=palletised',
    #                 choices=[0, 1])
    parser.add_argument('-c', '--colour_depth', type=int,
                    help='Set the OUTPUT colour depth in bits: 12=4 bits for each of the R,G,B components (default), 24=8 bits for each of the R,G,B components',
                    choices=[12, 24])
    parser.add_argument('-p', '--palette_coe',
                    help='Output colour palette .coe file path')
    parser.add_argument('-s', '--palette_switch',
                    help='Output colour palette verilog switch-case statement file path')
    parser.add_argument('-v', '--verbose',
                    help='Enable verbose mode - output full debug info',
                    action='store_true')

    args = parser.parse_args()
    main(args)

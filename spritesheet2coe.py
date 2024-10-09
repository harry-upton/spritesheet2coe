import struct
import argparse
import math

def main(args):
    # Open File
    bmp = open(args.input, 'rb')

    # Read the first 14 bytes - header
    file_type = bmp.read(2).decode()
    file_size = struct.unpack('I', bmp.read(4))
    bmp.read(4) # Read 4 reserved bytes
    offset = struct.unpack('I', bmp.read(4))[0]

    if file_type != "BM":
        raise TypeError("Incorrect file format (header filetype not BM)")
    
    # Read the next 40 bytes - info header
    dib_header_size = struct.unpack('I', bmp.read(4))[0] # actual size of info header
    image_width = struct.unpack('I', bmp.read(4))[0]
    image_height = struct.unpack('I', bmp.read(4))[0]
    colour_planes = struct.unpack('H', bmp.read(2))[0]
    bits_per_pixel = struct.unpack('H', bmp.read(2))[0]
    compression = struct.unpack('I', bmp.read(4))[0]
    image_size = struct.unpack('I', bmp.read(4))[0]
    h_resolution = struct.unpack('I', bmp.read(4))[0]
    v_resolution = struct.unpack('I', bmp.read(4))[0]
    actual_colours = struct.unpack('I', bmp.read(4))[0]
    important_colours = struct.unpack('I', bmp.read(4))[0]

    # Verify program arguments and Bitmap Info Header are valid
    if image_width < int(args.sprite_size) or image_height < (args.sprite_size):
        raise Exception(f"Specified sprite size is smaller than image width/height ({image_width}x{image_height}).")
    
    sprite_size = int(args.sprite_size)
    sprites_x = math.floor(image_width / sprite_size)
    sprites_y = math.floor(image_height / sprite_size)

    if args.verbose:
        print(f"Spritesheet dimensions: {sprites_x} sprites by {sprites_y} sprites. ({sprites_x}x{sprites_y})")
    
    # Check image type, print if verbosity enabled
    num_colours = 0
    if bits_per_pixel == 4:
        num_colours = 16
        if args.verbose:
            print("Bits per pixel = 4, image is palletised with a 16 colour palette.")
    elif bits_per_pixel == 8:
        num_colours = 256
        if args.verbose:
            print("Bits per pixel = 8, image is palletised with a 256 colour palette.")
    elif bits_per_pixel == 24:
        if args.verbose:
            print("Bits per pixel = 24, image is RGB with 24 (or 8 R,G and B) bits per pixel")
    else:
        raise Exception(f"Unsupported number of bits per pixel ({bits_per_pixel}) (not a 24-bit RGB or 4/8-bit palletised bitmap)")
    
    # Warn if palletised image and no palette output
    if (bits_per_pixel == 4 or bits_per_pixel == 8) and (args.palette_coe == None and args.palette_switch == None):
        print(f"Warning: Image is palletised but no output file for the palette has been specified. Use the -p or -s flags.")

    # Check image is not compressed
    if compression != 0:
        raise Exception('Image must be uncompressed (compression = 0)')
    
    # Open palette .coe file
    palette_coe_file = None
    if args.palette_coe != None:
        palette_coe_file = open(args.palette_coe, 'w')
        palette_coe_file.write("memory_initialization_radix=16;\nmemory_initialization_vector=")

    # Open palette verilog switch-case file
    palette_switch_file = None
    if args.palette_switch != None:
        palette_switch_file = open(args.palette_switch, 'w')
        palette_switch_file.write("testheader\n")

    # Load Colour Table (if applicable)
    if num_colours == 16 or num_colours == 256:
        bmp.seek(dib_header_size + 14) # Start of colour table is file header size + info header size
        for i in range(num_colours):
            blue = struct.unpack('B', bmp.read(1))[0] # B,G,R,unused
            green = struct.unpack('B', bmp.read(1))[0]
            red = struct.unpack('B', bmp.read(1))[0]
            unused = struct.unpack('B', bmp.read(1))[0]
            
            if args.colour_depth == 12:
                # Make RGB values 4 bit
                blue = int(blue / 16)
                green = int(green / 16)
                red = int(red/16)
            
            # Print to terminal if verbose
            if args.verbose:
                print("%s \n %s \n %s \n %s" % (hex(blue), hex(green), hex(red), hex(unused)))
            
            # Write palette to files
            if palette_coe_file != None:
                palette_coe_file.write(format(red,'x'))
                palette_coe_file.write(format(green,'x'))
                palette_coe_file.write(format(blue,'x'))
                palette_coe_file.write(" ")

            if palette_switch_file != None:
                palette_switch_file.write("testline\n")

    # Close palette files
    if palette_coe_file != None:
        palette_coe_file.close()

    if palette_switch_file != None:
        palette_switch_file.close()

    # Load pixel data
    bmp.seek(offset)

    # Write to .coe file(s)


        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # --- Positional Args ---
    parser.add_argument('input',
                    help='Input bitmap file path')
    parser.add_argument('sprite_size', type=int,
                        help='Sprite width/height in pixels. e.g. sprite_size=16 means 16x16 sprites')
    parser.add_argument('output_image',
                    help='Output image .coe file path')
    
    # --- Optional Args ---
    # parser.add_argument('-m', '--mode', type=int,
    #                 help='Set the mode: 0=spritesheet (default), 1=single sprite',
    #                 choices=[0, 1])
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

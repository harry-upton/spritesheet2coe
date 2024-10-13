import struct
import argparse
import math

def hex_to_int(hex_input):
    return int(hex_input, 16)

def main(args):
    # Commandline optional args default values
    if args.colour_depth == None:
        args.colour_depth = 12
    if args.transparency_colour == None:
        args.transparency_colour = 0xFF00FF # Magenta is default
    
    if args.transparency_colour > 0xFFFFFF or args.transparency_colour < 0x000000:
        raise Exception("Invalid transparency colour value")

    # Separate transparency into 3 component
    transparency_r = (args.transparency_colour >> 16) & 0x0000ff
    transparency_g = (args.transparency_colour >> 8) & 0x0000ff
    transparency_b = (args.transparency_colour) & 0x0000ff

    # Make transparency colour 4 bit if necessary:
    if args.colour_depth == 12:
        transparency_r = int(transparency_r/16)
        transparency_g = int(transparency_g/16)
        transparency_b = int(transparency_b/16)

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

    # Some extra debug info
    if args.verbose:
        print(f"Spritesheet dimensions: {image_width}x{image_height}")
        print(f"Actual colours: {actual_colours}")
        print(f"Start of colour table: byte {dib_header_size + 14}")
        print(f"Start of pixel data: byte {offset}")

    # Open palette .coe file
    palette_coe_file = None
    if args.palette_coe != None:
        palette_coe_file = open(args.palette_coe, 'w')
        palette_coe_file.write("memory_initialization_radix=16;\nmemory_initialization_vector=")

    # Open palette verilog switch-case file
    palette_switch_file = None
    if args.palette_switch != None:
        palette_switch_file = open(args.palette_switch, 'w')

    # Load Colour Table (if applicable)
    if num_colours == 16 or num_colours == 256:
        bmp.seek(dib_header_size + 14) # Start of colour table is file header size + info header size
        for i in range(actual_colours):
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
                bits_per_component = int(args.colour_depth/3)
                palette_switch_file.write(f"{bits_per_pixel}'d{i}: begin\n")
                palette_switch_file.write(f"\tpalette_r={bits_per_component}'d{(red)}\n")
                palette_switch_file.write(f"\tpalette_g={bits_per_component}'d{(green)}\n")
                palette_switch_file.write(f"\tpalette_b={bits_per_component}'d{(blue)}\n")
                palette_switch_file.write("end\n")

    # Add final colours, close palette files
    remaining_colours = num_colours - actual_colours
    if palette_coe_file != None:
        for i in range(remaining_colours):
            palette_coe_file.write(format(transparency_r,'x'))
            palette_coe_file.write(format(transparency_g,'x'))
            palette_coe_file.write(format(transparency_b,'x'))
            palette_coe_file.write(" ")
        palette_coe_file.close()

    if palette_switch_file != None:
        bits_per_component = int(args.colour_depth/3)
        palette_switch_file.write("default: begin\n")
        palette_switch_file.write(f"\tpalette_r={bits_per_component}'d{(transparency_r)}\n")
        palette_switch_file.write(f"\tpalette_g={bits_per_component}'d{(transparency_g)}\n")
        palette_switch_file.write(f"\tpalette_b={bits_per_component}'d{(transparency_b)}\n")
        palette_switch_file.write("end\n")
        palette_switch_file.close()

    # Load the entire image into an array, removing padding
    bmp.seek(offset)
    image_bytes = []
    if bits_per_pixel == 8:
        # Calculate linelength and padding bytes
        scanline_length = image_width # Num pixels in line * 1 byte per pixel
        line_padding = 4 - (scanline_length % 4)
        if line_padding == 4:
            line_padding = 0

        # Read bitmap data
        for y in range(image_height):
            for x in range(image_width):
                pixel = struct.unpack('B', bmp.read(1))[0] # Read 1 byte
                image_bytes.append(pixel)

                if args.verbose:
                    print(f"{pixel:02x}")

            if args.verbose:
                print(f"newline, padding={line_padding}")
            if line_padding != 0:
                bmp.read(line_padding)

    elif bits_per_pixel == 24:
        # Calculate linelength and padding bytes
        scanline_length = image_width * 3 # Num pixels in line * 3 bytes per pixel
        line_padding = 4 - (scanline_length % 4)
        if line_padding == 4:
            line_padding = 0

        # Read bitmap data
        for y in range(image_height):
            for x in range(image_width):
                pixel = struct.unpack('B', bmp.read(3))[0] # Read 3 bytes
                image_bytes.append(pixel)

                if args.verbose:
                    print(f"{pixel:02x}")

            if args.verbose:
                print(f"newline, padding={line_padding}")
            if line_padding != 0:
                bmp.read(line_padding)

    elif bits_per_pixel == 4:
        # Calculate linelength and padding bytes
        scanline_length = math.ceil(image_width / 2)
        line_padding = 4 - (scanline_length % 4)
        if line_padding == 4:
            line_padding = 0

        # Read bitmap data
        for y in range(image_height):
            for x in range(scanline_length):
                two_pixels = struct.unpack('B', bmp.read(1))[0] # Read 1 byte

                if args.verbose:
                    print(f"{two_pixels:02x}")

                high, low = two_pixels >> 4, two_pixels & 0x0F # Split into 2 nibbles
                image_bytes.append(high)
                if (x == scanline_length - 1) and (math.floor(image_width/2) != scanline_length):
                    pass # This is the last byte on the line AND there is an odd number of bytes per line
                else:
                    image_bytes.append(low)
            
            if args.verbose:
                print(f"newline, padding={line_padding}")
            if line_padding != 0:
                bmp.read(line_padding)
    else:
        raise Exception("Tried to read bitmap with invalid bits_per_pixel number - not implemented!")
    

    # Write to .coe file(s), sprite by sprite
    num_pixels = len(image_bytes)
    row_width = sprites_x * sprite_size
    top_left_corner = num_pixels - row_width

    if args.verbose:
        print(f"Writing coe file: num_pixels={num_pixels}; row_width={row_width}; top_left_corner={top_left_corner}")

    sprites = open(args.output_image, 'w')
    sprites.write("memory_initialization_radix=16;\nmemory_initialization_vector=")
    for sprite_y in range(sprites_y):
        for sprite_x in range(sprites_x):
            top_left_pixel = top_left_corner - row_width * sprite_size * sprite_y + sprite_size * sprite_x
            if args.verbose:
                print(f"Writing sprite starting at: {top_left_pixel}")

            for pix_y in range(sprite_size):
                for pix_x in range(sprite_size):
                    pixel = top_left_pixel + pix_x - pix_y * row_width
                    sprites.write(format(image_bytes[pixel],'x'))
                    sprites.write(" ")

    sprites.close()

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
    parser.add_argument('-t', '--transparency_colour', type=hex_to_int,
                    help='Set the colour used as transparency in sprites.  Default is magenta (0xFF00FF). Input the value as a 6 digit hex. This value will fill any unused colours in the colour palette if one is being used.')
    
    args = parser.parse_args()
    main(args)
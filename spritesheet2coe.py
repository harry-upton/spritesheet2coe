def main():
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('input',
                    help='Input bitmap file path')
    parser.add_argument('output_image',
                    help='Output image .coe file path')
    parser.add_argument('output_palette',
                    help='Output colour palette .coe file path')
    parser.add_argument('sprite_size',
                    help='Sprite width/height in pixels. e.g. sprite_size=16 means 16x16 sprites')
    parser.add_argument('-m', '--mode', type=int,
                    help='Set the mode: 0=spritesheet (default), 1=single sprite',
                    choices=[0, 1])

    args = parser.parse_args()
    main(args)
    
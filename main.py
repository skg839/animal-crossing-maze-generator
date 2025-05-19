import os
import cv2
import cairosvg
import numpy as np
import shutil
from PIL import Image
from maze import Maze

# Define directories to be cleared
directories_to_clear = ['nhl/', 'tmp/']

for directory in directories_to_clear:
    if os.path.exists(directory):
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    else:
        print(f"Directory does not exist: {directory}")

# Maze parameters and creation
maze_width, maze_height = 40, 40
maze = Maze(maze_width, maze_height)
maze.make_maze()
maze.write_svg('tmp/maze.svg')
cairosvg.svg2png(url='tmp/maze.svg', write_to='tmp/maze.png')

# Add white background to transparent pixels
maze_image = cv2.imread('tmp/maze.png', cv2.IMREAD_UNCHANGED)
alpha_channel = maze_image[:, :, 3]
white_background = np.ones_like(maze_image) * 255
maze_image = np.where(alpha_channel[:, :, None] == 0, white_background, maze_image).astype(np.uint8)
cv2.imwrite('tmp/maze_white_bg.png', maze_image)

# Resize image
image = Image.open('tmp/maze_white_bg.png')
image = image.resize((160, 160), Image.Resampling.NEAREST)
image.save('tmp/maze_resized.png')

# Apply border mask
resized_image = Image.open('tmp/maze_resized.png')
border_mask = Image.open('border/border.png')
resized_image.paste(border_mask, (0, 0), border_mask)
resized_image.save('tmp/maze_masked.png')

# Convert to RGB grid
rgb_image = Image.open('tmp/maze_masked.png')
rgb_pixels = [pixel[:3] for pixel in list(rgb_image.getdata())]

width, height = rgb_image.size
pixel_grid = [rgb_pixels[i * width:(i + 1) * width] for i in range(height)]

# Overlay 2x2 color pattern for black pixels
for y in range(height - 1):
    for x in range(width - 1):
        if pixel_grid[y][x] == (0, 0, 0):
            pixel_grid[y][x] = (0, 0, 0)
            pixel_grid[y][x + 1] = (0, 0, 255)
            pixel_grid[y + 1][x] = (255, 0, 0)
            pixel_grid[y + 1][x + 1] = (0, 128, 0)

# Save updated image
rgb_array = np.array(pixel_grid, dtype=np.uint8)
Image.fromarray(rgb_array).save('tmp/rgb_maze.png')

# Crop image
cropped = Image.open('tmp/rgb_maze.png').crop((0, 31, 160, 160))
cropped.save('tmp/map.png')

# Shift image 1px left
shift_matrix = np.float32([[1, 0, -1], [0, 1, 0]])
shifted_img = cv2.warpAffine(cv2.imread('tmp/map.png'), shift_matrix, (160, 129))
cv2.imwrite('tmp/map_shifted.png', shifted_img)

# Remove right border
base = Image.open('tmp/map_shifted.png')
border2 = Image.open('border/border2.png')
base.paste(border2, (159, 0), border2)
base.save('tmp/map_cleaned.png')

# Split into tiles
img = cv2.imread('tmp/map_cleaned.png')
tile_count = 0
for y in range(0, img.shape[0], 32):
    for x in range(0, img.shape[1], 32):
        tile = img[y:y+32, x:x+32]
        cv2.imwrite(f"tmp/{tile_count}.png", tile)
        tile_count += 1

# Rename tiles in specific order
hex_order = ['0', '1', '10', '11', '12', '13', '14', '15', '16', '17',
             '18', '19', '2', '3', '4', '5', '6', '7', '8', '9']
tile_names = ['B1-1', 'B2-1', 'B3-1', 'B4-1', 'B5-1',
              'C1-1', 'C2-1', 'C3-1', 'C4-1', 'C5-1',
              'D1-1', 'D2-1', 'D3-1', 'D4-1', 'D5-1',
              'E1-1', 'E2-1', 'E3-1', 'E4-1', 'E5-1']

for i, index in enumerate(sorted(map(int, hex_order))):
    os.rename(f"tmp/{index}.png", f"tmp/{tile_names[i]}.png")

# Write 24KB .nhl files
for names in tile_names:
    with open(f"nhl/{names}.nhl", 'wb') as f:
        remove = ['FE FF 00 00 00 00 00 00'] * 1024  # ensure exactly 1024 entries (one per pixel)

        im = Image.open(f"tmp/{names}.png", 'r')
        print(names)
        pix_val = list(im.getdata())

        if len(pix_val) != 1024:
            print(f"Warning: {names} has {len(pix_val)} pixels instead of 1024")

        for i in range(min(len(pix_val), 1024)):
            if pix_val[i] == (0, 0, 0):
                remove[i] = '08 ED 00 00 01 00 00 00'
            elif pix_val[i] == (0, 0, 255):
                remove[i] = 'FD FF 00 00 08 ED 01 00'
            elif pix_val[i] == (255, 0, 0):
                remove[i] = 'FD FF 00 00 08 ED 00 01'
            elif pix_val[i] == (0, 128, 0):
                remove[i] = 'FD FF 00 00 08 ED 01 01'

        for entry in remove:
            f.write(bytes.fromhex(entry))

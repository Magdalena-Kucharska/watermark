from math import floor, sqrt

import numpy as np
from PIL import Image
from scipy.fftpack import dct

Q = 60
watermarked_image = np.array(Image.open("watermarked.png"))
watermarked_image_blocks = []
for row in range(0, watermarked_image.shape[0], 8):
    for col in range(0, watermarked_image.shape[1], 8):
        watermarked_image_blocks.append(np.array(watermarked_image[row:row +
                                                                       8,
                                                 col:col + 8]))

blocks_8x8 = sum([1 for block
                  in watermarked_image_blocks
                  if block.shape[0] == 8 and block.shape[1] == 8])
max_watermark_size = floor(sqrt(blocks_8x8))
watermark = np.zeros((max_watermark_size, max_watermark_size), dtype="uint8")
for i in range(len(watermarked_image_blocks)):
    watermarked_image_blocks[i] = dct(dct(dct(watermarked_image_blocks[i],
                                              norm="ortho", axis=0), axis=1,
                                          norm="ortho"), axis=2, norm="ortho")

i = 0
for row in range(watermark.shape[0]):
    for col in range(watermark.shape[1]):
        if any((watermarked_image_blocks[i][0][0] % Q) >= (Q / 2)):
            watermark[row][col] = 255

Image.fromarray(watermark).show()

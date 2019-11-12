from math import floor, sqrt

import numpy as np
from PIL import Image
from scipy.fftpack import dct, idct

# F:\Magda\Downloads\WJET_2015102313563208.pdf
Q = 60
image = np.array(Image.open("wp.png").convert("RGB"))
image_blocks = []
for row in range(0, image.shape[0], 8):
    for col in range(0, image.shape[1], 8):
        image_blocks.append(np.array(image[row:row + 8, col:col + 8]))
blocks_8x8 = sum([1 for block
                  in image_blocks
                  if block.shape[0] == 8 and block.shape[1] == 8])
max_watermark_size = floor(sqrt(blocks_8x8))
watermark = np.array(
    Image.open("watermark3.png").resize((max_watermark_size, max_watermark_size
                                         )).convert("1"), dtype="uint8")

for i in range(len(image_blocks)):
    image_blocks[i] = dct(dct(dct(image_blocks[i], axis=0, norm="ortho"),
                              axis=1, norm="ortho"), axis=2, norm="ortho")
    # image_blocks[i] = dctn(image_blocks[i], norm="ortho")

i = 0
for col in range(watermark.shape[0]):
    for row in range(watermark.shape[1]):
        if watermark[col][row] == 0:
            image_blocks[i][0][0] += Q / 2 - ((
                                                      image_blocks[i][0][
                                                          0] -
                                                      0.75 * Q) % Q)
        else:
            image_blocks[i][0][0] += + Q / 2 - ((
                                                        image_blocks[i][0][
                                                            0] +
                                                        0.75 * Q) % Q)

for i in range(len(image_blocks)):
    image_blocks[i] = idct(idct(idct(image_blocks[i], axis=0, norm="ortho"),
                                axis=1, norm="ortho"), axis=2, norm="ortho")
    # image_blocks[i] = idctn(image_blocks[i], norm="ortho")

i = 0
watermarked_image = np.zeros(image.shape)
for row in range(0, watermarked_image.shape[0], 8):
    for col in range(0, watermarked_image.shape[1], 8):
        watermarked_image[row:row + 8, col:col + 8] = image_blocks[i]
        i += 1

Image.fromarray(np.uint8(watermarked_image)).save("watermarked.png")

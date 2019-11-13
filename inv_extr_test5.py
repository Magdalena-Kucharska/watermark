from math import floor, sqrt

import cv2
import numpy as np
import skimage
from PIL import Image

Q = 60
watermarked_image = np.array(Image.open("watermarked.jpg"))
rows, cols = watermarked_image.shape[0], watermarked_image.shape[1]
while rows % 8 != 0:
    rows += 1
while cols % 8 != 0:
    cols += 1
watermarked_image_padded = np.zeros((rows, cols, 3), dtype="float32")
watermarked_image_padded[:watermarked_image.shape[0],
:watermarked_image.shape[1]] = watermarked_image
watermarked_image_blocks = skimage.util.view_as_blocks(
    watermarked_image_padded, (8, 8,
                               3))
max_watermark_size = floor(
    sqrt(watermarked_image.shape[0] * watermarked_image.shape[1]
         / 64))
watermark = np.array(
    Image.open("watermark3.png").resize((max_watermark_size, max_watermark_size
                                         )).convert("1"), dtype="uint8")
for i in range(watermarked_image_blocks.shape[0]):
    for j in range(watermarked_image_blocks.shape[1]):
        # image_blocks[i][j] = dct(dct(dct(image_blocks[i][j], axis=0,
        #                                  norm="ortho"),
        #                       axis=1, norm="ortho"), axis=2, norm="ortho")
        # watermarked_image_blocks[i][j][0] = dctn(watermarked_image_blocks[
        # i][j][0],
        #                                          norm="ortho")
        for k in range(3):
            watermarked_image_blocks[i][j][0][:, :, k] = cv2.dct(
                watermarked_image_blocks[i][j][0][
                :, :, k])
k, l = 0, 0
for row in range(watermark.shape[0]):
    for col in range(watermark.shape[1]):
        if (watermarked_image_blocks[k][l][0][0][0][0] % Q) >= (Q / 2):
            watermark[row][col] = 255
        if l == watermarked_image_blocks.shape[1] - 1:
            k += 1
            l = 0
        else:
            l += 1

Image.fromarray(watermark).show()

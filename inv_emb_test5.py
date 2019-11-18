from math import floor, sqrt

import cv2
import numpy as np
import skimage
from PIL import Image

# F:\Magda\Downloads\WJET_2015102313563208.pdf
Q = 60
image = np.array(Image.open("photo1.jpg").convert("RGB"))
rows, cols = image.shape[0], image.shape[1]
while rows % 8 != 0:
    rows += 1
while cols % 8 != 0:
    cols += 1
image_padded = np.zeros((rows, cols, 3), dtype="float32")
image_padded[:image.shape[0], :image.shape[1]] = image
image_blocks = skimage.util.view_as_blocks(image_padded, (8, 8, 3))
max_watermark_size = floor(sqrt(image.shape[0] * image.shape[1] / 64))
watermark = np.array(
    Image.open("watermark3.png").resize((max_watermark_size, max_watermark_size
                                         )).convert("1"), dtype="uint8")

for i in range(image_blocks.shape[0]):
    for j in range(image_blocks.shape[1]):
        for k in range(3):
            image_blocks[i][j][0][:, :, k] = cv2.dct(image_blocks[i][j][0][
                                                     :, :, k])

k, l = 0, 0
for row in range(watermark.shape[0]):
    for col in range(watermark.shape[1]):
        if watermark[row][col] == 0:
            image_blocks[k][l][0][0][0][2] += Q / 2 - ((
                                                               image_blocks[k][
                                                                   l][0][
                                                                   0][0][2] -
                                                               0.75 * Q) % Q)
        else:
            image_blocks[k][l][0][0][0][2] += Q / 2 - ((
                                                               image_blocks[k][
                                                                   l][0][
                                                                   0][0][2] +
                                                               0.75 * Q) % Q)
        if l == image_blocks.shape[1] - 1:
            k += 1
            l = 0
        else:
            l += 1

for row in range(image_blocks.shape[0]):
    for col in range(image_blocks.shape[1]):
        for k in range(3):
            image_blocks[row][col][0][:, :, k] = cv2.idct(image_blocks[row][
                                                              col][0][
                                                          :, :, k])

image_blocks = np.round(image_blocks, 0)
image_blocks = image_blocks.transpose((0, 3, 2, 1, 4, 5))
image_blocks = image_blocks.reshape((rows, cols, 3))
watermarked_image = image_blocks[:image.shape[0], :image.shape[1]]

Image.fromarray(np.uint8(watermarked_image)).save("watermarked.jpg")

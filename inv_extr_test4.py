from math import floor, sqrt

import numpy as np
import pywt
import skimage
from PIL import Image
from cv2 import dct

# from scipy.fftpack import dct

watermarked_image = np.array(Image.open("watermarked.jpg"))
b = watermarked_image[:, :, 0]
g = watermarked_image[:, :, 1]
r = watermarked_image[:, :, 2]

LL, (LH, HL, HH) = pywt.dwt2(b, wavelet="haar")
rows, cols = HH.shape[0], HH.shape[1]
while rows % 8 != 0:
    rows += 1
while cols % 8 != 0:
    cols += 1
HH_padded = np.zeros((rows, cols), dtype="float32")
HH_padded[:HH.shape[0], :HH.shape[1]] = HH
HH_blocks = skimage.util.view_as_blocks(HH_padded, (8, 8))

max_watermark_size = floor(sqrt(HH.shape[0] * HH.shape[1] / 64))
watermark = np.zeros((max_watermark_size, max_watermark_size), dtype="uint8")

for row in range(watermark.shape[0]):
    for col in range(watermark.shape[1]):
        dct(HH_blocks[row][col], HH_blocks[row][col])
        # HH_blocks[i] = dct(HH_blocks[i], norm="ortho")
        if HH_blocks[row][col][4][1] >= HH_blocks[row][col][3][2]:
            watermark[row][col] = 0
        else:
            watermark[row][col] = 255

# print(np.count_nonzero(watermark), watermark.shape[0] * watermark.shape[1] -
#       np.count_nonzero(watermark))
# processed_watermark = np.array(Image.open(
#     "processed_watermark.png").convert("1"))
# print(np.count_nonzero(processed_watermark), processed_watermark.shape[0] *
#       processed_watermark.shape[1] -
#       np.count_nonzero(processed_watermark))
Image.fromarray(watermark).save("extracted.png")

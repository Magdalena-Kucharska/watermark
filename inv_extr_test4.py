from math import floor, sqrt

import numpy as np
import pywt
from PIL import Image
from cv2 import dct

# from scipy.fftpack import dct

watermarked_image = np.array(Image.open("watermarked.jpg"))
b = watermarked_image[:, :, 0]
g = watermarked_image[:, :, 1]
r = watermarked_image[:, :, 2]

LL, (LH, HL, HH) = pywt.dwt2(b, wavelet="haar")
HH_blocks = []
for row in range(0, HH.shape[0], 8):
    for col in range(0, HH.shape[1], 8):
        HH_blocks.append(HH[row:row + 8, col:col + 8])
blocks_8x8 = sum([1 for block
                  in HH_blocks
                  if block.shape[0] == 8 and block.shape[1] == 8])
max_watermark_size = floor(sqrt(blocks_8x8))
watermark = np.zeros((max_watermark_size, max_watermark_size), dtype="uint8")
i = 0
for row in range(watermark.shape[0]):
    for col in range(watermark.shape[1]):
        dct(HH_blocks[i], HH_blocks[i])
        # HH_blocks[i] = dct(HH_blocks[i], norm="ortho")
        if HH_blocks[i][4][1] >= HH_blocks[i][3][2]:
            watermark[row][col] = 0
        else:
            watermark[row][col] = 255
        i += 1

print(np.count_nonzero(watermark), watermark.shape[0] * watermark.shape[1] -
      np.count_nonzero(watermark))
processed_watermark = np.array(Image.open(
    "processed_watermark.png").convert("1"))
print(np.count_nonzero(processed_watermark), processed_watermark.shape[0] *
      processed_watermark.shape[1] -
      np.count_nonzero(processed_watermark))
Image.fromarray(watermark).show()

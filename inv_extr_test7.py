from math import floor, sqrt

import numpy as np
import pywt
from PIL import Image
from scipy.fftpack import dct, idct

wi = np.array(Image.open("watermarked.png").convert("RGB"))
b = wi[:, :, 0]
g = wi[:, :, 1]
r = wi[:, :, 2]

LL1, (LH1, HL1, HH1) = pywt.dwt2(b, wavelet="haar")
LL2, (LH2, HL2, HH2) = pywt.dwt2(HL1, wavelet="haar")

HL2_blocks = []
for row in range(0, HL2.shape[0] - 8, 8):
    for col in range(0, HL2.shape[1], 8):
        HL2_blocks.append(dct(HL2[row:row + 8, col:col + 8]))
blocks_8x8 = sum([1 for block in HL2_blocks if block.shape == (8, 8)])
blocks_max = max([np.max(block) for block in HL2_blocks])
blocks_min = min([np.min(block) for block in HL2_blocks])
max_w_size = floor(sqrt(blocks_8x8 * 4))
watermark = np.zeros(max_w_size ** 2, dtype="uint8")

for i in range(0, watermark.shape[0] - 4, 4):
    j = i // 4
    watermark[i] = HL2_blocks[j][0][4]
    watermark[i + 1] = HL2_blocks[j][1][3]
    watermark[i + 2] = HL2_blocks[j][2][2]
    watermark[i + 3] = HL2_blocks[j][3][1]

watermark = watermark.reshape((max_w_size, max_w_size))
watermark *= 64
# Image.fromarray(watermark).show()
watermark = idct(watermark, norm="ortho")
# watermark = np.uint8(np.clip(watermark, 0, 255))

Image.fromarray(watermark).show()

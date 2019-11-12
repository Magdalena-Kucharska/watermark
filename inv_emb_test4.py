from math import floor, sqrt

import numpy as np
import pywt
from PIL import Image
from cv2 import dct, idct

# from scipy.fftpack import dct, idct
# F:\Magda\Downloads\10.1.1.661.536.pdf
cover_image = np.array(Image.open("wp6_res.jpg").convert("RGB"))
cover_image_b = cover_image[:, :, 0]
cover_image_g = cover_image[:, :, 1]
cover_image_r = cover_image[:, :, 2]

LL, (LH, HL, HH) = pywt.dwt2(cover_image_b, wavelet="haar")
HH_blocks = []
for row in range(0, HH.shape[0], 8):
    for col in range(0, HH.shape[1], 8):
        HH_blocks.append(HH[row:row + 8, col:col + 8])
blocks_8x8 = sum([1 for block
                  in HH_blocks
                  if block.shape[0] == 8 and block.shape[1] == 8])
max_watermark_size = floor(sqrt(blocks_8x8))
watermark = Image.open("watermark3.png").resize((max_watermark_size,
                                                 max_watermark_size)).convert(
    "1")
# if watermark.size[0] > max_watermark_size or watermark.size[1] > \
#         max_watermark_size:
watermark.save("processed_watermark.png")
watermark = np.array(watermark, dtype="uint8")
# if watermark.shape[0] < max_watermark_size or watermark.shape[1] < \
#         max_watermark_size:
#     temp_array = np.ones((max_watermark_size, max_watermark_size))
#     temp_array[:watermark.shape[0], :watermark.shape[1]] = watermark
#     watermark = temp_array
# Image.fromarray(watermark).show()
i = 0
for row in range(watermark.shape[0]):
    for col in range(watermark.shape[1]):
        dct(HH_blocks[i], HH_blocks[i])

        # HH_blocks[i] = dct(HH_blocks[i], norm="ortho")
        if watermark[row][col] == 0:
            if HH_blocks[i][4][1] < HH_blocks[i][3][2]:
                temp = np.copy(HH_blocks[i][4][1])
                HH_blocks[i][4][1] = HH_blocks[i][3][2]
                HH_blocks[i][3][2] = temp
        else:
            if HH_blocks[i][4][1] > HH_blocks[i][3][2]:
                temp = np.copy(HH_blocks[i][4][1])
                HH_blocks[i][4][1] = HH_blocks[i][3][2]
                HH_blocks[i][3][2] = temp
        diff = (7 - (HH_blocks[i][4][1] - HH_blocks[i][3][2]))
        if HH_blocks[i][4][1] >= HH_blocks[i][3][2]:
            HH_blocks[i][4][1] += diff
        else:
            HH_blocks[i][3][2] += diff
        idct(HH_blocks[i], HH_blocks[i])
        # HH_blocks[i] = idct(HH_blocks[i], norm="ortho")
        i += 1

i = 0
for row in range(0, HH.shape[0], 8):
    for col in range(0, HH.shape[1], 8):
        HH[row:row + 8, col:col + 8] = HH_blocks[i]
        i += 1

cover_image_b = pywt.idwt2((LL, (LH, HL, HH)), wavelet="haar")
watermarked_image = np.zeros(cover_image.shape)
watermarked_image[:, :, 0] = cover_image_b
watermarked_image[:, :, 1] = cover_image_g
watermarked_image[:, :, 2] = cover_image_r

Image.fromarray(np.uint8(watermarked_image)).convert("RGB").save(
    "watermarked.jpg")

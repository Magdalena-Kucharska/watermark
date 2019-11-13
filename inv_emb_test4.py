from math import floor, sqrt

import numpy as np
import pywt
import skimage
from PIL import Image
from cv2 import dct, idct

# from scipy.fftpack import dct, idct
# F:\Magda\Downloads\10.1.1.661.536.pdf
cover_image = np.array(Image.open("wp6_res.jpg").convert("RGB"))
cover_image_b = cover_image[:, :, 0]
cover_image_g = cover_image[:, :, 1]
cover_image_r = cover_image[:, :, 2]

LL, (LH, HL, HH) = pywt.dwt2(cover_image_b, wavelet="haar")
rows, cols = HH.shape[0], HH.shape[1]
while rows % 8 != 0:
    rows += 1
while cols % 8 != 0:
    cols += 1
HH_padded = np.zeros((rows, cols), dtype="float32")
HH_padded[:HH.shape[0], :HH.shape[1]] = HH
HH_blocks = skimage.util.view_as_blocks(HH_padded, (8, 8))
blocks_8x8 = sum([1 for block
                  in HH_blocks
                  if block.shape[0] == 8 and block.shape[1] == 8])
max_watermark_size = floor(sqrt(HH.shape[0] * HH.shape[1] / 64))
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

for row in range(watermark.shape[0]):
    for col in range(watermark.shape[1]):
        dct(HH_blocks[row][col], HH_blocks[row][col])

        # HH_blocks[i] = dct(HH_blocks[i], norm="ortho")
        if watermark[row][col] == 0:
            if HH_blocks[row][col][4][1] < HH_blocks[row][col][3][2]:
                temp = np.copy(HH_blocks[row][col][4][1])
                HH_blocks[row][col][4][1] = HH_blocks[row][col][3][2]
                HH_blocks[row][col][3][2] = temp
        else:
            if HH_blocks[row][col][4][1] > HH_blocks[row][col][3][2]:
                temp = np.copy(HH_blocks[row][col][4][1])
                HH_blocks[row][col][4][1] = HH_blocks[row][col][3][2]
                HH_blocks[row][col][3][2] = temp
        diff = (7 - (HH_blocks[row][col][4][1] - HH_blocks[row][col][3][2]))
        if HH_blocks[row][col][4][1] >= HH_blocks[row][col][3][2]:
            HH_blocks[row][col][4][1] += diff
        else:
            HH_blocks[row][col][3][2] += diff
        idct(HH_blocks[row][col], HH_blocks[row][col])
        # HH_blocks[i] = idct(HH_blocks[i], norm="ortho")

HH_blocks = HH_blocks.transpose((0, 2, 1, 3))
HH_blocks = HH_blocks.reshape((rows, cols))
HH = HH_blocks[:HH.shape[0], :HH.shape[1]]

cover_image_b = pywt.idwt2((LL, (LH, HL, HH)), wavelet="haar")
watermarked_image = np.zeros(cover_image.shape)
watermarked_image[:, :, 0] = cover_image_b
watermarked_image[:, :, 1] = cover_image_g
watermarked_image[:, :, 2] = cover_image_r

Image.fromarray(np.uint8(np.round(watermarked_image, 0))).convert("RGB").save(
    "watermarked.jpg")

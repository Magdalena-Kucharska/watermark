from math import floor

import numpy as np
import pywt
from PIL import Image

# 90c79db69c649d71eea4958ba45149075a02.pdf
image = np.asarray(Image.open("wp1.jpg"))
coeffs = pywt.dwt2(image, wavelet="db2")
LL, (LH, HL, HH) = coeffs
# Image.fromarray(np.uint8(LL)).show()
watermark = Image.open("watermark.png").convert("L")
watermark_np_arr = np.asarray(watermark, dtype="uint8")
watermark.save("processed_watermark.png")
watermark_np_arr_len_row = len(watermark_np_arr[0])
watermark_np_arr_len_col = len(watermark_np_arr)

c_r = floor((len(HL[0]) - watermark_np_arr_len_row) / 2)  # przesunięcia
c_c = floor((len(HL) - watermark_np_arr_len_col) / 2)
a = 3
for col in range(watermark_np_arr_len_col):
    for row in range(watermark_np_arr_len_row):
        intensity = str(watermark_np_arr[col][row]).zfill(3)
        # HH[col + c_c][row + c_r][0] += watermark_np_arr[col][row]
        HH[col + c_c][row + c_r][0] += (a * int(intensity[0]))
        HH[col + c_c][row + c_r][0] += (a * int(intensity[1]))
        HH[col + c_c][row + c_r][0] += (a * int(intensity[2]))
# for col in range(len(watermark_bin)):
#     for row in range(len(watermark_bin[0])):
#         if not watermark_bin[col][row]:
#             LL[col][row] += 1


image_inv = pywt.idwt2(coeffs=(LL, (LH, HL, HH)), wavelet="db2")
image_inv = image_inv[:, :, 0:3]
image = Image.fromarray(np.uint8(image_inv))
image.save("watermarked.jpg")

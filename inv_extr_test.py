from math import floor

import numpy as np
import pywt
from PIL import Image

original = np.asarray(Image.open("wp1.jpg"))
watermarked = np.asarray(Image.open("watermarked.jpg"))

original_coeffs = pywt.dwt2(original, wavelet="db2")
LL_o, (LH_o, HL_o, HH_o) = original_coeffs
watermarked_coeffs = pywt.dwt2(watermarked, wavelet="db2")
LL_w, (LH_w, HL_w, HH_w) = watermarked_coeffs
# watermark_arr = np.zeros((128, 128), dtype="uint8")

watermark_arr = np.zeros((128, 128), dtype="uint8")
watermark_arr_len_row = len(watermark_arr[0])
watermark_arr_len_col = len(watermark_arr)

c_r = floor((len(HL_w[0]) - watermark_arr_len_row) / 2)  # przesunięcia
c_c = floor((len(HL_w) - watermark_arr_len_col) / 2)
a = 1
for col in range(watermark_arr_len_col):
    for row in range(watermark_arr_len_row):
        # watermark_arr[col][row] = int((HH_w[col][row][0] - HH_o[col][row][
        #     0]))
        intensity = ''
        for i in range(3):
            digit = HH_w[col + c_c][row + c_r][i] \
                    - HH_o[col + c_c][row + c_r][i]
            # digit /= a
            if i == 0:
                # digit = HH_w[col + c_c][row + c_r][i] \
                #         - HH_o[col + c_c][row + c_r][i]
                # digit /= a
                digit = np.clip(digit, 0, 2)
            else:
                # digit = HL_w[col + c_c][row + c_r][i] \
                #         - HL_o[col + c_c][row + c_r][i]
                # digit /= a
                digit = np.clip(digit, 0, 5)
            intensity += str(int(digit))
        watermark_arr[col][row] = intensity
        # if HL_w[col + c_c][row + c_r][0] == 3:
        #     watermark_arr[col][row] = 0
        # else:
        #     watermark_arr[col][row] = 255

# watermark_arr = LL_w[:, :, 0] - LL_o[:, :, 0]
# watermark_arr = watermark_arr[0:243, 0:308]
# watermark_arr = np.clip(watermark_arr, 0, 1)
# watermark_arr = np.uint8(watermark_arr)
# watermark_arr *= 255
Image.fromarray(watermark_arr).show()

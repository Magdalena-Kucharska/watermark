from math import floor

import numpy as np
import pywt
from PIL import Image

# TODO: convert to RGB when alpha layer detected, improve code, connect to main program
image_np_arr = np.asarray(Image.open("screenshot.png"))
image_np_arr_b, image_np_arr_g, image_np_arr_r = image_np_arr[:, :, 0], image_np_arr[:, :, 1], image_np_arr[:, :, 2]
coeffs2b = pywt.dwt2(image_np_arr_b, wavelet="haar")
coeffs2g = pywt.dwt2(image_np_arr_g, wavelet="haar")
coeffs2r = pywt.dwt2(image_np_arr_r, wavelet="haar")

LLb, (LHb, HLb, HHb) = coeffs2b
LLg, (LHg, HLg, HHg) = coeffs2g
LLr, (LHr, HLr, HHr) = coeffs2r

watermark = Image.open("watermark.png").convert("L", colors=8)
watermark.save("watermark_processed.png")
watermark_np_arr = np.asarray(watermark)
print(f"watermark rows: {len(watermark_np_arr)}, cols: {len(watermark_np_arr[0])}")
print(f"image rows: {len(HLr)}, {len(HLg)}, {len(HLb)}, cols: {len(HLg[0])}, {len(HLr[0])}, {len(HLb[0])}")
watermark_np_arr_len_row = len(watermark_np_arr)
watermark_np_arr_len_col = len(watermark_np_arr[0])

c_r = floor((len(HLg) - watermark_np_arr_len_row) / 2)  # przesunięcia
c_c = floor((len(HLg[0]) - watermark_np_arr_len_col) / 2)
for row in range(watermark_np_arr_len_row):
    for col in range(watermark_np_arr_len_col):
        splitted = str(watermark_np_arr[row][col]).zfill(3)
        HLr[row + c_r][col + c_c] += int(splitted[0])
        HLg[row + c_r][col + c_c] += int(splitted[1])
        HLb[row + c_r][col + c_c] += int(splitted[2])

image_inv_r = pywt.idwt2(coeffs=(LLr, (LHr, HLr, HHr)), wavelet="haar")
image_inv_g = pywt.idwt2(coeffs=(LLg, (LHg, HLg, HHg)), wavelet="haar")
image_inv_b = pywt.idwt2(coeffs=(LLb, (LHb, HLb, HHb)), wavelet="haar")
image_inv = np.zeros(image_np_arr.shape, dtype="uint8")
image_inv[:, :, 0] = image_inv_b
image_inv[:, :, 1] = image_inv_g
image_inv[:, :, 2] = image_inv_r

image = Image.fromarray(image_inv)
image.save("watermarked.png")

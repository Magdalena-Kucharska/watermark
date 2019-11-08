from math import floor

import numpy as np
import pywt
from PIL import Image

original = np.asarray(Image.open("pic.jpg"))
watermarked = np.asarray(Image.open("watermarked.png"))

original_b, original_g, original_r = original[:, :, 0], original[:, :, 1], original[:, :, 2]
watermarked_b, watermarked_g, watermarked_r = watermarked[:, :, 0], watermarked[:, :, 1], watermarked[:, :, 2]

original_coeffs2b = pywt.dwt2(original_b, wavelet="haar")
original_coeffs2g = pywt.dwt2(original_g, wavelet="haar")
original_coeffs2r = pywt.dwt2(original_r, wavelet="haar")
watermarked_coeffs2b = pywt.dwt2(watermarked_b, wavelet="haar")
watermarked_coeffs2g = pywt.dwt2(watermarked_g, wavelet="haar")
watermarked_coeffs2r = pywt.dwt2(watermarked_r, wavelet="haar")

original_LLb, (original_LHb, original_HLb, original_HHb) = original_coeffs2b
original_LLg, (original_LHg, original_HLg, original_HHg) = original_coeffs2g
original_LLr, (original_LHr, original_HLr, original_HHr) = original_coeffs2r
watermarked_LLb, (watermarked_LHb, watermarked_HLb, watermarked_HHb) = watermarked_coeffs2b
watermarked_LLg, (watermarked_LHg, watermarked_HLg, watermarked_HHg) = watermarked_coeffs2g
watermarked_LLr, (watermarked_LHr, watermarked_HLr, watermarked_HHr) = watermarked_coeffs2r

watermark_arr = np.zeros((128, 128), dtype="uint8")

watermark_arr_len_row = len(watermark_arr)
watermark_arr_len_col = len(watermark_arr[0])
c_r = floor((len(watermarked_HLr) - watermark_arr_len_row) / 2)
c_c = floor((len(watermarked_HLr[0]) - watermark_arr_len_col) / 2)
for row in range(watermark_arr_len_row):
    for col in range(watermark_arr_len_col):
        string = str(np.clip(int(watermarked_HLr[row + c_r][col + c_c] - original_HLr[row + c_r][col + c_c]), 0, 2))
        string += str(np.clip(int(watermarked_HLg[row + c_r][col + c_c] - original_HLg[row + c_r][col + c_c]), 0, 5))
        string += str(np.clip(int(watermarked_HLb[row + c_r][col + c_c] - original_HLb[row + c_r][col + c_c]), 0, 5))
        watermark_arr[row][col] = int(string)

watermark = Image.fromarray(watermark_arr)

watermark.save("extracted.png")

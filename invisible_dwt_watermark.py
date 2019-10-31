import numpy as np
import pywt
from PIL import Image

image_np_arr = np.asarray(Image.open("pic.jpg"))
image_np_arr_b, image_np_arr_g, image_np_arr_r = image_np_arr[:, :, 0], image_np_arr[:, :, 1], image_np_arr[:, :, 2]
coeffs2b = pywt.dwt2(image_np_arr_b, wavelet="haar")
coeffs2g = pywt.dwt2(image_np_arr_g, wavelet="haar")
coeffs2r = pywt.dwt2(image_np_arr_r, wavelet="haar")

LLb, (LHb, HLb, HHb) = coeffs2b
LLg, (LHg, HLg, HHg) = coeffs2g
LLr, (LHr, HLr, HHr) = coeffs2r

watermark_np_arr = np.asarray(Image.open("grey.jpg").convert("L", colors=8))
for row in range(len(watermark_np_arr)):
    for col in range(len(watermark_np_arr[row])):
        splitted = str(watermark_np_arr[row][col])
        HLr[row][col] += int(splitted[0])
        HLg[row][col] += int(splitted[1])
        HLb[row][col] += int(splitted[2])

image_inv_r = pywt.idwt2(coeffs=(LLr, (LHr, HLr, HHr)), wavelet="haar")
image_inv_g = pywt.idwt2(coeffs=(LLg, (LHg, HLg, HHg)), wavelet="haar")
image_inv_b = pywt.idwt2(coeffs=(LLb, (LHb, HLb, HHb)), wavelet="haar")
image_inv = np.zeros(image_np_arr.shape)
image_inv[:, :, 0] = image_inv_b
image_inv[:, :, 1] = image_inv_g
image_inv[:, :, 2] = image_inv_r

image = Image.fromarray(np.uint8(image_inv))
image.save("im.jpg")

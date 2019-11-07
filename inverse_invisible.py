import numpy as np
import pywt
from PIL import Image

original = np.asarray(Image.open("pic.jpg"))
watermarked = np.asarray(Image.open("watermarked_compressed.jpg"))

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
# shape = (len(watermarked_HLb) + len(watermarked_HLg) + len(watermarked_HLr),
#          len(watermarked_HLb[0] + len(watermarked_HLg[0] + len(watermarked_HLr[0]))))
watermark_arr = np.zeros((128, 128))
# print(f"watermark rows: {len(watermark_arr)}, cols: {len(watermark_arr[0])}")
# print(len(watermark_arr))
for row in range(len(watermark_arr)):
    for col in range(len(watermark_arr[row])):
        string = str(int(watermarked_HLr[row][col] - original_HLr[row][col]))
        string += str(int(abs(watermarked_HLg[row][col] - original_HLg[row][col])))
        string += str(int(abs(watermarked_HLb[row][col] - original_HLb[row][col])))
        # string = string.zfill(3)
        watermark_arr[row][col] = int(string)
#         string = f"{int(watermarked_HLr[row][col] - original_HLr[row][col])}"
#         string += f"{int(watermarked_HLg[row][col] - original_HLg[row][col])*10}"
#         string += f"{int(watermarked_HLb[row][col] - original_HLb[row][col])*100}"
#         print(string)
# watermark_arr[row][col] = (watermarked_HLr[row][col] - original_HLr[row][col]) + \
#                           10 * (watermarked_HLg[row][col] - original_HLg[row][col]) + \
#                           100 * (watermarked_HLb[row][col] - original_HLb[row][col])
# print(round(watermarked_HLr[row][col] - original_HLr[row][col], 0))

# print(watermark_arr)
# watermark_arr_norm = 255 * (watermark_arr - np.min(watermark_arr)) / np.ptp(watermark_arr).astype(int)
watermark = Image.fromarray(watermark_arr)
watermark = watermark.convert("L", colors=8)
watermark.save("extracted.png")
# plt.imsave("extracted.png", watermark_arr)
# print(np.max(watermark_arr))

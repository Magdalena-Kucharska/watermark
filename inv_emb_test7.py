from math import floor, sqrt

import cv2
import numpy as np
import pywt
import skimage.util
from PIL import Image

# 589-1-589-1-10-20150122.pdf

cover = np.array(Image.open("wp4.jpg").convert("RGB"))
b = cover[:, :, 0]
g = cover[:, :, 1]
r = cover[:, :, 2]

LL1, (LH1, HL1, HH1) = pywt.dwt2(b, wavelet="haar")
LL2, (LH2, HL2, HH2) = pywt.dwt2(HL1, wavelet="haar")
rows, cols = HL2.shape[0], HL2.shape[1]
while rows % 8 != 0:
    rows += 1
while cols % 8 != 0:
    cols += 1
HL2_padded = np.zeros((rows, cols), dtype="float32")
HL2_padded[:HL2.shape[0], :HL2.shape[1]] = HL2
HL2_blocks = skimage.util.view_as_blocks(HL2_padded, (8, 8))

for i in range(HL2_blocks.shape[0]):
    for j in range(HL2_blocks.shape[1]):
        HL2_blocks[i][j] = cv2.dct(HL2_blocks[i][j])
max_w_size = floor(sqrt(HL2.shape[0] * HL2.shape[1] * 4 / 64))
watermark = np.array(Image.open("watermark.jpg").
                     resize((max_w_size, max_w_size)).
                     convert("L"), dtype="float32")
watermark = cv2.dct(watermark)
# watermark /= 10
k, l = 0, 0
for i in range(0, watermark.shape[0]):
    for j in range(0, watermark.shape[1], 4):
        try:
            HL2_blocks[k][l][0][4] = watermark[i][j]
            HL2_blocks[k][l][1][3] = watermark[i][j + 1]
            HL2_blocks[k][l][2][2] = watermark[i][j + 2]
            HL2_blocks[k][l][3][1] = watermark[i][j + 3]
            if l == HL2_blocks.shape[1] - 1:
                k += 1
                l = 0
            else:
                l += 1
        except IndexError:
            pass
for i in range(HL2_blocks.shape[0]):
    for j in range(HL2_blocks.shape[1]):
        HL2_blocks[i][j] = cv2.idct(HL2_blocks[i][j])
HL2_blocks = HL2_blocks.transpose((0, 2, 1, 3))
HL2_blocks = HL2_blocks.reshape((rows, cols))
HL2 = HL2_blocks[:HL2.shape[0], :HL2.shape[1]]
HL1 = pywt.idwt2((LL2, (LH2, HL2, HH2)), wavelet="haar")
b = pywt.idwt2((LL1, (LH1, HL1, HH1)), wavelet="haar")
watermarked = np.zeros(cover.shape, dtype="float32")
watermarked[:, :, 0] = b
watermarked[:, :, 1] = g
watermarked[:, :, 2] = r
watermarked = Image.fromarray(np.uint8(np.round(watermarked, 0)))
# watermarked.show()
watermarked.save("watermarked.png")
watermarked = np.array(Image.open("watermarked.png"), dtype="float32")
# watermarked = np.array(watermarked)
b = watermarked[:, :, 0]
g = watermarked[:, :, 1]
r = watermarked[:, :, 2]
LL1, (LH1, HL1, HH1) = pywt.dwt2(b, wavelet="haar")
LL2, (LH2, HL2, HH2) = pywt.dwt2(HL1, wavelet="haar")
HL2_padded = np.zeros((rows, cols), dtype="float32")
HL2_padded[:HL2.shape[0], :HL2.shape[1]] = HL2
HL2_blocks = skimage.util.view_as_blocks(HL2_padded, (8, 8))
for i in range(HL2_blocks.shape[0]):
    for j in range(HL2_blocks.shape[1]):
        HL2_blocks[i][j] = cv2.dct(HL2_blocks[i][j])
watermark_extr = np.zeros(watermark.shape, dtype="float32")
k, l = 0, 0
for i in range(0, watermark.shape[0]):
    for j in range(0, watermark.shape[1], 4):
        try:
            watermark_extr[i][j] = HL2_blocks[k][l][0][4]
            watermark_extr[i][j + 1] = HL2_blocks[k][l][1][3]
            watermark_extr[i][j + 2] = HL2_blocks[k][l][2][2]
            watermark_extr[i][j + 3] = HL2_blocks[k][l][3][1]
            if l == HL2_blocks.shape[1] - 1:
                k += 1
                l = 0
            else:
                l += 1
        except IndexError:
            break
watermark_extr = cv2.idct(watermark_extr)
# watermark_extr = np.uint8(watermark_extr)
watermark = cv2.idct(watermark)
# watermark_extr *= 10
# watermark_extr = np.interp(watermark_extr, (watermark_extr.min(),
#                                             watermark_extr.max()), (0.0,
#                                             1.0))
Image.fromarray(np.round(watermark_extr, 0)).convert("L").save(
    "extracted_watermark.jpg")
# plt.imshow(watermark_extr, cmap="Greys")
# plt.show()

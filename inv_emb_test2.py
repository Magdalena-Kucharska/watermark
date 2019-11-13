from math import floor, sqrt

# from cv2 import dct, idct
import cv2
import numpy as np
import pywt
from PIL import Image

# 175-1-175-1-10-20150122.pdf
# Select any color image as the original image ‘OI’.
# Decompose the image into 3 color components R, G and B.
image = Image.open("photo.jpg").convert("RGB")
oi = np.array(image)
oi_b = oi[:, :, 0]
oi_g = oi[:, :, 1]
oi_r = oi[:, :, 2]

# Apply DWT to B channel. Then we get multiresolution sub-bands LL1, HL1,
# LH1, and HH1.
LL1, (LH1, HL1, HH1) = pywt.dwt2(oi_b, wavelet="haar")

# Apply DWT again to HL1 and we get LL2, HL2, LH2 and HH2.
# Select the HL2 sub-bands.
LL2, (LH2, HL2, HH2) = pywt.dwt2(HL1, wavelet="haar")

# Divide the HL2 sub-band into 8X8 size blocks (consider each block as cell).
HL2_blocks = []
for col in range(0, len(HL2), 8):
    for row in range(0, len(HL2[0]), 8):
        arr = HL2[col:col + 8, row:row + 8]
        HL2_blocks.append(arr)

# Apply DCT to each cell of HL2 sub-band.
HL2_blocks_dct = [np.zeros(block.shape) for block in HL2_blocks]
for i, block in enumerate(HL2_blocks):
    # HL2_blocks_dct[i] = dct(block, norm="ortho")
    HL2_blocks_dct[i] = cv2.dct(block, cv2.DCT_ROWS)

# Select any color watermark image ‘WI’. Obtain the R, G, B channels of WI.
image = Image.open("watermark.jpg").convert("RGB")
blocks_8x8 = sum([1 for block
                  in HL2_blocks
                  if len(block) == 8 and len(block[0]) == 8])
max_size = floor(sqrt(blocks_8x8))
if max_size % 2 != 0:
    max_size -= 1
image = image.resize((max_size, max_size))
image.show()
wi = np.array(image, dtype="float32")
# wi_b = np.float32(wi[:, :, 0])
# wi_g = np.float32(wi[:, :, 1])
# wi_r = np.float32(wi[:, :, 2])
# wi_b = wi[:, :, 0]
# wi_g = wi[:, :, 1]
# wi_r = wi[:, :, 2]


# Apply DCT to each R, G and B channels separately.
# wi_b_dct = np.zeros(wi_b.shape)
# wi_b_dct=dct(wi_b, norm="ortho")
# wi_b_dct = cv2.dct(wi_b, cv2.DCT_ROWS)
# wi_g_dct = np.zeros(wi_g.shape)
# wi_g_dct=dct(wi_g, norm="ortho")
# wi_g_dct = cv2.dct(wi_g, cv2.DCT_ROWS)
# wi_r_dct = np.zeros(wi_r.shape)
# wi_r_dct=dct(wi_r, norm="ortho")
# wi_r_dct = cv2.dct(wi_r, cv2.DCT_ROWS)
wi_dct = cv2.dct(wi, cv2.DCT_ROWS)

# Embed one pixel of every R, G and B channels of Watermark image WI
# into each cell of HL2.
i = 0
max = max([np.max(block) for block in HL2_blocks_dct])
min = min([np.min(block) for block in HL2_blocks_dct])
wi_dct = (wi_dct - min) / (max - min)
for col in range(len(wi_dct)):
    for row in range(len(wi_dct[0])):
        # HL2_blocks_dct[i][2][1] = wi_r_dct[col][row]
        # HL2_blocks_dct[i][3][2] = wi_g_dct[col][row]
        HL2_blocks_dct[i][4][1] = wi_dct[col][row]
        i += 1

# Apply IDCT to the each cell of HL2 sub-band.
for i in range(len(HL2_blocks_dct)):
    # HL2_blocks[i]=idct(HL2_blocks_dct[i], norm="ortho")
    HL2_blocks[i] = cv2.idct(HL2_blocks_dct[i], cv2.DCT_ROWS)
i = 0
for col in range(0, len(HL2), 8):
    for row in range(0, len(HL2[0]), 8):
        HL2[col:col + 8, row:row + 8] = HL2_blocks[i]
        i += 1

# Apply 2 levels IDWT to B channel.
HL1 = pywt.idwt2((LL2, (LH2, HL2, HH2)), wavelet="haar")[0:len(HL1),
      0:len(HL1[0])]
oi_b = pywt.idwt2((LL1, (LH1, HL1, HH1)), wavelet="haar")

# Combine the R, G and B channels to get the watermarked image ‘WMI’.
wmi = np.zeros(oi.shape)
wmi[:, :, 0] = oi_b
wmi[:, :, 1] = oi_g
wmi[:, :, 2] = oi_r
# wmi = np.round(wmi, 0)

Image.fromarray(np.uint8(wmi)).convert("RGB").save("watermarked.png")

MSE = np.sum((oi - wmi) ** 2) / (3 * len(oi) * len(oi[0]))
print(MSE)

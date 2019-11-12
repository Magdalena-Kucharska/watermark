from math import floor, sqrt

# from cv2 import dct, idct
import cv2
import numpy as np
import pywt
from PIL import Image

# Take the watermarked image ‘WMI’ and decompose
# into R, G and B channels.
wmi = np.array(Image.open("watermarked.png").convert("RGB"))
wmi_b = wmi[:, :, 0]
wmi_g = wmi[:, :, 1]
wmi_r = wmi[:, :, 2]

# omi = np.array(Image.open("wp.png").convert("RGB"))
# omi_b = wmi[:, :, 0]
# omi_g = wmi[:, :, 1]
# omi_r = wmi[:, :, 2]

# Apply DWT to B channel. Then we get multiresolution
# sub-bands LL1, HL1, LH1, and HH1.
LL1, (LH1, HL1, HH1) = pywt.dwt2(wmi_b, wavelet="haar")
# LL1o, (LH1o, HL1o, HH1o) = pywt.dwt2(omi_b, wavelet="haar")

# Apply DWT again to HL1 and we get LL2, HL2, LH2 and HH2.
# Select the HL2 sub-bands.
LL2, (LH2, HL2, HH2) = pywt.dwt2(HL1, wavelet="haar")
# LL2o, (LH2o, HL2o, HH2o) = pywt.dwt2(HL1o, wavelet="haar")

# Divide the HL2 sub-band into 8X8 size blocks (consider each block as cell).
HL2_blocks = []
for col in range(0, len(HL2), 8):
    for row in range(0, len(HL2[0]), 8):
        HL2_blocks.append(np.array(HL2[col:col + 8, row:row + 8]))
# HL2o_blocks = []
# for col in range(0, len(HL2o), 8):
#     for row in range(0, len(HL2o[0]), 8):
#         HL2o_blocks.append(np.array(HL2o[col:col + 8, row:row + 8]))
blocks_8x8 = sum([1 for block
                  in HL2_blocks
                  if len(block) == 8 and len(block[0]) == 8])
max_size = floor(sqrt(blocks_8x8))
if max_size % 2 != 0:
    max_size -= 1
wi = np.zeros((max_size, max_size), dtype="float32")
# wi_b = np.float32(wi[:, :, 0])
# wi_g = np.float32(wi[:, :, 1])
# wi_r = np.float32(wi[:, :, 2])
# Apply DCT to each cell of HL2 sub-band.
HL2_blocks_dct = [np.zeros(block.shape) for block in HL2_blocks]
for i, block in enumerate(HL2_blocks):
    HL2_blocks_dct[i] = cv2.dct(block, cv2.DCT_ROWS)
    # HL2_blocks_dct[i] = dct(block, norm="ortho")

# HL2o_blocks_dct = [np.zeros(block.shape) for block in HL2o_blocks]
# for i, block in enumerate(HL2o_blocks):
#     dct(block, HL2o_blocks_dct[i])

# Extract the first bits of watermark from first cell of B channel
# and placed in first positions of WR, WG nd WB channels.
# Extract the second bits of watermark from the second cell of B channel and
# placed in second positions of WR, WG and WB channels.
# Repeat the previous step until we get all the pixels into the WR, WG and
# WB channels of ‘WI’ separately.
i = 0
for col in range(len(wi)):
    for row in range(len(wi[0])):
        # wi_r[col][row] = HL2_blocks_dct[i][2][1]
        # wi_g[col][row] = HL2_blocks_dct[i][3][2]
        wi[col][row] = HL2_blocks_dct[i][4][1]
        # HL2_blocks_dct[i][3][0] += wi_r_dct[col][row]
        # HL2_blocks_dct[i][2][1] += wi_g_dct[col][row]
        # HL2_blocks_dct[i][1][2] += wi_b_dct[col][row]
        i += 1
# wi_b_idct = np.zeros(wi_b.shape)
# wi_b_idct = cv2.idct(wi_b, cv2.DCT_ROWS)
# wi_g_idct = np.zeros(wi_g.shape)
# wi_g_idct = cv2.idct(wi_g, cv2.DCT_ROWS)
# wi_r_idct = np.zeros(wi_r.shape)
wi_idct = np.clip(cv2.idct(wi, cv2.DCT_ROWS), 0, 255)
# wi_b_idct = idct(wi_b, norm="ortho")
# wi_g_idct = idct(wi_g, norm="ortho")
# wi_r_idct = idct(wi_r, norm="ortho")
# wi[:, :, 0] = wi_b_idct
# wi[:, :, 1] = wi_g_idct
# wi[:, :, 2] = wi_r_idct
Image.fromarray(np.uint8(wi)).show()

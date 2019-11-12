from math import floor

import numpy as np
# from scipy.fftpack import dct, idct
import pywt
from PIL import Image
from cv2 import dct, idct

# 8efda0e78b555124117df282c68a13e17f3f.pdf
# Read color cover image I & binary watermark image W.
# Convert I from RGB color space into YCbCr color space
# for better watermarking efficiency. Since the pixel values
# are highly correlated in RGB color space, the watermark
# embedding in YCbCr color space is preferred.
I = np.array(Image.open("wp.png").convert("YCbCr"), dtype="uint8")
W = np.array(Image.open("0c9.png").resize((128, 128)).convert("1"),
             dtype="uint8").flatten()

# Select the luminance component Y to embed the
# watermark, because the human eye is less sensitive to
# luminance in YCbCr space than other color channels in
# RGB space.
Y = np.float32(I[:, :, 0])

# Divide Y into BxB non-overlapping blocks of pixels
# according to the number of bits of the original watermark
# image, where each bit in the watermark image
# corresponds to one block in the luminance component.
B = floor((len(Y) * len(Y[0])) / len(W))
Y_blocks = []
for row in range(0, len(Y), B):
    for col in range(0, len(Y[0]), B):
        Y_blocks.append(Y[row:row + B, col:col + B])

# Perform the following steps for each block to embed the
# watermark information bits:
n = 0
for i in range(len(Y_blocks)):
    if n < len(W):
        # Apply DCT calculation, to obtain DCT coefficients DCTb.
        # Y_blocks[i] = dct(Y_blocks[i])
        dct(Y_blocks[i], Y_blocks[i])

        # Apply 1-level DWT using daubechies filters to DCTb
        # to decompose it into four sub-bands:
        # LL1(approximation sub-band), HL1(horizontal
        # sub-band), LH1(vertical sub-band) and HH1(diagonal
        # sub-band).
        LL1, (LH1, HL1, HH1) = pywt.dwt2(Y_blocks[i], wavelet="db1")

        # Find the size of LH1 matrix and store it in S.
        # S = LH1.shape
        a = 2

        # Modify the vertical DWT coefficients LH1 by adding
        # the binary watermark bits.
        for row in range(len(LH1)):
            for col in range(len(LH1[0])):
                try:
                    if W[n]:
                        LH1[row][col] += 100
                    else:
                        LH1[row][col] -= 100
                    n += 1
                except IndexError:
                    break

        Y_blocks[i] = pywt.idwt2((LL1, (LH1, HL1, HH1)), wavelet="db1")
        idct(Y_blocks[i], Y_blocks[i])

i = 0
for row in range(0, len(Y), B):
    for col in range(0, len(Y[0]), B):
        Y[row:row + B, col:col + B] = Y_blocks[i]
        i += 1

I[:, :, 0] = Y
Image.fromarray(I, mode="YCbCr").convert("RGB").save("watermarked.png")

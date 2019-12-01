import os
from math import floor, sqrt, log

import cv2
import numpy as np
import skimage
from PIL import Image

import main_window


def calculate_mse(M, N, cover_image_arr, watermarked_image_arr):
    square_diff = np.sum((cover_image_arr - watermarked_image_arr) ** 2)
    return 1 / (M * N) * square_diff


def calculate_psnr(mse):
    return 10 * log((255 ** 2) / mse, 10)


class Invisible3DDCTBased:

    def __init__(self, Q=60, channel='b', output_format=".jpg", quality=95):
        self.Q = Q
        channels = {'r': 0, 'g': 1, 'b': 2}
        self.channel = channels[channel]
        self.output_format = output_format
        self.quality = quality

    def encode(self, cover_image_path, watermark_path, output_path):
        image = Image.open(cover_image_path).convert("RGB")
        M, N = image.size
        image = np.array(image)
        rows, cols = image.shape[0], image.shape[1]
        while rows % 8 != 0:
            rows += 1
        while cols % 8 != 0:
            cols += 1
        image_padded = np.zeros((rows, cols, 3), dtype="float32")
        image_padded[:image.shape[0], :image.shape[1]] = image
        image_blocks = skimage.util.view_as_blocks(image_padded, (8, 8, 3))
        max_watermark_size = floor(sqrt(image.shape[0] * image.shape[1] / 64))
        watermark = np.array(
            Image.open(watermark_path).resize(
                (max_watermark_size, max_watermark_size
                 )).convert("1"), dtype="uint8")

        for i in range(image_blocks.shape[0]):
            for j in range(image_blocks.shape[1]):
                for k in range(3):
                    image_blocks[i][j][0][:, :, k] = \
                        cv2.dct(image_blocks[i][j][0][:, :, k])

        k, l = 0, 0
        for row in range(watermark.shape[0]):
            for col in range(watermark.shape[1]):
                if watermark[row][col] == 0:
                    image_blocks[k][l][0][0][0][self.channel] += \
                        self.Q / 2 - \
                        ((image_blocks[k][l][0][0][0][self.channel] -
                          0.75 * self.Q) % self.Q)
                else:
                    image_blocks[k][l][0][0][0][self.channel] += \
                        self.Q / 2 - \
                        ((image_blocks[k][l][0][0][0][self.channel] +
                          0.75 * self.Q) % self.Q)
                if l == image_blocks.shape[1] - 1:
                    k += 1
                    l = 0
                else:
                    l += 1

        for row in range(image_blocks.shape[0]):
            for col in range(image_blocks.shape[1]):
                for k in range(3):
                    image_blocks[row][col][0][:, :, k] = \
                        cv2.idct(image_blocks[row][col][0][:, :, k])

        image_blocks = np.round(image_blocks, 0)
        image_blocks = image_blocks.transpose((0, 3, 2, 1, 4, 5))
        image_blocks = image_blocks.reshape((rows, cols, 3))
        watermarked_image = image_blocks[:image.shape[0], :image.shape[1]]
        watermarked_image = np.uint8(watermarked_image)

        save_file_name = os.path.basename(cover_image_path)
        save_file_name_split = save_file_name.split('.')
        save_file_name = '.'.join(
            save_file_name_split[:-1]) + self.output_format
        unique_name = main_window.generate_unique_file_name(save_file_name,
                                                            output_path)
        save_path = os.path.join(output_path, unique_name)
        if self.output_format in [".jpg", ".jpeg"]:
            Image.fromarray(watermarked_image).save(save_path,
                                                    quality=self.quality)
        else:
            Image.fromarray(watermarked_image).save(save_path)

        return calculate_psnr(calculate_mse(M, N, image, watermarked_image))

    def decode(self, watermarked_image_path, output_path):
        watermarked_image = np.array(Image.open(watermarked_image_path))
        rows, cols = watermarked_image.shape[0], watermarked_image.shape[1]
        while rows % 8 != 0:
            rows += 1
        while cols % 8 != 0:
            cols += 1
        watermarked_image_padded = np.zeros((rows, cols, 3), dtype="float32")
        watermarked_image_padded[:watermarked_image.shape[0],
        :watermarked_image.shape[1]] = watermarked_image
        watermarked_image_blocks = skimage.util.view_as_blocks(
            watermarked_image_padded, (8, 8, 3))
        max_watermark_size = floor(
            sqrt(watermarked_image.shape[0] * watermarked_image.shape[1]
                 / 64))
        watermark = np.zeros((max_watermark_size, max_watermark_size),
                             dtype="uint8")
        for i in range(watermarked_image_blocks.shape[0]):
            for j in range(watermarked_image_blocks.shape[1]):
                for k in range(3):
                    watermarked_image_blocks[i][j][0][:, :, k] = cv2.dct(
                        watermarked_image_blocks[i][j][0][:, :, k])
        k, l = 0, 0
        for row in range(watermark.shape[0]):
            for col in range(watermark.shape[1]):
                if (watermarked_image_blocks[k][l][0][0][0][self.channel]
                    % self.Q) >= (self.Q / 2):
                    watermark[row][col] = 255
                if l == watermarked_image_blocks.shape[1] - 1:
                    k += 1
                    l = 0
                else:
                    l += 1

        watermarked_image_name = os.path.basename(watermarked_image_path)
        watermarked_image_name_split = watermarked_image_name.split('.')
        watermarked_image_name = '.'.join(watermarked_image_name_split[:-1]) \
                                 + "_extracted_watermark" + \
                                 f".{watermarked_image_name_split[-1]}"
        unique_name = main_window.generate_unique_file_name(
            watermarked_image_name, output_path)
        save_path = os.path.join(output_path, unique_name)
        Image.fromarray(watermark).save(save_path)

# Real-CUGAN - Iceshell

Real-CUGAN - Iceshell is a GUI program that upscales and denoises anime-style images.
Iceshell is available on Linux and Windows.

![Preview](preview.png)

This program can make your images better and sharper! 

Original image vs ImageMagick upscale vs Real-CUGAN upscale:
![comparison](comparison.png)

A GPU is required to run this program.

## Installation

>Python

Download the repository and install PyQt5:
```
git clone https://github.com/eli0009/Real-CUGAN_Iceshell
pip3 install PyQt5
```

## Usage

>Python

Go to the install directory and run iceshell.py:
```
cd Real-CUGAN_Iceshell
python3 iceshell.py
```

JPG, JPEG, PNG and WEBP image formats are supported.

Either drag & drop your images or select them by clicking on the main window. Upscaled images are outputted to the same folder as the input by default.

## About Real-CUGAN

[Real-CUGAN](https://github.com/bilibili/ailab/tree/main/Real-CUGAN) is an AI super resolution model for anime images

## Acknowledgements
- [Real-CUGAN ncnn Vulkan](https://github.com/nihui/realcugan-ncnn-vulkan) by nihui
- [BreezeStyleSheets](https://github.com/Alexhuszagh/BreezeStyleSheets)
- Qt for Python
- Qt Designer
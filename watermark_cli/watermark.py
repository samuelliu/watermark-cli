#!/usr/bin/env python3

import os
import json
import sys
import random
from PIL import Image, ImageDraw, ImageFont

CONFIG_FILE = os.path.expanduser("~/.watermark-cli/config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def add_watermark(image_path, output_path, watermark_text):
    with Image.open(image_path) as img:
        x_text = 0
        y_text = 0
        for o in range(5):
            watermark_text = watermark_text + "   " + watermark_text
        watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
        font = ImageFont.load_default(size=100)
        for n in range(20):
            draw = ImageDraw.Draw(watermark)
            draw.text((x_text % 5 * -200, y_text), watermark_text, font=font, fill=(0, 0, 0, 30))
            x_text += 1
            y_text += 200
        watermark=watermark.rotate(17.5,  expand=1)

        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            watermarked = Image.alpha_composite(img.convert('RGBA'), watermark)
        else:
            watermarked = img.copy()
            watermarked.paste(watermark, (-100, -500), watermark)

        if img.format == 'JPEG':
            watermarked = watermarked.convert('RGB')
            watermarked.save(output_path, quality=95, optimize=True)
        elif img.format == 'WEBP':
            watermarked.save(output_path, format='WEBP', lossless=True)
        else:
            watermarked.save(output_path, format=img.format)

    print(f"Watermarked {image_path} to {output_path}")

def process_images(source_path, watermark_text):
    supported_formats = ('.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp', '.gif')
    if os.path.isfile(source_path):
        if source_path.lower().endswith(supported_formats):
            output_dir = os.path.dirname(source_path)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, 'watermark_' + os.path.basename(source_path))
            add_watermark(source_path, output_path, watermark_text)
        else:
            print(f"Error: {source_path} is not a supported image file")
    elif os.path.isdir(source_path):
        output_dir = source_path
        os.makedirs(output_dir, exist_ok=True)
        for filename in os.listdir(source_path):
            if filename.lower().endswith(supported_formats):
                input_path = os.path.join(source_path, filename)
                output_path = os.path.join(output_dir, 'watermark_' + filename)
                add_watermark(input_path, output_path, watermark_text)
    else:
        print(f"Error: {source_path} is not a valid file or directory")

def set_config(default_text):
    config = load_config()
    config['default_text'] = default_text
    save_config(config)
    print(f"Default watermark text set to: {default_text}")

def main():
    if len(sys.argv) < 2:
        print("Usage: watermark <image_path> [--text 'Your Watermark'] or watermark config --default-text 'Your Text'")
        return

    config = load_config()
    default_text = config.get('default_text', '')

    if sys.argv[1] == 'config':
        if len(sys.argv) == 4 and sys.argv[2] == '--default-text':
            set_config(sys.argv[3])
        else:
            print("Usage for config: watermark config --default-text 'Your Text'")
    else:
        source = sys.argv[1]
        custom_text = None
        if len(sys.argv) == 4 and sys.argv[2] == '--text':
            custom_text = sys.argv[3]
        
        watermark_text = custom_text if custom_text else default_text

        if not watermark_text:
            print("Error: No watermark text provided. Please use --text or set a default text with the config command")
            return

        process_images(source, watermark_text)

if __name__ == "__main__":
    main()

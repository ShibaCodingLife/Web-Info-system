import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

__ALL__ = ("generate_random_code", "generate_image")


def generate_random_code(length=4):
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    code = ''.join(random.choice(characters) for _ in range(length))
    return code.lower()


def generate_image(code):
    image = Image.new("RGB", (150, 60), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 使用艺术字体
    with open("static/arial.ttf", "rb") as f:
        # Well shit, I don't have arial.ttf on local OS
        font = ImageFont.truetype(f, 40)

    for i in range(4):
        draw.text((10 + i * 30, 10), code[i], font=font, fill=(0, 0, 0))

    for _ in range(20):
        x1 = random.randint(0, 150)
        y1 = random.randint(0, 60)
        x2 = random.randint(0, 150)
        y2 = random.randint(0, 60)
        draw.line((x1, y1, x2, y2), fill=(0, 0, 0))

    for _ in range(30):
        x = random.randint(0, 150)
        y = random.randint(0, 60)
        draw.rectangle([x, y, x + 3, y + 3], fill=(0, 0, 0))

    for _ in range(500):
        x = random.randint(0, 150)
        y = random.randint(0, 60)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        draw.point((x, y), fill=(r, g, b))

    image = image.filter(ImageFilter.SMOOTH_MORE)
    return image

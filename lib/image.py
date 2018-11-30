import os
import random
import numpy as np
from PIL import Image
from PIL import ImageFilter
import PIL.ImageDraw as ImageDraw
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

DATA_DIR = os.path.join(os.getcwd() + '/lib/fonts/')

class _Captcha(object):
    """A parent CAPTCHA class that implements generate() and write().
    """
    def generate(self, chars, format='png'):
        """Generate an Image Captcha of the given characters.

        :param chars: text to be generated.
        :param format: image file format
        """
        im = self.generate_image(chars)
        out = BytesIO()
        im.save(out, format=format)
        out.seek(0)
        return out

    def write(self, chars, output, format='png'):
        """Generate and write an image CAPTCHA data to the output.

        :param chars: text to be generated.
        :param output: output destination.
        :param format: image file format
        """
        im = self.generate_image(chars)
        return im.save(output, format=format)

class ColorCaptcha(_Captcha):
    """Create a colored CAPTCHA with noise and curve.
    :param width: The width of the CAPTCHA image.
    :param height: The height of the CAPTCHA image.
    :param fonts: Fonts to be used to generate CAPTCHA images.
    :param font_sizes: Random choose a font size from this parameters.
    """
    def __init__(self, width=160, height=60, fonts=None, font_sizes=None, curve=True, dots=True):
        self._width = width
        self._height = height
        self._fonts = [DATA_DIR + 'Merriweather-Bold.ttf',
                       DATA_DIR + 'Merriweather-Regular.ttf',
                       DATA_DIR + 'Merriweather-Black.ttf',
                       DATA_DIR + 'Roboto-Regular.ttf',
                       DATA_DIR + 'Roboto-Black.ttf',
                       DATA_DIR + 'Roboto-Medium.ttf',]
        self._font_sizes = font_sizes or (40, 44, 48, 52)
        self._truefonts = []
        self._curve = curve
        self._dots = dots

    @property
    def truefonts(self):
        if self._truefonts:
            return self._truefonts
        self._truefonts = tuple([
            truetype(n, s)
            for n in self._fonts
            for s in self._font_sizes
        ])
        return self._truefonts

    @staticmethod
    def create_noise_curve(image, color):
        for i in range(0, random.randint(0,3)):
            w, h = image.size
            x1 = random.randint(int(w/5), int(w / 3))
            x2 = random.randint(w - int(w / 3), w-int(w/5))
            y1 = random.randint(int(h / 5), h - int(h / 5))
            y2 = random.randint(y1, h)
            points = [x1, y1, x2, y2]
            if random.random()<0.5:
                start = random.randint(160, 200)
                end = random.randint(0, 20)
            else:
                end = random.randint(160, 200)
                start = random.randint(0, 20)
            Draw(image).arc(points, start, end, fill=color)
        return image

    @staticmethod
    def create_noise_dots(image, color, width=random.randint(1,5), number=random.randint(2,60)):
        draw = Draw(image)
        w, h = image.size
        if random.random()>0.5:
            return image
        while number:
            x1 = random.randint(0, w)
            y1 = random.randint(0, h)
            draw.line(((x1, y1), (x1 - 1, y1 - 1)), fill=color, width=width)
            number -= 1
        return image

    def create_captcha_image(self, chars, color, background):
        """Create the CAPTCHA image itself.

        :param chars: text to be generated.
        :param color: color of the text.
        :param background: color of the background.

        The color should be a tuple of 3 numbers, such as (0, 255, 255).
        """
        image = Image.new('RGB', (self._width, self._height), background)
        font = random.choice(self.truefonts)
        draw = Draw(image)

        def _draw_character(font, c):
            w, h = draw.textsize(c, font)
            dx = random.randint(0, 4)
            dy = random.randint(0, 6)

            im = Image.new('RGBA', (w + dx, h + dy))

            Draw(im).text((dx, dy), c, font=font, fill=color)
            im = im.crop(im.getbbox())
            im = im.rotate(random.uniform(-20, 20), Image.BILINEAR, expand=1)

            return im

        images = []
        char_list = []

        for c in chars:
            images.append(_draw_character(font, " "))
            char_list.append(" ")
            if random.random() > 0.5:
               images.append(_draw_character(font, " "))
               char_list.append(" ")
            images.append(_draw_character(font, c))
            char_list.append(c)

        text_width = sum([im.size[0] for im in images])

        width = max(text_width, self._width)
        image = image.resize((width, self._height))

        average = int(text_width / len(chars))
        rand = int(0.25 * average)
        offset = int(average * 0.1)

        bboxes = []

        for i in range(len(images)):
            w, h = images[i].size
            mask = images[i].convert('RGBA')
            x1, y1 = offset, int((self._height - h) / 2)
            x2, y2 = offset + w, int((self._height - h) / 2) + h
            image.paste(images[i], (x1, y1), mask)

            if char_list[i] is not " ":
                bboxes.append([x1, y1, x2, y2])

            offset = offset + w + random.randint(-rand, 0)

        if width > self._width:
            old_width, old_height = image.size
            image = image.resize((self._width, self._height))
            new_width, new_height = image.size
            width_scale = new_width / old_width
            height_scale = new_height / old_height
            for box in bboxes:
                for index in range(len(box)):
                    if index % 2:
                        box[index] = int(box[index] * height_scale)
                    else:
                        box[index] = int(box[index] * width_scale)

        return image, bboxes

    def generate_image(self, chars, bbox):
        """Generate the image of the given characters.

        :param chars: text to be generated.
        """
        background = random_color(238, 255)
        color = random_color(10, 200, 255)
        im, boxes = self.create_captcha_image(chars, color, background)
        if self._dots:
            self.create_noise_dots(im, color)
        if self._curve:
            self.create_noise_curve(im, color)
        im = im.filter(ImageFilter.SMOOTH)
        if bbox:
            return im, boxes
        return im

class SUTDCaptcha(_Captcha):
    """Create an image CAPTCHA similar to the one used by SUTD.

    :param width: The width of the CAPTCHA image.
    :param height: The height of the CAPTCHA image.
    :param fonts: Fonts to be used to generate CAPTCHA images.
    :param font_sizes: Random choose a font size from this parameters.
    """
    def __init__(self, width=160, height=60, fonts=None, font_sizes=None):
        self._width = width
        self._height = height
        self._fonts = [DATA_DIR + 'Roboto-Regular.ttf',
                       DATA_DIR + 'DroidSansMono.ttf']
        self._font_sizes = font_sizes or (40, 44, 48, 52, 56)
        self._truefonts = []

    @property
    def truefonts(self):
        if self._truefonts:
            return self._truefonts
        self._truefonts = tuple([
            truetype(n, s)
            for n in self._fonts
            for s in self._font_sizes
        ])
        return self._truefonts

    @staticmethod
    def get_sine(x):
        return 5*np.sin((x/200)*np.pi)

    @staticmethod
    def get_cosine(x):
        return 5*np.cos((x/200)*np.pi)

    def create_captcha_image(self, chars, color, background):
        """Create the CAPTCHA image itself.

        :param chars: text to be generated.
        :param color: color of the text.
        :param background: color of the background.

        The color should be a tuple of 3 numbers, such as (0, 255, 255).
        """
        image = Image.new('RGB', (self._width, self._height), background)
        font = random.choice(self.truefonts)
        draw = Draw(image)

        def _draw_character(font, c):
            w, h = draw.textsize(c, font)

            dx = 1
            dy = 1

            im = Image.new('RGBA', (w + dx, h + dy))

            Draw(im).text((dx, dy), c, font=font, fill=color)
            im = im.crop(im.getbbox())
            im = im.rotate(random.uniform(-10, 10), Image.BILINEAR, expand=1)

            return im

        images = []
        char_list = []

        for c in chars:
            images.append(_draw_character(font, c))
            char_list.append(c)

        text_width = sum([im.size[0] for im in images])

        width = max(text_width, self._width)
        image = image.resize((width, self._height))

        average = int(text_width / len(chars))
        rand = int(0.25 * average)
        offset = int(average * 0.1)

        bboxes = []

        if random.random()>0.5:
            for i in range(len(images)):
                w, h = images[i].size
                mask = images[i].convert('RGBA')
                x1, y1 = offset, int(self.get_sine(offset)+15)
                x2, y2 = offset + w, y1 + h
                image.paste(images[i], (x1, y1), mask)

                if char_list[i] is not " ":
                    bboxes.append([x1, y1, x2, y2])

                offset = offset + w + random.randint(-rand, 0)
        else:
            for i in range(len(images)):
                w, h = images[i].size
                mask = images[i].convert('RGBA')
                x1, y1 = offset, int(self.get_cosine(offset)+15)
                x2, y2 = offset + w, y1 + h
                image.paste(images[i], (x1, y1), mask)

                if char_list[i] is not " ":
                    bboxes.append([x1, y1, x2, y2])

                offset = offset + w + random.randint(-rand, 0)

        if width > self._width:
            old_width, old_height = image.size
            image = image.resize((self._width, self._height))
            new_width, new_height = image.size
            width_scale = new_width / old_width
            height_scale = new_height / old_height
            for box in bboxes:
                for index in range(len(box)):
                    if index % 2:
                        box[index] = int(box[index] * height_scale)
                    else:
                        box[index] = int(box[index] * width_scale)

        return image, bboxes

    def generate_image(self, chars, bbox):
        """Generate the image of the given characters.

        :param chars: text to be generated.
        """
        background = (255,255,255,255)
        color = (random.randint(8,14),random.randint(130,150),random.randint(8,14),255)
        im, boxes = self.create_captcha_image(chars, color, background)
        im = im.filter(ImageFilter.SMOOTH)
        if bbox:
            return im, boxes
        return im

class BWCaptcha(_Captcha):
    """Create a greyscale 4-character CAPTCHA using the Gentium font

    :param width: The width of the CAPTCHA image. This is the target width before scaling.
    :param height: The height of the CAPTCHA image. This is the target height before scaling.
    :param scale_factor: The scale factor at which we render fonts.
    :param target_width: The target width at which to feed into the neural network.
    :param target_height: The target height at which to feed into the neural network.
    :param fonts: Fonts to be used to generate CAPTCHA images.
    :param font_sizes: Random choose a font size from this parameters.
    """
    def __init__(self, width=160, height=60, scale_factor=3, target_width=200, target_height=75, fonts=None, font_sizes=None):
        self._width = width * scale_factor
        self._height = height * scale_factor
        self._scale_factor = scale_factor
        self._target_width = target_width
        self._target_height = target_height
        self._fonts = [DATA_DIR + 'GenBasBI.ttf',
                       DATA_DIR + 'GenBasB.ttf',
                       DATA_DIR + 'GenBasI.ttf',
                       DATA_DIR + 'GenBasR.ttf']
        self._font_sizes = font_sizes or (50, 55, 60)
        self._truefonts = []

    @property
    def truefonts(self):
        if self._truefonts:
            return self._truefonts
        self._truefonts = tuple([
            truetype(n, s)
            for n in self._fonts
            for s in self._font_sizes
        ])
        return self._truefonts

    def create_captcha_image(self, chars, color, background):
        """Create the CAPTCHA image itself.

        :param chars: text to be generated.
        :param color: color of the text.
        :param background: color of the background.

        The color should be a tuple of 3 numbers, such as (0, 255, 255).
        """
        image = Image.new('RGB', (self._width, self._height), background)

        # BW Captcha has to choose between Gentium variants
        font = random.choice(self.truefonts)
        draw = Draw(image)

        def _draw_character(font, c):
            font = random.choice(self.truefonts)
            w, h = draw.textsize(c, font)

            dx = random.randint(0, 4)
            dy = random.randint(0, 6)
            im = Image.new('RGBA', (w + dx, h + dy))
            Draw(im).text((dx, dy), c, font=font, fill=color)

            # rotate
            im = im.crop(im.getbbox())
            im = im.rotate(random.uniform(-20, 20), Image.BILINEAR, expand=1)

            return im

        images = []
        char_list = []

        for c in chars:
            if random.random() > 0.3:
                images.append(_draw_character(font, " "))
                char_list.append(" ")
            images.append(_draw_character(font, c))
            char_list.append(c)

        text_width = sum([im.size[0] for im in images])

        width = max(text_width, self._width)
        image = image.resize((width, self._height))

        average = int(text_width / len(chars))
        rand = int(0.25 * average)
        offset = int(average * 0.1)

        bboxes = []

        for i in range(len(images)):
            w, h = images[i].size
            mask = images[i].convert('RGBA')
            x1, y1 = offset, int((self._height - h) / 2)
            x2, y2 = offset + w, int((self._height - h) / 2) + h
            image.paste(images[i], (x1, y1), mask)

            if char_list[i] is not " ":
                bboxes.append([x1, y1, x2, y2])

            offset = offset + w + random.randint(-rand, 0)

        if width > self._width:
            old_width, old_height = image.size
            image = image.resize((self._width, self._height))
            new_width, new_height = image.size
            width_scale = new_width / old_width
            height_scale = new_height / old_height
            for box in bboxes:
                for index in range(len(box)):
                    if index % 2:
                        box[index] = int(box[index] * height_scale)
                    else:
                        box[index] = int(box[index] * width_scale)

        for box in bboxes:
            for ind in range(len(box)):
                if ind % 2 == 0:
                    box[ind] = int(box[ind] / self._scale_factor * self._target_width / (self._width / self._scale_factor))
                else:
                    box[ind] = int(box[ind] / self._scale_factor * self._target_height / (self._height / self._scale_factor))

        return image, bboxes

    def generate_image(self, chars, bbox):
        """Generate the image of the given characters.

        :param chars: text to be generated.
        :param bbox: the bbox
        """
        background = (255,255,255)
        color = random_color(0, 0, opacity=255)
        im, boxes = self.create_captcha_image(chars, color, background)
        im = im.filter(ImageFilter.SMOOTH)
        if bbox:
            return im, boxes
        return im

def draw_rect(im, bboxes):
    draw = Draw(im)
    for box in bboxes:
        draw.rectangle(box, outline='red', fill=None)

def random_color(start, end, opacity=None):
    red = random.randint(start, end)
    green = random.randint(start, end)
    blue = random.randint(start, end)
    if opacity is None:
        return (red, green, blue)
    return (red, green, blue, opacity)
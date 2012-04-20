import os

import Image, ImageChops

from django.conf import settings
from django.core.management.base import BaseCommand

def trim(im, bg=(255, 255, 255, 0)):
    bg = Image.new(im.mode, im.size, bg)
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    else:
        # found no content
        raise ValueError('cannot trim; image was empty')

def crop_screenshots():
    for filename in os.listdir(settings.KHAN_EXERCISE_SCREENSHOT_DIR):
        if not filename.endswith('-full.png'):
            continue

        # Load image and trim
        filename = os.path.join(settings.KHAN_EXERCISE_SCREENSHOT_DIR, filename)
        image = trim(Image.open(filename))
        
        grad = gradient(215, 223, 182, 255, 255, 255, image.size[0], image.size[1])
        r, g, b, alpha = image.split()
        grad.paste(image, mask=alpha) # paste the resized version on gradient
        
        # Save image
        filename, ext = os.path.splitext(filename)
        grad.save(filename + '-trimmed.png', 'png')


def gradient(r1, g1, b1, r2, g2, b2, size, grad_size):

  rgb1 = (int(r1),int(g1),int(b1))
  rgb2 = (int(r2),int(g2),int(b2))
  size = int(size)
  grad_size = int(grad_size)

  # create image
  im = Image.new('RGB', (size, grad_size))
  def channel(i, c):
    """calculate the value of a single color channel for a single pixel"""
    return rgb1[c] + int((i * 1.0 / grad_size) * (rgb2[c] - rgb1 [c]))

  def color(i):
    """calculate the RGB value of a single pixel"""
    return tuple([channel(i, c) for c in range(3)])

  gradient = [ color(i) for i in xrange(grad_size) ]

  # put gradient into image
  for x in xrange(size):
    for y in xrange(grad_size):
        im.putpixel((x, y), gradient[y])
  # send image

  return im

class Command(BaseCommand):
    help = 'Crops out transparency from screenshots in settings.KHAN_EXERCISE_SCREENSHOT_DIR.'

    def handle(self, *args, **options):
        crop_screenshots()

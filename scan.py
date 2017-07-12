import zbar
import io
import time
import picamera
from PIL import Image



stream = io.BytesIO()
with picamera.PiCamera() as camera:
    #camera.start_preview()
    time.sleep(2)
    camera.capture(stream, format='jpeg')
stream.seek(0)
pil = Image.open(stream)

scanner = zbar.ImageScanner()

scanner.parse_config('enable')

pil = pil.convert('L')
width, height = pil.size
raw = pil.tostring()

image = zbar.Image(width, height, 'Y800', raw)

scanner.scan(image)

for symbol in image:
    print '\ndecoded'
    print symbol.data
    print symbol.type
    #print 'decoded', symbol.type, '"%s"' % symbol.data

del(image)


#!/usr/bin/python
from PIL import Image

f = open("magic.jpg","r")
data_raw = f.read()
data = ''.join('{0:08b}'.format(ord(x), 'b') for x in data_raw)
im = Image.open("./raw.png")
pix = im.load()
width, height = im.size
encode_image = Image.new("RGB",(width,height))
newpix = encode_image.load()
count = 0
for i in range(0,width,1):
	for j in range(0,height,1):
                if count+2 < len(data):
                    newpix[i,j] = (pix[i,j][0] & 0xfd) | (int(data[count])<<1),(pix[i,j][1] & 0xfe) | int(data[count+1])  , (pix[i,j][2] & 0xfb) | (int(data[count+2]) << 2)
                    count += 3
                else :
                    newpix[i,j] = (pix[i,j][0] & 0xfd),(pix[i,j][1] & 0xfe)  ,(pix[i,j][2] & 0xfb)

encode_image.save("en.png")

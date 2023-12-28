import rawpy
from astropy.io import fits
from AAtools import img_read

file=input("Images a lire : ")

rgb = img_read(file)

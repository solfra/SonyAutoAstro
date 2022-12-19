import rawpy
from astropy.io import fits
from AAtools import img_read

file=input("Images a lire : ")

rgb = img_read(file)

fits.writeto(file[:-4]+'_r.fits',rgb[:,:,0],overwrite=True)
fits.writeto(file[:-4]+'_g.fits',rgb[:,:,1],overwrite=True)
fits.writeto(file[:-4]+'_b.fits',rgb[:,:,2],overwrite=True)
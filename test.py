#import gphoto2 as gp
import os
import matplotlib.pyplot as plt
import rawpy
from astropy.io import fits
import serial
import keyring
from astroquery.astrometry_net import AstrometryNet
import cv2 
from astropy import units as u
from astropy.coordinates import SkyCoord
from astroquery.simbad import Simbad
import numpy as np
from AAtools import *
import configparser


"""
#------------- Test cfg -------------

cfg_check()
config = configparser.ConfigParser()



config = configparser.ConfigParser()

config.read('AA.cfg')


#---------- Test prise de vue ----------
os.system("gphoto2 --list-ports")
os.system("gphoto2 --auto-detect ")
os.system("gphoto2 --summary")

if config['gphoto']['port'] == '?' :
    port = input("Entrer le nom du port USB a utiliser pour l'appareil photo : ")
else :
    port = config['gphoto']['port']

if int(config['sky_object']['nbrPict']) == 0 :
    nbr = int(input('Combien de photo à prendre ? '))
else : 
    nbr = int(config['sky_object']['nbrPict'])

if config['sky_object']['name'] == '?' :
    name = input('Quel est le nom des images ? ')
else :
    name = config['sky_object']['name']
    
for i in range(nbr):
    os.system("gphoto2 --port={} --filename={}.arw  --capture-image-and-download".format(port,name+'_'+str(i)))
print("test FINI")



#---------- Test lecture raw ----------
file= input('nom fichier : ')
raw = rawpy.imread(file)

rgb = raw.postprocess(use_camera_wb=True)

raw.close()


print(rgb.shape)

plt.imshow(rgb)
plt.show()


plt.subplot(131)
plt.imshow(rgb[:,:,0])
plt.subplot(132)
plt.imshow(rgb[:,:,1])
plt.subplot(133)
plt.imshow(rgb[:,:,2])
plt.show()

fits.writeto(file[:-4]+'.fits',rgb,overwrite=True)

#---------- Test comande telescope ----------
"""
scope = serial.Serial("/dev/ttyUSB0")

c='J' #Demande si alignement OK; Repond 1 si true 0 sinon
scope.write(c.encode())
rep=scope.read(2)
if rep == '#' :
    rep=scope.read(2)
    print("l'alignement est",ord(rep))
else : 
    print("l'alignement est",ord(rep))

"""

#---------- Test astrometrie ----------

key = config['astrometry']['user']
file = input('fichier ? ')
ast = AstrometryNet()
ast.api_key = keyring.get_password('astroquery:astrometry_net', key)

r = astrometry(file,ast)
ra,dec=get_coord(r)




ra = 322.87161335
dec = 12.0829461448
c= SkyCoord(ra*u.degree,dec*u.degree)
print('RA =',c.ra.hms[0],'h',c.ra.hms[1],'min',c.ra.hms[2],'s','\nDEC =',c.dec.dms[0],'deg',c.dec.dms[1],'min',c.dec.dms[2],'sec')

fov = 0.44
minRA = ra-fov
maxRA = ra+fov
minDEC = dec-fov
maxDEC = dec+fov
result = Simbad.query_criteria('ra>'+str(minRA)+'&ra<'+str(maxRA)+'&dec>'+str(minDEC)+'&dec<'+str(maxDEC),cat='NGC')
print(result)

#------ test collimation ------
print('test opencv')
c = cv2.HoughCircles(rgb[:,:,1],cv2.HOUGH_GRADIENT,80,5,param1=1,param2=1,minRadius=100,maxRadius=0)
print(c)

plt.figure()
plt.imshow(rgb[:,:,1])
fig = plt.gcf()
ax = fig.gca()
for i in c[0,:] :

    plt.scatter(i[0],i[1])
    circle1 = plt.Circle((i[0], i[1]), i[2])
    ax.add_patch(circle1)

plt.show()


#------ test détection d'étoiles ------
from astropy.stats import sigma_clipped_stats
from photutils.detection import DAOStarFinder
from photutils.aperture import CircularAperture
from photutils.detection import find_peaks

file = 'test/test5_g.fits'
a = fits.open(file)
data = a[0].data
mean, median, std = sigma_clipped_stats(data, sigma=3.0) 
pixel_angle = 0.6
seeing = 2.0
fwhm = seeing/pixel_angle *8
threshold=255-0.5*std
tbl = find_peaks(data, threshold, box_size=fwhm*50)
print(tbl)


daofind = DAOStarFinder(fwhm=fwhm, threshold=255.-0.5*std)  
sources = daofind(data - mean)
for col in sources.colnames:  
    sources[col].info.format = '%.8g'  # for consistent table output
print(sources)  

positions = np.transpose((sources['xcentroid'], sources['ycentroid']))

positions = np.transpose((tbl['x_peak'], tbl['y_peak']))
apertures = CircularAperture(positions, r=4.)
plt.imshow(data, origin='lower')
apertures.plot(color='red', lw=1.5, alpha=0.5)
plt.show()

#fwhm_calc = np.sqrt(np.mean(sources['npix'])/np.pi)*pixel_angle
#print(fwhm_calc,'arcsec')





#---------- Simbad query ------------------

from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astropy import units as u

t = Simbad.query_object('M42')
c = SkyCoord([t['RA'][0]+" "+t['DEC'][0]], unit=(u.hourangle, u.deg))

from AAtools import get_coord
from astropy.io import fits
a = fits.open("wcs_m42.fits")
h = a[0].header
ra,dec = get_coord(h)
c_r = SkyCoord(ra*u.deg,dec*u.deg)
sep = c.separation(c_r)
print(sep.arcmin)
print("img",c_r.ra.deg, c_r.dec.deg)
print("th",c.ra.deg, c.dec.deg)
print(c.ra.deg - c_r.ra.deg, c.dec.deg - c_r.dec.deg)
"""
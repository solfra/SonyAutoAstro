#-------------------- Initialisation des librairies-------------------- 
import os
import matplotlib.pyplot as plt
import rawpy
import keyring
from astroquery.astrometry_net import AstrometryNet
from astropy.io import fits
from astropy import units as u
from astropy.coordinates import SkyCoord
from astroquery.simbad import Simbad
from AAtools import *

#-------------------- Inisialisation systèmes-------------------- 

ast = AstrometryNet()
ast.api_key = keyring.get_password('astroquery:astrometry_net', 'solfra38')

os.system("gphoto2 --list-ports")
os.system("gphoto2 --auto-detect ")
os.system("gphoto2 --summary")

port = input("Entrer le nom du port USB a utiliser pour l'appareil photo : ")

#-------------------- Test du systèmes-------------------- 
test_img = True
i=0 #numero de l'image test
while test_img :
    os.system("gphoto2 --port={} --filename=test{}.arw  --capture-image-and-download".format(port,i))
    
    rgb=img_read('test{}.arw'.format(i))

    continue_test = input("\nQue voulez vous faire ? \nAstrometrie (a) \nContinuer test (Y/n) ")
    
    if continue_test=='a' or continue_test =='A':
        f='test{}.arw'.format(i)
        fits.writeto(f[:-4]+'_b.fits',rgb[:,:,2],overwrite=True)
        result_ast=astrometry('test{}_b.fits'.format(i))
        fits.writeto('heder_result.fits', [], result_ast,overwrite=True)
        ra, dec = get_coord(result_ast)
        simbad_query(ra,dec)
        continue_test = input("\nQue voulez vous faire ? \nContinuer test (Y/n) ")

    if continue_test == "N" or continue_test == "n" :
        test_img = False

    i+=1

#-------------------- Capture des images --------------------

capt  = True

while capt : 
    nbr = int(input('Combien de photo à prendre ? '))
    name = input('Quel est le nom des images ? ')
    for i in range(nbr):
        os.system("gphoto2 --port={} --filename={}.arw  --capture-image-and-download".format(port,name+'_'+str(i)))

    print('\n**************\nFin des captures')

    continue_capt = input("\nQue voulez vous faire ? \nContinuer capture (Y/n) ")
    if continue_capt == "N" or continue_capt == "n" :
        capt = False
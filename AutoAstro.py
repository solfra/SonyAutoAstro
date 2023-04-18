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
import configparser
from AAtools import *

#-------------------- Inisialisation systèmes-------------------- 
cfg_check()
config = configparser.ConfigParser()
config.read('AA.cfg')

ast = AstrometryNet()

key = config['astrometry']['user']
ast.api_key = keyring.get_password('astroquery:astrometry_net', key)

os.system("gphoto2 --list-ports")
os.system("gphoto2 --auto-detect ")
os.system("gphoto2 --summary")

if config['gphoto']['port'] == '?' :
    port = input("Entrer le nom du port USB a utiliser pour l'appareil photo : ")
else :
    port = config['gphoto']['port']

if config['sky_object']['get_coord'] == 'y' or config['sky_object']['get_coord'] == 'Y' :
    obj = Simbad.query_object(config['sky_object']['name'])
    try:
        c_obj = SkyCoord([obj['RA'][0]+" "+obj['DEC'][0]], unit=(u.hourangle, u.deg))
    except :
        print('error in object query')
        exit()

internet_verif() #verifie qu'une conection internet est bien presente

#-------------------- Test du systèmes-------------------- 
test_img = True
i=0 #numero de l'image test

while test_img :
    os.system("gphoto2 --port={} --filename=test{}.arw  --trigger-capture --wait-event-and-download=FILEADDED".format(port,i))
    
    rgb=img_read('test{}.arw'.format(i))

    continue_test = input("\nQue voulez vous faire ? \nAstrometrie (a) \nContinuer test (Y/n) ")
    
    if continue_test=='a' or continue_test =='A':
        f='test{}.arw'.format(i)
        fits.writeto(f[:-4]+'_b.fits',rgb[:,:,2],overwrite=True)

        result_ast=astrometry('test{}_b.fits'.format(i),ast)
        fits.writeto('heder_result.fits', [], result_ast,overwrite=True)
        ra, dec = get_coord(result_ast)
        fov = get_fov(result_ast)

        if config['sky_object']['get_coord'] == 'y' or config['sky_object']['get_coord'] == 'Y' :
            c_img = SkyCoord(ra*u.deg,dec*u.deg)
            sep = c_img.separation(c_obj)
            print("Separation obj image :",sep.arcmin,"arcmin")
            print("Plus precisement :",(c_obj.ra.deg - c_img.ra.deg)*60, "arcmin en RA et", (c_obj.dec.deg - c_img.dec.deg)*60,"arcmin en DEC")
            if sep > max(fov) :
                print("Cible hors champ !")
                print("Objects dans le champ actuel : ")
                simbad_query(ra,dec,fov=max(fov)*60)
        else :
            print("Objects dans le champ actuel : ")
            simbad_query(ra,dec,fov=max(fov)*60)


        continue_test = input("\nQue voulez vous faire ? \nContinuer test (Y/n) ")

    if continue_test == "N" or continue_test == "n" :
        test_img = False

    i+=1

#-------------------- Capture des images --------------------

capt  = True

while capt : 
    if int(config['sky_object']['nbrPict']) == 0 :
        nbr = int(input('Combien de photo à prendre ? '))
    else : 
        nbr = int(config['sky_object']['nbrPict'])
    
    if config['sky_object']['name'] == '?' :
        name = input('Quel est le nom des images ? ')
    else :
        name = config['sky_object']['name']
    
    for i in range(nbr):
        os.system("gphoto2 --port={} --filename={}.arw  --trigger-capture --wait-event-and-download=FILEADDED".format(port,name+'_'+str(i)))
        if int(config['astrometry']['check_every_x_imgs']) != 0 and i % int(config['astrometry']['check_every_x_imgs']) == 0 and i!=0:
            f=name+'_'+str(i)+'.arw'
            fits.writeto(f[:-4]+'_b.fits',rgb[:,:,2],overwrite=True)

            result_ast=astrometry(name+'_'+str(i)+'_b.fits',ast)
            fits.writeto('heder_result.fits', [], result_ast,overwrite=True)
            ra, dec = get_coord(result_ast)
            fov = get_fov(result_ast)

            if config['sky_object']['get_coord'] == 'y' or config['sky_object']['get_coord'] == 'Y' :
                c_img = SkyCoord(ra*u.deg,dec*u.deg)
                sep = c_img.separation(c_obj)
                print("Separation obj image :",sep.arcmin,"arcmin")
                print("Plus précisément :",(c_obj.ra.deg - c_img.ra.deg)*60, "arcmin en RA et", (c_obj.dec.deg - c_img.dec.deg)*60,"arcmin en DEC")
                if sep > max(fov) :
                    print("Cible hors champ !")
                    print("Objects dans le champ actuel : ")
                    simbad_query(ra,dec,fov=max(fov)*60)
            else :
                print("Objects dans le champ actuel : ")
                simbad_query(ra,dec,fov=max(fov)*60)

    print('\n**************\nFin des captures')

    continue_capt = input("\nQue voulez vous faire ? \nContinuer capture (Y/n) ")
    if continue_capt == "N" or continue_capt == "n" :
        capt = False

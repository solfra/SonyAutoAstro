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
import serial
from AAnexstar import *
import logging

#-------------------- Inisialisation systèmes-------------------- 
logging.basicConfig(filename="AutoAstro.log", level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

logging.info("Check config file")
cfg_check()
config = configparser.ConfigParser()
logging.info("Read config file")
config.read('AA.cfg')

internet_verif() #verifie qu'une conection internet est bien presente

logging.info("Astrometry start")
ast = AstrometryNet()
key = config['astrometry']['user']
ast.api_key = keyring.get_password('astroquery:astrometry_net', key)

logging.info("gphoto2 inisialisation")
os.system("gphoto2 --list-ports")
os.system("gphoto2 --auto-detect ")
os.system("gphoto2 --summary")

if config['gphoto']['port'] == '?' :
    port = input("Entrer le nom du port USB a utiliser pour l'appareil photo : ")
else :
    port = config['gphoto']['port']
logging.info("Port used for gphoto2 : %s", port)


if config['sky_object']['get_coord'] == 'y' or config['sky_object']['get_coord'] == 'Y' :
    logging.info("Get coordinate of the object")
    obj = Simbad.query_object(config['sky_object']['name'])
    logging.info("Objet : %s", obj)
    try:
        c_obj = SkyCoord([obj['RA'][0]+" "+obj['DEC'][0]], unit=(u.hourangle, u.deg))
        logging.info("coord : %s", c_obj)
    except :
        print('error in object query')
        logging.error("Error in object query")
        exit()

logging.info("Nexstar inisialisation")
if config['nexstar']['port'] == '?' :
    nexstar_port = input("Nexstar usb port : ")
else :
    nexstar_port = config['nexstar']['port'] 
logging.info("Nexstar port %s", nexstar_port)
logging.info("Start nexstar serial port")
scope = serial.Serial(nexstar_port)
set_time(scope,utc=int(config['nexstar']['UTC']),daylight=int(config['nexstar']['daylight']))
nexstar_info(scope)
lat,long = get_location(scope)


#-------------------- Test du systèmes-------------------- 
logging.info("Start systeme test")

test_img = True
i=0 #numero de l'image test

while test_img :
    logging.info("Capture image test %s", i)
    os.system("gphoto2 --port={} --filename=test{}.arw  --trigger-capture --wait-event-and-download=FILEADDED".format(port,i))
    
    rgb=img_read('test{}.arw'.format(i))

    continue_test = input("\nQue voulez vous faire ? \nAstrometrie (a) \nContinuer test (Y/n) ")
    
    if continue_test=='a' or continue_test =='A':
        logging.info("Astrometry of the image")
        f='test{}.arw'.format(i)
        fits.writeto(f[:-4]+'_b.fits',rgb[:,:,2],overwrite=True)
        c_img, fov = astromerty_img(config, ast, c_obj, 'test{}_b.fits'.format(i))

        continue_test = input("\nQue voulez vous faire ? \nSyncronisation telescope (s) \nContinuer test (Y/n) ")
    
        if continue_test=='s' or continue_test == 'S' :
            logging.info("Sync mount with last coord obtened by astrometry")
            print("Syncronisation du telescope avec les derniere coordonnes obtenue par astrometrie")
            sync_precise_ra_dec(scope,c_img.ra.deg,c_img.dec.deg)

    if continue_test == "N" or continue_test == "n" :
        logging.info("End of systeme test")
        test_img = False

    i+=1

#-------------------- Capture des images --------------------
logging.info("Start image capture")
capt  = True

while capt : 
    if int(config['sky_object']['nbrPict']) == 0 :
        nbr = int(input('Combien de photo à prendre ? '))
    else : 
        nbr = int(config['sky_object']['nbrPict'])
    logging.info("Number of image you want : %s", nbr)

    if config['sky_object']['name'] == '?' :
        name = input('Quel est le nom des images ? ')
    else :
        name = config['sky_object']['name']
    logging.info("Object name : %s", name)
    
    for i in range(nbr):
        logging.info("Capture image %s", i)
        t = get_time(scope)
        os.system("gphoto2 --port={} --filename={}.arw  --trigger-capture --wait-event-and-download=FILEADDED".format(port,name+'_'+str(i)))
        
        if int(config['astrometry']['check_every_x_imgs']) != 0 and i % int(config['astrometry']['check_every_x_imgs']) == 0 and i!=0:
            centering = True
            i_center = 1
        
        if i_center > int(config['nexstar']['max_test']) :
            print("Error in centering, make it manualy")
            logging.error("Error in centering, make it manualy")
            logging.info('End of the programm')
            print("End of the programm")
            goto_precise_azm_alt(scope, 0,0)
            exit()

        if centering :
            logging.info("Check image coordinates")
            f=name+'_'+str(i)+'.arw'
            raw = rawpy.imread(f)
            rgb = raw.postprocess(use_camera_wb=True)
            raw.close()
            logging.info("convert into fits file")
            fits.writeto(f[:-4]+'_b.fits',rgb[:,:,2],overwrite=True)
            c_img, fov = astromerty_img(config, ast, c_obj, f[:-4]+'_b.fits')
            if abs(c_img.separation(c_obj).arcmin) > max(fov)/2 :
                logging.info("Nexstar centering")
                nexstar_obj_centering(scope,c_obj,c_img,t, lat,long)
                i_center += 1
            else :
                centering = False

    print('\n**************\nFin des captures')
    logging.info('End of capture')

    continue_capt = input("\nQue voulez vous faire ? \nContinuer capture (Y/n) ")
    if continue_capt == "N" or continue_capt == "n" :
        capt = False

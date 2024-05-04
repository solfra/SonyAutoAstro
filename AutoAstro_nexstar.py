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
import argparse

#-------------------- Inisialisation systèmes-------------------- 
logging.basicConfig(filename="AutoAstro.log", level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

parser = argparse.ArgumentParser(description='Auto_astro')
parser.add_argument('--config',help='Config file name',default='AA.cfg')
args = parser.parse_args()

conf_name=args.config

config = configparser.ConfigParser()
logging.info("Read config file")
config.read(conf_name)

try:
    port = config['gphoto']['port']
    key = config['astrometry']['user']
    check_img = config['astrometry'].getint('check_every_x_imgs')
    sky_coord = config['sky_object'].getboolean('get_coord')
    image_nbr = config['sky_object'].getint('nbrpict')
    name = config['sky_object']['name']
    nexstar_port = config['nexstar']['port'] 
    utc=config['nexstar'].getint('UTC')
    daylight=config['nexstar'].getint('daylight')
    nexstar_max_test = config['nexstar'].getint('max_test')
except :
    print('Error in config file, exit')
    logging.error('! Erro in config file, exit')
    exit()

internet_verif() #verifie qu'une conection internet est bien presente

logging.info("Astrometry start")
ast = AstrometryNet()
ast.api_key = keyring.get_password('astroquery:astrometry_net', key)

logging.info("gphoto2 inisialisation")
os.system("gphoto2 --list-ports")
os.system("gphoto2 --auto-detect ")
os.system("gphoto2 --summary")

if port == '?' :
    port = input("Entrer le nom du port USB a utiliser pour l'appareil photo : ")
logging.info("Port used for gphoto2 : %s", port)


if sky_coord :
    logging.info("Get coordinate of the object")
    obj = Simbad.query_object(config['sky_object']['name'])
    logging.info("Objet : %s", obj)
    try:
        c_obj = SkyCoord(obj['RA'][0]+" "+obj['DEC'][0], unit=(u.hourangle, u.deg))
        logging.info("coord : %s", c_obj)
    except :
        print('error in object query')
        logging.error("Error in object query")
        exit()
else : 
    print("You can not take astrometry because no object coordinate")
    logging.warning("Astrometry is impossible, no object coordinate")

logging.info("Nexstar inisialisation")
if nexstar_port == '?' :
    nexstar_port = input("Nexstar usb port : ")
    
logging.info("Nexstar port %s", nexstar_port)
logging.info("Start nexstar serial port")
scope = serial.Serial(nexstar_port)
set_time(scope,utc=utc,daylight=daylight)
nexstar_info(scope)
lat,long = get_location(scope)


#-------------------- Test du systèmes-------------------- 
logging.info("Start systeme test")

test_img = True
i=0 #numero de l'image test

while test_img :
    logging.info("Capture image test %s", i)
    t = get_time(scope)
    os.system("gphoto2 --port={} --filename=test{}.arw  --trigger-capture --wait-event-and-download=FILEADDED".format(port,i))
    
    rgb=img_read('test{}.arw'.format(i),print_img=True)

    continue_test = input("\nQue voulez vous faire ? \nAstrometrie (a) \nContinuer test (Y/n) ")
    
    if continue_test=='a' or continue_test =='A':
        logging.info("Astrometry of the image")
        f='test{}.arw'.format(i)
        fits.writeto(f[:-4]+'_b.fits',rgb[:,:,2],overwrite=True)
        c_img, fov = astromerty_img(sky_coord, ast, c_obj, 'test{}_b.fits'.format(i))

        continue_test = input("\nQue voulez vous faire ? \nSyncronisation telescope (s) \nCentrer le telescope (m) \nContinuer test (Y/n) ")

        if continue_test == "m" or continue_test == "M":
            logging.info("move the telescope to the right position")
            nexstar_obj_centering(scope,c_obj,c_img,t, lat,long)
            continue_test = input("\nQue voulez vous faire ? \nContinuer test (Y/n) ")
    
        if continue_test=='s' or continue_test == 'S' :
            logging.info("Sync mount with last coord obtened by astrometry")
            print("Syncronisation du telescope avec les derniere coordonnes obtenue par astrometrie")
            sync_precise_ra_dec(scope,c_img.ra.deg,c_img.dec.deg)
            continue_test = input("\nQue voulez vous faire ? \nContinuer test (Y/n) ")

    if continue_test == "N" or continue_test == "n" :
        logging.info("End of systeme test")
        test_img = False

    i+=1

#-------------------- Capture des images --------------------
logging.info("Start image capture")
capt  = True
centering = False

while capt : 
    if image_nbr == 0 :
        image_nbr = int(input('Combien de photo à prendre ? '))
    logging.info("Number of image you want : %s", image_nbr)

    if name == '?' :
        name = input('Quel est le nom des images ? ')
    logging.info("Object name : %s", name)
    
    for i in range(image_nbr):
        logging.info("Capture image %s", i)
        t = get_time(scope)
        os.system(f"gphoto2 --port={port} --filename={name}_{str(i)}.arw  --trigger-capture --wait-event-and-download=FILEADDED")
        
        if check_img != 0 and i % check_img == 0 and i!=0:
            centering = True
            i_center = 1
        
        if centering :
            if i_center > nexstar_max_test  :
                print("Error in centering, make it manualy")
                logging.error("Error in centering, make it manualy")
                logging.info('End of the programm')
                print("End of the programm")
                goto_precise_azm_alt(scope, 0,0)
                exit()
            logging.info("Check image coordinates")
            f=name+'_'+str(i)+'.arw'
            rgb = img_read(f)
            logging.info("convert into fits file")
            fits.writeto(f[:-4]+'_b.fits',rgb[:,:,2],overwrite=True)
            c_img, fov = astromerty_img(sky_coord, ast, c_obj, f[:-4]+'_b.fits')
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

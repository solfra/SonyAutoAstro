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
from AAnexstar import *
import serial
import time
from urllib.request import urlopen
import logging

#--------------------- Fonction utiles-------------------- 
def img_read(file):
    '''
    Read and print a raw image from Sony camera

    Input : 
    file (str) : name of the file to read

    Output :
    rgb (3d array) : image array
    '''
    logging.info("read image")
    raw = rawpy.imread(file)
    rgb = raw.postprocess(use_camera_wb=True)
    raw.close()
    logging.info("print image")
    plt.imshow(rgb)
    plt.show()
    return rgb

def astrometry(file,ast):
    '''
    Compute astrometry for an image (fits)
    Note this result can also been view online on nova.astrometry.net

    Input :
    file = name of the image 
    ast = AstrometryNet()

    Output :
    wcs_header = result of the astrometry
    '''
    try_again = True
    submission_id = None
    while try_again:
        try:
            if not submission_id:
                print('submission')
                wcs_header = ast.solve_from_image(file,force_image_upload = True, submission_id=submission_id)
            else:
                wcs_header = ast.monitor_submission(submission_id,solve_timeout=120)

        except TimeoutError as e:
            submission_id = e.args[1]
        else:
            # got a result, so terminate
            try_again = False
    return wcs_header

def get_coord(astrom) :
    '''
    Print and return coordone from the astrometry results in format hms / dms

    Input :
    astrom = astrometry wcs header

    Output :
    ra, dec = CRVAL 1 and 2 from wcs header
    '''
    ra=astrom['CRVAL1']
    dec=astrom['CRVAL2']
    c= SkyCoord(ra*u.degree,dec*u.degree)
    print('RA =',c.ra.hms[0],'h',c.ra.hms[1],'min',c.ra.hms[2],'s','\nDEC =',c.dec.dms[0],'deg',c.dec.dms[1],'min',c.dec.dms[2],'sec')
    logging.info("coord center image : ra : %s ; dec : %s", ra, dec)
    return ra, dec

def simbad_query(ra, dec, fov = 0.44) :
    '''
    Query simbad around ra, dec for giving object of NGC cataloge in the field of view of the camera

    Input :
    ra, dec = CRVAL 1 and 2 from wcs header
    fov = field of view of the camera (in degree)

    Output :
    NaN
    '''
    minRA = ra-fov
    maxRA = ra+fov
    minDEC = dec-fov
    maxDEC = dec+fov
    result = Simbad.query_criteria('ra>'+str(minRA)+'&ra<'+str(maxRA)+'&dec>'+str(minDEC)+'&dec<'+str(maxDEC),cat='NGC')
    print(result)

def cfg_check(file='AA.cfg'):
    config = configparser.ConfigParser()
    try :
        config.read(file)
        int(config['sky_object']['nbrPict'])
        key = config['astrometry']['user']
        keyring.get_password('astroquery:astrometry_net', key)
        int(config['astrometry']['check_every_x_imgs'])
    except :
        print("Error in config file")
        logging.error("Error in config file")
        exit()
    else :
        print("Config file OK")
        logging.info("config file ok")

def get_fov(header):
    """
    Get the fov of an image with is header of is plate solve

    Input :
    header : the fits header of the plate solve from astrometry.net   

    Output : 
    FOV in arcmin (tupple)
    """
    com = header['COMMENT']
    for i in range(len(com)) :
        l = com[-i].split(" ")
        if l[0] == 'scale:' :
            pixScal = float(l[1])
            break
    return (header['IMAGEW']*pixScal*60,header['IMAGEH']*pixScal*60)

def internet_verif():
    try :
        urlopen('https://www.google.com')
        print("internet is OK")
        logging.info("Internet is ok")
    except :
        print('Error ! Internet not conected !!!!!!!!!!!!!!!!')
        logging.error("Internet not conected")

def astromerty_img(config, ast, c_obj, fits_file):
    result_ast=astrometry(fits_file,ast)
    fits.writeto('heder_result.fits', [], result_ast,overwrite=True)
    ra, dec = get_coord(result_ast)
    fov = get_fov(result_ast)

    if config['sky_object']['get_coord'] == 'y' or config['sky_object']['get_coord'] == 'Y' :
        c_img = SkyCoord(ra*u.deg,dec*u.deg)
        sep = c_img.separation(c_obj)
        print("Separation obj image :",sep.arcmin,"arcmin")
        logging.info("Separation obj image : %s arcmin",sep.arcmin)
        print("Plus precisement :",(c_obj.ra.deg - c_img.ra.deg)*60, "arcmin en RA et", (c_obj.dec.deg - c_img.dec.deg)*60,"arcmin en DEC")
        if sep > max(fov) :
            print("Cible hors champ !")
            print("Objects dans le champ actuel : ")
            simbad_query(ra,dec,fov=max(fov)*60)
    else :
        print("Objects dans le champ actuel : ")
        simbad_query(ra,dec,fov=max(fov)*60)
    return c_img

def nexstar_info(scope):
    """
    Print the information of the nexstar telescope

    Input :
    scope : the serial object of the telescope

    Output :
    None, just print information
    """
    print("tracking mode :", get_tracking(scope))
    print("align mode", get_align(scope))
    print("telescope time", get_time(scope,print_offset=True))
    print("telescope localisation", get_location(scope))
    print("position ALT/AZ", get_AZM_ALT_precise(scope))
    print("position RA/DEC", get_RA_DEC_precise(scope))

def nexstar_obj_centering(scope,ra_obj,dec_obj):
    ra_scope, dec_scope = get_RA_DEC_precise(scope)
    c_obj = SkyCoord(ra_obj*u.deg, dec_obj*u.deg)
    c_scope = SkyCoord(ra_scope*u.deg,dec_scope*u.deg)
    if c_obj.separation(c_scope).deg > 7 :
        goto_precise_ra_dec(scope,ra_obj,dec_obj)
    else :
        print("mv scope")
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
from astropy.coordinates import EarthLocation,SkyCoord
from astropy.time import Time
from astropy.coordinates import AltAz

#--------------------- Fonction -------------------- 

def img_read(file):
    '''
    Read and print a raw image from Sony camera

    Input : 
    file (str) = name of the file to read

    Output :
    rgb (3d array) = image array
    '''
    logging.info("read image")
    print("read image")
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
    logging.info("Submission to nova.astrometry.net")
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
    """
    Check the config file is ok

    Input :
    file = the config file

    Output :
    None, just print the result and writ it in the log file
    """
    config = configparser.ConfigParser()
    try :
        config.read(file)
        int(config['sky_object']['nbrPict'])
        key = config['astrometry']['user']
        keyring.get_password('astroquery:astrometry_net', key)
        int(config['astrometry']['check_every_x_imgs'])
        int(config['nexstar']['max_test'])
        int(config['nexstar']['daylight'])
        int(config['nexstar']['UTC'])
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
    header = the fits header of the plate solve from astrometry.net   

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
    """
    Verify you have an internet connection, print the result and writ in log file

    Input : Nothin
    Output : Nothing
    """
    try :
        urlopen('https://www.google.com')
        print("internet is OK")
        logging.info("Internet is ok")
    except :
        print('Error ! Internet not conected !!!!!!!!!!!!!!!!')
        logging.error("Internet not conected")

def astromerty_img(config, ast, c_obj, fits_file):
    """
    Get the astrometry of an image and make some calculation

    Input :
    config = the config file object
    ast = the astrometry object
    c_obj = the coordinates of the object (astropy.coordinates.Skycoord format)
    fits_file = the name of the file you want to analyse

    Output :
    c_img = coordinate of the image (astropy.coordinates.Skycoord format)
    """
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
        if sep.arcmin > max(fov) :
            print("Cible hors champ !")
            #print("Objects dans le champ actuel : ")
            #simbad_query(ra,dec,fov=max(fov)*60)
    else :
        print("Check astrometry result for knowing the object in your image")
        #simbad_query(ra,dec,fov=max(fov)*60)
    return c_img, fov

def astromerty_img2(config, ast, c_obj, fits_file,solver="astrometry"):
    """
    Get the astrometry of an image and make some calculation

    Input :
    config = the config file object
    ast = the astrometry object
    c_obj = the coordinates of the object (astropy.coordinates.Skycoord format)
    fits_file = the name of the file you want to analyse
    solver = astrometry (with internet) or astap (in local)

    Output :
    c_img = coordinate of the image (astropy.coordinates.Skycoord format)
    """
    if solver == "astrometry" :
        result_ast=astrometry(fits_file,ast)
        fits.writeto('heder_result.fits', [], result_ast,overwrite=True)
        ra, dec = get_coord(result_ast)
        fov = get_fov(result_ast)
    elif solver == "astap" :
        print(c_obj)
        os.system("astap -f "+ fits_file + " -ra " + str(c_obj.ra.hourangle) + " -spd " + str(c_obj.dec.deg+90)+ " -wcs")
        try :
            res = fits.open(fits_file[:-5]+".wcs")
        except :
            print("no astrometry solution")
            exit()
        result_ast = res[0].header 
        ra, dec = get_coord(result_ast)
        fov = (result_ast["CDELT2"]*60*5000,result_ast["CDELT2"]*60*3000) #a revoir, faut multiplier par le vrai nbr de pixel du capteur 
        
    if config['sky_object']['get_coord'] == 'y' or config['sky_object']['get_coord'] == 'Y' :
        c_img = SkyCoord(ra*u.deg,dec*u.deg)
        sep = c_img.separation(c_obj)
        print("Separation obj image :",sep.arcmin,"arcmin")
        logging.info("Separation obj image : %s arcmin",sep.arcmin)
        print("Plus precisement :",(c_obj.ra.deg - c_img.ra.deg)*60, "arcmin en RA et", (c_obj.dec.deg - c_img.dec.deg)*60,"arcmin en DEC")
        print(sep, fov)
        if sep.arcmin > max(fov) :
            print("Cible hors champ !")
            #print("Objects dans le champ actuel : ")
            #simbad_query(ra,dec,fov=max(fov)*60)
    else :
        print("Check astrometry result for knowing the object in your image")
        #simbad_query(ra,dec,fov=max(fov)*60)
    return c_img, fov

def nexstar_info(scope):
    """
    Print the information of the nexstar telescope

    Input :
    scope = the serial object of the telescope

    Output :
    None, just print information
    """
    print("tracking mode :", get_tracking(scope))
    print("align mode", get_align(scope))
    print("telescope time", get_time(scope,print_offset=True))
    print("telescope localisation", get_location(scope))
    print("position ALT/AZ", get_AZM_ALT_precise(scope))
    print("position RA/DEC", get_RA_DEC_precise(scope))

def nexstar_obj_centering(scope,c_obj, c_img,t, lat, long):
    """
    Centering the nexstar telescope to the right coordinates

    Input :
    scope = the serial object of the telescope
    c_obj = coordinates of the object (astropy.coordinates.Skycoord format)
    c_img = coordinates of the image (astropy.coordinates.Skycoord format)
    t = the time at witch you take the picture, need to be in UTC time. Format = aaaa-mm-dd hh:mm:ss
    lat, long = latitude and longitude of your earth position

    Output :
    Nothing, just mouve the telescope, print some value and write it in log file
    """
    ra_scope, dec_scope = get_RA_DEC_precise(scope)
    c_scope = SkyCoord(ra_scope*u.deg,dec_scope*u.deg)
    if c_obj.separation(c_scope).deg > 7 :
        goto_precise_ra_dec(scope,c_obj.ra.deg,c_obj.dec.deg)
        logging.info("Go to the object position")
        print("Go to the object position")
    else :
        print("Calculation of the necessary diasplacement")
        logging.info("Set observatory position in space and time")
        observing_location = EarthLocation(lat=lat, lon=long, height=250*u.m)  
        observing_time = Time(t)  
        aa = AltAz(location=observing_location, obstime=observing_time)

        logging.info("Transform object coordinates RA/DEC into AZ/ALT")
        c_obj_altAz = c_obj.transform_to(aa)
        az_obj = c_obj_altAz.az.arcsec
        alt_obj = c_obj_altAz.alt.arcsec

        logging.info("Transform image coordinates RA/DEC into AZ/ALT")
        c_img_altAz = c_img.transform_to(aa)
        az_img = c_img_altAz.az.arcsec
        alt_img = c_img_altAz.alt.arcsec

        logging.info("Calculation of the necessary diasplacement")
        az_mvt = az_obj-az_img
        alt_mvt = alt_obj - alt_img
        print("Need to mouve", az_mvt, "arcsec in az and", alt_mvt, "arcsec in alt")
        logging.info("movement required in az : %s arcsec", az_mvt)
        logging.info("movement required in alt : %s arcsec", alt_mvt)

        logging.info("Move the telescope in az")
        if az_mvt < 0 :
            d = "neg"
        else :
            d = "pos"
        mouv_telescope_variable(scope, ["AZ",d], az_mvt)

        logging.info("Move the telescope in alt")
        if alt_mvt < 0 :
            d="neg"
        else :
            d="pos"
        mouv_telescope_variable(scope, ["ALT",d],alt_mvt)
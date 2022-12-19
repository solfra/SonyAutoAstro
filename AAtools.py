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

ast = AstrometryNet()
ast.api_key = keyring.get_password('astroquery:astrometry_net', 'solfra38') # This API key must be changed

#--------------------- Fonction utiles-------------------- 
def img_read(file):
    '''
    Read and print a raw image from Sony camera

    input : 
    file (str) : name of the file to read

    output :
    rgb (3d array) : image array
    '''
    raw = rawpy.imread(file)
    rgb = raw.postprocess(use_camera_wb=True)
    raw.close()
    plt.imshow(rgb)
    plt.show()
    return rgb

def astrometry(file):
    try_again = True
    submission_id = None
    while try_again:
        try:
            if not submission_id:
                print('submission')
                wcs_header = ast.solve_from_image(file,submission_id=submission_id)
            else:
                wcs_header = ast.monitor_submission(submission_id,solve_timeout=120)
                i+=1
                print(i)

        except TimeoutError as e:
            submission_id = e.args[1]
        else:
            # got a result, so terminate
            try_again = False
    return wcs_header

def get_coord(astrom) :
    ra=astrom['CRVAL1']
    dec=astrom['CRVAL2']
    c= SkyCoord(ra*u.degree,dec*u.degree)
    print('RA =',c.ra.hms[0],'h',c.ra.hms[1],'min',c.ra.hms[2],'s','\nDEC =',c.dec.dms[0],'deg',c.dec.dms[1],'min',c.dec.dms[2],'sec')
    return ra, dec

def simbad_query(ra, dec, fov = 0.44) :
    minRA = ra-fov
    maxRA = ra+fov
    minDEC = dec-fov
    maxDEC = dec+fov
    result = Simbad.query_criteria('ra>'+str(minRA)+'&ra<'+str(maxRA)+'&dec>'+str(minDEC)+'&dec<'+str(maxDEC),cat='NGC')
    print(result)
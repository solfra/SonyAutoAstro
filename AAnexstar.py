import serial
import time

def get_align(scope) :
    """
    Get the alignement of the scope
    return 0 if not aligne and  if aligned

    input :
    scope : the serial object of the telescope

    return :
    result : the response of the mount
    """
    c='J'
    scope.write(c.encode())
    result=scope.read(2).decode("utf-8")
    return ord(result[0])

def get_AZM_ALT(scope):
    """
    Get the altitude and azimut of the telescope in degrees

    input :
    scope : the serial object of the telescope

    return :
    azm : azimut in degree
    alt : altitude in degree
    """

    c="Z" #Get AZM-ALT
    scope.write(c.encode())
    result=scope.read(10).decode("utf-8")
    d = result.split(',')
    azm=int(d[0], 16)/65536*360
    alt=int(d[1][:-1], 16)/65536*360
    return azm,alt

def get_RA_DEC(scope):
    """
    Get the RA and DEC of the telescope in degrees

    input :
    scope : the serial object of the telescope

    return :
    ra : ra in degree
    dec : dec in degree
    """
    align = get_align(scope)
    if align == 0 :
        print("Error, telescope not aligned")
        return None
    elif align == 1 :
        c="E" #Get RA / dec
        scope.write(c.encode())
        result=scope.read(10).decode("utf-8")
        d = result.split(',')
        ra=int(d[0], 16)/65536*360
        dec=int(d[1][:-1], 16)/65536*360
        return ra,dec

def get_AZM_ALT_precise(scope):
    """
    Get the precise altitude and azimut of the telescope in degrees

    input :
    scope : the serial object of the telescope

    return :
    azm : azimut in degree
    alt : altitude in degree
    """

    c="z" #Get AZM-ALT
    scope.write(c.encode())
    result=scope.read(18).decode("utf-8")
    d = result.split(',')
    azm=int(d[0], 16)/4294967296*360
    alt=int(d[1][:-1], 16)/4294967296*360
    return azm,alt

def get_RA_DEC_precise(scope):
    """
    Get the precise ra and dec of the telescope in degrees

    input :
    scope : the serial object of the telescope

    return :
    ra : ra in degree
    dec : dec in degree
    """
    align = get_align(scope)
    if align == 0 :
        print("Error, telescope not aligned")
        return None
    elif align == 1 :
        c="e" #RA dec
        scope.write(c.encode())
        result=scope.read(18).decode("utf-8")
        d = result.split(',')
        ra=int(d[0], 16)/4294967296*360
        dec=int(d[1][:-1], 16)/4294967296*360
        return ra,dec

def get_tracking(scope) :
    """
    Get the tracking mode of the telescope

    input :
    scope : the serial object of the telescope

    return :
    mode = the tracking mode (0=off, 1=al/az, 2=EQ N, 3=EQ S)
    """
    c="t"
    scope.write(c.encode())
    mode = scope.read(2).decode("utf-8")
    return ord(mode[0])

def modif_tracking(scope,track) :
    """
    Modification of the tracking mode of the telescope

    input :
    scope : the serial object of the telescope

    return :
    None, juste write mode
    """
    c="T"+chr(track)
    scope.write(c.encode())
    m=scope.read(1)

def mouv_telescope(scope, direction, rate, duration) :
    """
    Move the telescope along a specific direction, at a given speed, for a certain time.

    Input :
    scope : the serial object of the telescope
    direction (list) : a list for position and direction : [AZ/ALT , pos/neg]
    rate : rate betwint 1 and 9 (0 for off)
    duration : duartaion in s of the mvt

    Output :
    None, juste mouve the mount
    """
    if direction[0] == "AZ" :
        d=16
    elif direction[0] == "ALT" :
        d=17
    
    if direction[1] == "pos" :
        p=36
    elif direction[1] == "neg" :
        p=37
    
    track = get_tracking(scope)
    if track !=0 :
        com = 'T' + chr(0)
        scope.write(com.encode())
        m=scope.read(1)

    comande = "P" + chr(2) + chr(d) + chr(p) + chr(rate) + chr(0) +chr(0) + chr(0)
    scope.write(comande.encode())
    m=scope.read(1)
    time.sleep(duration)
    comande = "P" + chr(2) + chr(d) + chr(p) + chr(0) + chr(0) +chr(0) + chr(0) #stop le mvt
    scope.write(comande.encode())
    m=scope.read(1)
    com = "T" + chr(track)
    scope.write(com.encode())
    m=scope.read(1)

def mouv_telescope_variable(scope, direction, rate, duration=1) :
    """
    Move the telescope along a specific direction, at a given speed, for a certain time.

    Input :
    scope : the serial object of the telescope
    direction (list) : a list for position and direction : [AZ/ALT , pos/neg]
    rate : desired rate in arcsec
    duration (optional) : duartaion in s of the mvt, by defaut 1s

    Output :
    None, juste mouve the mount
    """
    if direction[0] == "AZ" :
        d=16
    elif direction[0] == "ALT" :
        d=17
    
    if direction[1] == "pos" :
        p=6
    elif direction[1] == "neg" :
        p=7
    
    rateH = (rate*4)//256
    rateL = (rate*8)%256

    track = get_tracking(scope)
    if track !=0 :
        com = 'T' + chr(0)
        scope.write(com.encode())
        m=scope.read(1)

    comande = "P" + chr(3) + chr(d) + chr(p) + chr(rateH) + chr(rateL) +chr(0) + chr(0)
    scope.write(comande.encode())
    m=scope.read(1)
    time.sleep(duration)
    comande = "P" + chr(3) + chr(d) + chr(p) + chr(0) + chr(0) +chr(0) + chr(0) #stop le mvt
    scope.write(comande.encode())
    m=scope.read(1)
    com = "T" + chr(track)
    scope.write(com.encode())
    m=scope.read(1)

def get_time(scope,print_offset=False) :
    """
    Get time of the telescope

    Input :
    scope : the serial object of the telescop
    print_offset (optional, True or False) : an option to allowd to print more information (UTC time and daylight)

    Output :
    t : Time in format AAAA-mm-dd hh:mm:ss 
    """
    c='h'
    scope.write(c.encode())
    result=scope.read(9).decode("utf-8")
    t = '20'+str(ord(result[5]))+'-'+str(ord(result[3]))+'-'+str(ord(result[4]))+' '+str(ord(result[0]))+':'+str(ord(result[1]))+':'+str(ord(result[2]))
    if print_offset :
        print("utc+",str(ord(result[6])))
        print("Heure ete ? ",str(ord(result[7])))
    return t

def get_location(scope) :
    """
    Get GPS position of the telescope

    Input :
    scope : the serial object of the telescop

    Output : 
    lat : latitude in format +/- ..d..m..s
    long : longituide in format +/- ..d..m..s
    """
    c='w'
    scope.write(c.encode())
    result=scope.read(9).decode("utf-8")
    if ord(result[3]) == 0 :
        posLat = "+"
    elif ord(result[3]) == 1 :
        posLat = '-'
    if ord(result[7]) == 0 :
        posLong = "+"
    elif ord(result[7]) == 1 :
        posLong = '-'
    lat = posLat+str(ord(result[0]))+"d"+str(ord(result[1]))+"m"+str(ord(result[2]))+"s"
    long = posLong+str(ord(result[4]))+"d"+str(ord(result[5]))+"m"+str(ord(result[6]))+"s"
    return lat,long

#def sync_precise_ra_dec(scope):

#def goto_precise_azm_alt(scope) :

#def goto_precise_ra_dec(scope) :

#def set_location(scope) :

#def set_time(scope) :


#scope = serial.Serial("/dev/ttyUSB0") #attention port peut changer !
#print(get_AZM_ALT(scope))
#print(get_AZM_ALT_precise(scope))
#print("mode", get_tracking(scope))
#modif_tracking(scope,1)
#mouv_telescope(scope, ["ALT","pos"],8,2)
#print(get_RA_DEC_precise(scope))
#print(get_AZM_ALT_precise(scope))
#mouv_telescope_variable(scope, ["ALT","pos"],550)
#print(get_time(scope,print_offset=True))
#print(get_location(scope))

# Test transformation RA/dec
#from astropy.coordinates import EarthLocation,SkyCoord
#from astropy.time import Time
#from astropy import units as u
#from astropy.coordinates import AltAz
#
#lat,long = get_location(scope)
#t = get_time(scope)
#ra,dec = get_RA_DEC_precise(scope)
#
#observing_location = EarthLocation(lat=lat, lon=long, height=250*u.m)  
#observing_time = Time(t)  
#aa = AltAz(location=observing_location, obstime=observing_time)
#
#coord = SkyCoord(ra, dec,unit="deg")
#print('coord th',coord)
#print('Al/az transform of coord',coord.transform_to(aa))
#print('scope coord Al/az', get_AZM_ALT_precise(scope))
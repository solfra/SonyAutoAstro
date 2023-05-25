import configparser

config = configparser.ConfigParser()

config['gphoto'] = {}
config['gphoto']['port'] = '?'

config['astrometry'] = {}
config['astrometry']['user'] = "solfra38"
config['astrometry']['check_every_x_imgs'] = "0"

config['sky_object'] = {}
config['sky_object']['name'] = '?'
config['sky_object']['nbrPict'] = '0'
config['sky_object']['get_coord'] = 'n'

config['nexstar'] = {}
config['nexstar']['port'] = '?'
config['nexstar']['max_test'] = '5'
config['nexstar']['UTC'] = '1'
config['nexstar']['daylight'] = '0'

with open('AA.cfg', 'w') as configfile:
  config.write(configfile)

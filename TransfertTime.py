import time
import os
import numpy as np
import logging

logging.basicConfig(filename="TransfertTime.log", filemode='w', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

os.system("gphoto2 --list-ports")
os.system("gphoto2 --auto-detect ")
os.system("gphoto2 --summary")

port = input("Entrer le nom du port USB a utiliser pour l'appareil photo : ")
logging.info('using %s', port)

logging.info('Start 15 capture')
nbr = 15
name = 'tt'
res = []

for i in range(nbr):
    logging.info('capture image')
    d = time.time()
    os.system("gphoto2 --port={} --filename={}.arw  --trigger-capture --wait-event-and-download=FILEADDED".format(port,name+str(i)))
    res.append(time.time()-d)

logging.info('End of captures') 
print('\n**************\nFin des captures')
print(res)
t_mean = np.mean(np.array(res))
print('Mean capture time : ',t_mean)
logging.info('temps moyen de capture : %s s ',t_mean)
print('deviation du temps de capture : ',np.std(np.array(res)))

os.system("rm -r tt*")
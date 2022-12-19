import time
import os
import numpy as np

os.system("gphoto2 --list-ports")
os.system("gphoto2 --auto-detect ")
os.system("gphoto2 --summary")

port = input("Entrer le nom du port USB a utiliser pour l'appareil photo : ")

nbr = 15
name = 'tt'
res = []

for i in range(nbr):
    d = time.time()
    os.system("gphoto2 --port={} --filename={}.arw  --capture-image-and-download".format(port,name+str(i)))
    res.append(time.time()-d)
    
print('\n**************\nFin des captures')
print(res)
print('temps moyen de capture : ',np.mean(np.array(res)))
print('deviation du temps de capture : ',np.std(np.array(res)))

os.system("rm -r tt*")
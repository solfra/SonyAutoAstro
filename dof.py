import os

os.system("gphoto2 --list-ports")
os.system("gphoto2 --auto-detect ")
os.system("gphoto2 --summary")

port = input("Entrer le nom du port USB a utiliser pour l'appareil photo : ")

nbr = int(input('Combien de photo à prendre ? '))
name = input('Quel est le nom des images ? ')

for i in range(nbr):
    os.system("gphoto2 --port={} --filename={}.arw  --capture-image-and-download".format(port,name+str(i)))

print('\n**************\nFin des captures')
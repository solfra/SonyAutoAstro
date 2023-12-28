Application
===========

* AutoAstro.py : Main software. Make series of picture and saves in the curent directory, check astrometry position.

* AutoAstro_nexstar.py : Same as AutoAstropy but also control nexstar telescope.
  
* TrandfertTime.py : caracterise the time until gphoto save image in your folder.

* fits_write.py read and save r, g, b layer of a specific image.


AutoAstro and AutoAstro_nexstar
*******************************
The software guides you to establish the connection with the camera. 
Then, it proposes to make some tests to check the exposure parameters (adjustment to be made on the camera) 
and the position of the telescope (with astrometry). and the position of the telescope (with astrometry). 
Finally, the software makes a series of images, with a periodic verification of the position of the telescope. 
If AutoAstro_nexstar, the software also recenters the telescope when checking the position to always have the right position.

A log file is available to keep track of the operation of the software during the night of acquisition.

Check before run
----------------
Before run the software, check the Before use part.

An internet connection is required for using astrometry and simbad query.
Check also you are in the right folder for write your picture and you have free space on your disk.
The AA.cfg file must be in this folder and must be completed.

Your camera must be in raw mode and in usb pc remote control mode.

If AutoAstro_nexstar, your telescope must be aligned.

AA.cfg config file
------------------

This configuration file is useful to improve the productivity and automation of your installation. 
If you don't know the value used, leave the default values so that the software will ask you for them.
This configuration file must be located in the folder where you run AutoAstro.py!

The config file is define as folow :

gphoto :

* port = the usb port used by the camera

astrometry :

* user = the user name define with keyring for astrometry tools (see Astrometry API key part for more information)

* check_every_x_imgs = how often the software should check the position by astrometry. 0 means no verification

sky_object :

* name = name of the objects you observe. This field must not contain space character

* nbrpict = the number of photos you want to take

* get_coord = (y/n) get the coordinate of your target by a simbad quering. If yes, the name field must be a valid object name

nexstar (optional part) : 

* port = the usb port used by the telescope

* max_test = the number max of centering test. If centering not corect after this number of test, the programm return an error, the telescope go to 0,0 alt/az position and the programm exit

* utc = your offset from the utc time

* daylight = 1 to enable Daylight Savings and 0 for Standard Time


Initialisation
--------------

At the beginning, the software checks some information.

* Check if your config file is OK

* Verification of an internet connection (required by astrometry and for a simbad request)

* Connection to astrometry using your api key

* gphoto2 initialisation. At this moment the software tel you which port using for control your camera if the information is not in AA.cfg

* Get the coordinate of your object (obteined by a simbad query)

* (optional) nexstar initialisation. At this moment the software tel you which port using for control your telescope if the information is not in AA.cfg. Also activate the serial port, adjust the date and time of your telescope and print some control information.

Test
----

The first part of the software is the test part.
The software captures an image, downloads it and asks you if you want to do an astrometry or a re-capture. 
The files are saved under the name test{}.arw

If you want to change the shooting parameters, you must make the settings directly on the camera.

If you make an astrometry, the result is available on https://nova.astrometry.net/dashboard/submissions . 
The software also displays the ra,dec coordinates of your image and the ngc object in your fov (found by a simbad query).
If nexstar, you can also synchronize your telescope with these coordinates.

When everything is in order, you can exit the test loop and move on to the main loop.

Main
----

This part is the main loop. The software take the number of photo you want. 
Is define in AA.cfg, the software also make a periodic astrometry of your image and refocuses your telescope if AutoAstro_nexstar and if necessary.

You have to define the number of images and their name if it is not the case in AA.cfg.


TransfertTime
*************

This little script captures 15 images and estimates how long it will take your computer to transfer the capture.  
For a good approximation, take your camera at the fastest possible speed.
All tested images are deleted at the end.

FitsWrite
***********

This program reads an image and saves each rgb layer in a single fits file.

# Sony Auto Astro

Sony Auto astro is a powrful software for controle and use Sony camera in astronomy and, in option, control a Celestron nexstar telescope.

Whith this software, you can controle a Sony camera, make astrometry of your images, calculate the the deviation between your image and the position of the desired object.

You can also controle a nexstar SE telescope (alt/az configuration). This part is optional.

# Requirement 
- gphoto 
- astrometry.net api key
- python 3.
- rawpy ; keyring ; astroquery ; astropy ; numpy ; maplotlib 

# Use

Read the documenation for more information

## Before use :

- For begging, you need to be able to controle your camera whith gphoto, throught an usb cable.   
- You need to configue AA.cfg

## AutoAstro and AutoAstro_nexstar

The software guides you to establish the connection with the camera. 
Then, it proposes to make some tests to check the exposure parameters (adjustment to be made on the camera) 
and the position of the telescope (with astrometry). and the position of the telescope (with astrometry). 
Finally, the software makes a series of images, with a periodic verification of the position of the telescope. 
If AutoAstro_nexstar, the software also recenters the telescope when checking the position to always have the right position.

A log file is available to keep track of the operation of the software during the night of acquisition.

# Future improvement :
- Adding graphic interface
- Check collimation
- Check focus
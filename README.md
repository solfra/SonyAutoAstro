# Sony Auto Astro

Sony Auto astro is  a powrful softare for controle and use Sony camera in astronomy.

# Requirement 
- gphoto 
- astrometry.net api key
- python 3.
- rawpy ; keyring ; astroquery ; astropy ; numpy ; maplotlib

# Use
## Before use :

- For begging, you need to be able to controle your camera whith gphoto, throught an usb cable.   
- You need to change the api key for astrometry in AutoAstro.py. Procedure for that is explian here : https://astroquery.readthedocs.io/en/latest/astrometry_net/astrometry_net.html#using-keyring-to-store-api-key 

## Application :

Run AutoAstro.py .   
The software guide you for inisialise link whith camera. After that, propose to make some test for checking exposition parameter (adjustment to be made on the camera) and telescope position (with astrometry). Until it is done, software realise a series of pictures. All pictures are saves in the curent directory.     

If you want to caracterise the time until gphoto save image in your folder, you can run TrandfertTime.py.

If you want to read and save r, g, b layer of a specific image, you can run fits_write.py.

# Future improvement :
- Adding graphic interface
- Control Celestron Nexstar telescope (realignment every x images)
- Check collimation
- Check focus
Before use
==========

Because Sony Auto Astro uses other software, it is necessary to install these tools.

Gphoto
******
Gphoto is a powerfull linux softawre designed to control camera. This software is essential for SonyAutoAstro.

Install with :

.. code-block::
    
    sudo apt-get update
    sudo apt-get install libusb-1.0-0-dev libtool libgphoto2-6 gphoto2

Now, on your camera, change the usb mode into remote computer.

You can check if gphoto2 works with :

.. code-block::

    gphoto2 --list-ports
    gphoto2 --auto-detect 
    gphoto2 --summary

Astrometry API key
******************

You need to have an api key for nova.astrometry.net. This is essential for SonyAutoAstro.
To obtain this api key, create an account on https://nova.astrometry.net/. Your api key is available in your profil page.

On a python consol, run the folowing comand :

.. code-block::

    import keyring
    keyring.set_password('astroquery:astrometry_net', None, 'apikeyhere')

Change None to another name to assign a user name to this key and use these user names in AA.cfg, in user in the Astrometry category.

See here for more details : https://astroquery.readthedocs.io/en/latest/astrometry_net/astrometry_net.html#using-keyring-to-store-api-key 
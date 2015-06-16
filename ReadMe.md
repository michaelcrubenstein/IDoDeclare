README
==============================
PyDico is a python and Django implementation of a project initially conceived at
Hack4Congress in Cambridge, MA. With PyDico, users can create accounts and identify 
issues that they are interested in seeing action by their members of Congress.

The User dashboard currently identifies the members of Congress for a user based on 
their street address and zip code.

A complete list of features is maintained in docs/features.html. A list of tasks to be 
completed is maintained in doc/tasks.txt.

============================================================
Installation Instructions
==============================
1. BUILD INSTRUCTIONS FOR PYTHON
	Create tmp folder next to website folder
	Upload Python-3.4.2 gz tar file into temp folder
	Extract the files from the tar archive
		$ tar -xf Python-3.4.2.tar
	Go to the python directory
		$ cd ../Python-3.4.2
	Make the target directory
		$ mkdir $HOME/opt
		$ mkdir $HOME/opt/python-3.4.2
	Run the commands to build python
		$ ./configure --prefix=$HOME/opt/python-3.4.2
		$ make
		$ make install
	More instructions at http://wiki.dreamhost.com/Python

2. Add "export PATH=$HOME/opt/python-3.4.2/bin:$PATH" to .bash_profile and .bashrc

3. Load all of the modules:
pip3 install django
pip3 install sunlight
pip3 install mysql-connector-python --allow-external mysql-connector-python
pip3 install pillow
pip3 install pygeocoder
	3f. Downloaded and installed mysql-connector-python-2.0.3-osx10.9.dmg
	3g. Moved the mysql site-package from the python2.7 site-packages 
			(Macintosh HD:Library:Python:2.7:site-packages) 
			to the python3.4 site-packages
			(Macintosh HD:Library:Frameworks:Python.Framework:Versions:3.4:lib:python3.4:site-packages).
	
	3f. Temporarily: pip3 install --upgrade git+https://github.com/multiplay/mysql-connector-python	
4. Download all files from PyDico
4. Open a terminal window
5. Navigate to the folder in the terminal window
6. Update the custom_user/settings file with the correct database information for the
	default database.
7. Make the public/static directory in idodeclare.org - mkdir public/static
	7a. mkdir public/static/admin
	    mkdir public/static/admin/css
	    mkdir public/static/admin/img
	    mkdir public/static/admin/img/gis
	    mkdir public/static/admin/js
	    mkdir public/static/admin/js/admin
	    cp $SITE_PACKAGES_PATH/django/contrib/admin/static/admin/css/* public/static/admin/css/
	    cp $SITE_PACKAGES_PATH/django/contrib/admin/static/admin/img/* public/static/admin/img/
	    cp $SITE_PACKAGES_PATH/django/contrib/admin/static/admin/img/gis/* public/static/admin/img/gis/
	    cp $SITE_PACKAGES_PATH/django/contrib/admin/static/admin/js/* public/static/admin/js/
	    cp $SITE_PACKAGES_PATH/django/contrib/admin/static/admin/js/admin/* public/static/admin/js/admin/
        	    
	7b. mkdir public/static/dico
        cp custom_user/static/dico/*.json public/static/dico
        
8. Move all of the files from 

If running on a local Mac
9. Execute the command: python3 manage.py migrate --database=dbname
10. Execute the command: python3 manage.py runserver
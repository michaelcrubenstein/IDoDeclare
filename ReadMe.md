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
1. Make sure all of the python environment is loaded:
	1a. Downloaded and installed mysql-connector-python-2.0.3-osx10.9.dmg
	1b. Moved the mysql site-package from the python2.7 site-packages to the 
		python3.4 site-packages.
	1c. Install django - pip3 install django
    1d. Install the sunlight package - pip3 install sunlight
    1e. Install mysql-connector-python - pip3 install mysql-connector-python --allow-external mysql-connector-python
    1f. Install pillow - pip3 install pillow
    1g. Install pygeocoder - pip3 install pygeocoder
    1g. Add "export PATH=$HOME/opt/python-3.4.2/bin:$PATH" to .bash_profile and .bashrc
2. Download all files from PyDico
3. Open a terminal window
4. Navigate to the folder in the terminal window
5. Update the custom_user/settings file with the correct database information for the
	default database.
6. Make the public/static directory in idodeclare.org - mkdir public/static
	6a. mkdir public/static/admin
	    mkdir public/static/admin/css
	    mkdir public/static/admin/img
	    mkdir public/static/admin/img/gis
	    mkdir public/static/admin/js
	    mkdir public/static/admin/js/admin
	    cp env/lib/python3.4/site-packages/django/contrib/admin/static/admin/css/* public/static/admin/css/
	    cp env/lib/python3.4/site-packages/django/contrib/admin/static/admin/img/* public/static/admin/img/
	    cp env/lib/python3.4/site-packages/django/contrib/admin/static/admin/img/gis/* public/static/admin/img/gis/
	    cp env/lib/python3.4/site-packages/django/contrib/admin/static/admin/js/* public/static/admin/js/
	    cp env/lib/python3.4/site-packages/django/contrib/admin/static/admin/js/admin/* public/static/admin/js/admin/
        	    
	6b. mkdir public/static/dico
        cp custom_user/static/dico/*.json public/static/dico
        
7. Move all of the files from 
6. Execute the command: python3 manage.py migrate --database=dbname
7. Execute the command: python3 manage.py runserver
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
1. Download all files from PyDico
2. Open a terminal window
3. Navigate the the folder in the terminal window
4. Execute the command: python3 manage.py migrate
5. Execute the command: python3 manage.py runserver
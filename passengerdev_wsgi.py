import sys, os
import traceback
import datetime

cwd = os.getcwd()
homed = os.environ['HOME']
bindirectory = homed + '/opt/python-3.4.2/bin'
libdirectory = homed + '/opt/python-3.4.2/lib'
pythondirectory = libdirectory + '/python3.4'
sys.path.insert(0,bindirectory)
sys.path.insert(0,pythondirectory+'/site-packages/django')
sys.path.insert(0,pythondirectory+'/site-packages')
sys.path.insert(0,pythondirectory)
sys.path.insert(0,cwd + '/dico')  #You must add your project here
sys.path.insert(0,cwd + '/custom_user')  #You must add your project here
sys.path.append(cwd)

with open(cwd + '/passengerwsgi.log', 'a') as log:
    try:
        log.write("Running %s\n" % (sys.executable))
        log.write("Running at %s\n" % (datetime.datetime.now()))
        log.write("  Version %s\n" % (sys.version))
        log.write("  Path: %s\n" % (sys.path))
        log.flush()
    except Exception as e:
        log.write("  Exception: %s\n" % (e))
        log.write("%s\n" % traceback.format_exc())
        log.write("Running %s\n" % (sys.executable))
        log.write("  Version %s\n" % (sys.version))
        log.write("  Path: %s\n" % (sys.path))
        log.flush()

#Switch to new python
if sys.version < "3.4.2": os.execl(bindirectory+"/python3.4", bindirectory+"/python3.4", *sys.argv)

# os.environ['DJANGO_SETTINGS_MODULE'] = "custom_user.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "custom_user.settings")

# Set the API key for the sunlight API.
os.environ.setdefault("SUNLIGHT_API_KEY", 'f9defbcc52934ab38960bd1415ad3906')

try:
    import mysql.connector.django
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()

except Exception as e:
    with open(cwd + '/passengerwsgi.log', 'a') as log:
        log.write("Error: %s\n" % e)
        log.write("%s\n" % traceback.format_exc())
        log.flush()


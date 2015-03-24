import sys, os
import traceback

cwd = os.getcwd()
sys.path.insert(0,cwd+'/env/bin')
sys.path.insert(0,cwd+'/env/lib/python3.4/site-packages/django')
sys.path.insert(0,cwd+'/env/lib/python3.4/site-packages')
sys.path.insert(0,cwd+'/env/lib/python3.4')
sys.path.insert(0,cwd + '/dico')  #You must add your project here
sys.path.insert(0,cwd + '/custom_user')  #You must add your project here
sys.path.append(cwd)

try:
    log = open('/home/micrub9/idodeclare.org/passengerwsgi.log', 'a')
    log.write("Running %s\n" % (sys.executable))
    log.write("  Version %s\n" % (sys.version))
    log.write("  Path: %s\n" % (sys.path))
    log.flush()
except Exception as e:
    log.write("  Exception: %s\n" % (e))
    log.write("%s\n" % traceback.format_exc())
    log.flush()
    log = open('/home/micrub9/idodeclare.org/passengerwsgi.log', 'a')
    log.write("Running %s\n" % (sys.executable))
    log.write("  Version %s\n" % (sys.version))
    log.write("  Path: %s\n" % (sys.path))
    log.flush()

#Switch to new python
if sys.version < "3.4.2": os.execl(cwd+"/env/bin/python3.4", cwd+"/env/bin/python3.4", *sys.argv)

# os.environ['DJANGO_SETTINGS_MODULE'] = "custom_user.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "custom_user.settings")

# Set the API key for the sunlight API.
os.environ.setdefault("SUNLIGHT_API_KEY", 'f9defbcc52934ab38960bd1415ad3906')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()

except Exception as e:
    log = open('/home/micrub9/idodeclare.org/passengerwsgi.log', 'a')
    log.write("Error: %s\n" % e)
    log.write("%s\n" % traceback.format_exc())
    log.flush()


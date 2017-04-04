#!/usr/bin/env python2

'''
usage:
   mseries-dash <command> [options...] [<file>...]

Commands:
   import     import the contents of the specified files / paths
   stop       stop mseries-dash
   workon     Deploy mseries-dash without a new import but using data from a previously imported project
   read       Read new ftdc data into a currently running project
   ls         Lists the projects previously imported in the default directory (~/.mseries/)
   drop       Drops a specific project from mseries-dash directory
   help       the help
options:
   -p, --project=<project>  the project name [default: mseries]
   -h --help   Show this screen.
   --pool=<processes>     the number of processes in the pool, defaults to all [default: 4].
   -s, --sample=<sample>      the sample ratio, ie. 1 in <sample> [default: 10].
   -d --data <data>       Data directory where the data parsed is stored.
   -h --host <host>        Database instance to connect to. Defaults to localhost. [default: localhost]


See 'mseries-dash help <command>' for more information on a specific command.
'''

from docopt import docopt, printable_usage, DocoptExit

import docker
from subprocess import Popen, PIPE
from influxdb import InfluxDBClient
from nap.url import Url
import json
import requests
import sys
import os
import time
import tarfile
import fileinput
import mmap
import re
import shutil
import datetime


__author__ = 'marco.bonezzi'

#Configuration to get the Docker environment
cwd = os.getcwd()
#Docker client is global and used in all functions
#cli = docker.Client(base_url='unix://var/run/docker.sock')
cli = docker.from_env()
args = docopt(__doc__, version='mseries version 0.0')


#################################################
#   Function:   JsonApi(Url)
#   Input:      url for the api call
#   Output:     json response to the call
#################################################

class JsonApi(Url):
    def after_request(self, response):
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()

#################################################
#   Function:   list()
#   Input:      None
#   Output:     prints list of containers running
#################################################
def list():
    print cli.containers()

#################################################
#   Function:   remove(container)
#   Input:      container (string) to be removed
#   Output:     result of the action
#################################################
def remove( cont ):
    cli.remove_container(container=cont)

#################################################
#   Function:   stop(container)
#   Input:      container (string) to be stopped
#   Output:     result of the action
#################################################
def stop (cont):
    cli.stop(cont)

#################################################
#   Function:       stop_running()
#   Input:          None
#   Output:         0 if correct
#   Description:    Search for grafana and influx
#                   containers to stop
#################################################
def stop_running():
    containers_running = cli.containers()
    c_grafana=cli.containers(all=True,filters={'name':'grafana'})
    #print c_grafana
    if c_grafana:
        stop('grafana')
        remove('grafana')
    c_influx=cli.containers(all=True,filters={'name':'influx'})
    #print c_influx
    if c_influx:
        stop("influx")
        remove("influx")
    return 0

#################################################
#   Function:       stop_mseries()
#   Input:          None
#   Output:         0 if correct
#   Description:    Search for mseries containers
#                   to stop
#################################################
def stop_mseries():
    #Search all containers based on mseries image
    c_mseries = cli.containers(all=True, filters={'ancestor': 'mseries'})
    #if found, stop and then remove
    for c in c_mseries:
        stop(c)
        remove(c)
    return 0

##################################################################################################
#   Function:       print_build(build_result)
#   Input:          output from client.build()
#   Output:         0 if correct
#   Description:    Print the output from mseries image build
#
##################################################################################################
def print_build(build_result):
   for lines in build_result:
       # sometimes all the data is sent on a single line ????
       #
       # ValueError: Extra data: line 1 column 87 - line 1 column
       # 33268 (char 86 - 33267)
       line = lines[0]
       # This ONLY works because every line is formatted as
       # {"stream": STRING}
       parsed_lines = [
           json.loads(obj)['stream'].strip() for obj in
           re.findall('{\s*"stream"\s*:\s*"[^"]*"\s*}', lines)
           ]
       print("".join(parsed_lines))

##################################################################################################
#   Function:       stop_mseries()
#   Input:          ftdc_file
#   Output:         0 if correct
#   Description:    Build the mseries image including
#                   the ftdc parser and copy the ftdc file inside the image
##################################################################################################
def build_mseries( ftdc_file):
    print "Preparing the image for mseries-dash..."
    #print args['<file>'][0]

    #cli.build(dockerfile='mseries.docker', path="image/", rm=True, quiet=False, tag='mseries', stream=False, buildargs = {'FTDC_FILE' : ftdc_file})

    #DEBUG BUILD
    response = cli.build(dockerfile='mseries.docker', path="image/", rm=True, quiet=True, tag='mseries', stream=True, buildargs={'FTDC_FILE': ftdc_file})
    #PRINT BUILD OUTPUT
    print_build(response)
    os.remove('image/'+ftdc_file)
    print "Image for mseries-dash created correctly..."
    return 0


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        for name in os.listdir(source_dir):
            if 'metrics.' in name:
                tar.add(source_dir+"/"+name, arcname=name)
                #print ("Adding " + source_dir+"/"+name+ " to " + source_dir)

def prepare_ftdc_file (ftdc_data):
    #Detect if ftdc_data is already a tar file
    #if tar, return ftdc_data
    if (ftdc_data.endswith("tar.gz")) or (ftdc_data.endswith("tgz")):
        #print ("FTDC FILE IS " + ftdc_data)
        return ftdc_data
    else:
        if os.path.isdir(ftdc_data) == True:
        #if directory, create a tar from it only including metrics files and return the filename
            mseries_ftdc_file='mseries_ftdc.tar.gz'
            make_tarfile(mseries_ftdc_file, ftdc_data)
            #print("FTDC FILE IS " + mseries_ftdc_file)
            return mseries_ftdc_file




##################################################################################################
#   Function:       host_config_influx()
#   Input:          None
#   Output:         host_config object for create_container
#   Description:    Define the host_config for the influx container. Here we define bind points or
#                   ports. For example, the data directory will be based on the data argument
#                   (args['--data'][0])
##################################################################################################
def host_config_influx():
    influx_cfg_file=os.getcwd()+'/influxdb.conf'
    from os.path import expanduser
    home = expanduser("~")

    #Data directory: if defined, use it. If not, use project
    if args['--data']:
        data_dir = args['--data'][0]
    else:
        data_dir = home+"/.mseries/"+args['--project'][0]
    print ("Setting ftdc data directory to " + data_dir + "...")
    print ("")
    if influx_cfg_file:
        return cli.create_host_config(
            binds={
                data_dir: {
                    'bind' : '/var/opt/influxdb/data',
                    'mode' :  'rw',
                },
                influx_cfg_file: {
                    'bind' : '/etc/influxdb/influxdb.conf',
                    'mode' : 'ro',
                }
            },
            port_bindings={
                8086: 8086
            }
        )

##################################################################################################
#   Function:       host_config_grafana()
#   Input:          None
#   Output:         host_config object for the create_container function
#   Description:    Define the host_config for the grafana container. Here we define bind points or
#                   ports.
##################################################################################################
def host_config_grafana():
    from os.path import expanduser
    home = expanduser("~")
    return cli.create_host_config(
        binds={
            home + "/.mseries/" +args['--project'][0]+ '/.grafana': {
                'bind': '/var/lib/grafana',
                'mode': 'rw',
            },
        },
        port_bindings={
            3000: 3000,
            80: 80
        }
    )

##################################################################################################
#   Function:       host_config_mseries()
#   Input:          dashboard_file to import
#   Output:         host_config object for create_container
#   Description:    Define the host_config for the mseries container. Here we define bind points or
#                   ports.
##################################################################################################

def host_config_mseries():
    return cli.create_host_config(
        port_bindings={
            3000: 3000
        }
    )

##################################################################################################
#   Function:       get_image()
#   Input:          image (string)
#   Output:         Return 0 if the image is pulled correctly
#   Description:    Pull the image if not existing on the host
##################################################################################################

def get_image(image):
    #print cli.images()
    cli.pull(image)
    return 0

##################################################################################################
#   Function:       create_influxdb()
#   Input:          None
#   Output:         Return 0 if the image is started correctly
#   Description:    Create and start container for influxdb (using the generated host_config)
##################################################################################################

def create_influxdb():
    #generate the host_config for the container to include port and volume mapping
    influx_config = host_config_influx()
    #pull the image in case is not yet available
    get_image('influxdb:1.1.1-alpine')
    #Create influxdb container
    influx = cli.create_container(image='influxdb:1.1.1-alpine',hostname='influx',name='influx',host_config=influx_config)
    #print influx
    #Start running the container (async)
    cli.start(influx)
    return 0

##################################################################################################
#   Function:       create_grafana()
#   Input:          None
#   Output:         Return 0 if the image is started correctly
#   Description:    Create and start container for grafana(4.0.2)(using the generated host_config)
##################################################################################################

def create_grafana():
    # generate the host_config for the container to include port and volume mapping
    grafana_config = host_config_grafana()
    # pull the image in case is not yet available
    get_image('grafana/grafana:4.2.0')
    #Create grafana container
    grafana = cli.create_container(image='grafana/grafana:4.2.0',hostname='grafana',name='grafana',host_config=grafana_config)
    #print grafana
    # Start running the container (async)
    cli.start(grafana)
    return 0

##################################################################################################
#   Function:       get_influx_ip()
#   Input:          None
#   Output:         String with the IP for the influx container
#   Description:    Inspect the influx container to return its IP address
##################################################################################################

def get_influx_ip():
    # Influx IP
    details = cli.inspect_container('influx')
    influx_ip = details['NetworkSettings']['Networks']['bridge']['IPAddress']
    return influx_ip


##################################################################################################
#   Function:       create_datasource(influx_ip,database)
#   Input:          influx_ip
#   Output:         Return 0 if the image is started correctly
#   Description:    Create and start container for grafana(4.0.2)(using the generated host_config)
##################################################################################################

def create_datasource(influx_ip,database):
    #print (database)
    api = JsonApi('http://localhost:3000/api/', auth=('admin', 'admin'))
    IP = "http://" + influx_ip + ":8086"

    try:
        response = api.post('datasources', json={
            "name": "mseries",
            "type": "influxdb",
            "url": IP,
            "access": "proxy",
            "database": database,
            "basicAuth": False,
            "user": "root",
            "password": "root",
            "isDefault": True
        }, headers={'content-type': 'application/json'})
    except:
        print "Datasource already defined."
        #sys.exc_info()[0]
    print "- Grafana datasource added correctly."
    print
    response = api.get('datasources/1')
    print(response)

##################################################################################################
#   Function:       import_dashboard(dashboard_file)
#   Input:          dashboard_file to import
#   Output:         Return 0 if imported correctly
#   Description:    Function to import json dashboard files into grafana
##################################################################################################

def import_dashboard( dashboard_file ):
    #Get the dashboard file
    #print dashboard_file
    FILE=str(dashboard_file)

    #Set the API call to Grafana
    api = JsonApi('http://localhost:3000/api/', auth=('admin', 'admin'))
    #Open the dashboard file
    #Reading file
    contents = open(FILE, 'rb').read()
    headers = {'Content-Type': 'application/json'}

    # POST request to create dashboard
    api = Url('http://localhost:3000/', auth=('admin', 'admin'))
    dashboards = api.post('api/dashboards/db', data=contents, headers=headers)
    #DEBUG
    print(dashboards.json())
    #star = api.post('api/user/stars/dashboard/1')
    #print(star.json())
    return 0


##################################################################################################
#   Function:       read_ftdc(ftdc_file)
#   Input:          ftdc file to import
#   Output:         Return 0 if imported correctly
#   Description:    function to invoke the mseries parser over each ftdc file to import metrics
##################################################################################################

def read_ftdc(ftdc_file,database):
    print("")
    print("---")
    print ("Preparing to import FTDC data for project: "+ database)
    #Generate the host_config for the mseries container
    mseries_config = host_config_mseries()

    # Influx IP
    #We try first to retrieve the IP of the influx container
    details = get_influx_ip()
    if details:
        influx_ip = details
        URI = "influxdb://" + influx_ip + ":8086/"+database
    else:
        URI = "influxdb://" + args['--host'][0] + ":8086/"+database

    print "-------------"
    print "Database URI: "+URI
    print "-------------"

    #Now we explore the ftdc file to get each filename to import
    #ftdc_file is a tar file so we open it to get each member
    tar = tarfile.open(ftdc_file)
    #For all members in the tar file
    for member in tar.getmembers():
        #print ("Member is " + member.name)
        #if it is a regular file
        if member.isreg():
            #Get the basename of the file
            member.name = os.path.basename(member.name)
            #Generate the command to import this metrics file, using URI, project name, sample detail and file name
            command_mseries = "stdbuf -i0 -o0 -e0 mseries-write --uri=" + URI + " --project " + args['--project'][0] + " --sample " + \
                              args['--sample'][0] + " " + member.name
            # print command_mseries
            #Create (and not yet run) the mseries container: it will run the command_mseries command
            mseries = cli.create_container(image='mseries', tty=False, stdin_open=True, hostname='mseries', command=command_mseries, host_config=mseries_config)

            #Starting the container
            print("- Importing "+member.name+"...")
            cli.start(container=mseries['Id'])


            #NEEDSWORK: THIS SECTION NEED TO BE IMPROVED TO STREAM PROPERLY THE OUTPUT from the IMPORT
            #for l in cli.logs(mseries,stdout=True, stderr=True, stream=True, follow=True, tail=True):
             #   sys.stdout.write('\r'+ str(l))
              #  sys.stdout.flush()
              #  sys.stdout.write(out)
               # sys.stdout.flush()
            #cli.wait(container=mseries['Id'])
            #sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
            log = cli.logs(mseries,stdout=True, stderr=True, stream=True, follow=True, tail=True)
            for line in log:
                out=''
                if line:
                    out += line
                    sys.stdout.write('\r'+ str(out))
                    sys.stdout.flush()

    print "------------------------------------------------------"
    print "All metrics files have been successfully imported."
    print "------------------------------------------------------"
    return 0


##################################################################################################
#   Function:       import_all_dashboards()
#   Input:          None
#   Output:         Return 0 if imported correctly
#   Description:    Import all existing dashboards and define preferences
##################################################################################################

def import_all_dashboards():
    print "- Importing dashboards:"
    import_dashboard(cwd+'/dashboard/newTimeseries1.json.range')
    print "...Oplog statistics imported"
    import_dashboard(cwd+'/dashboard/Oplogstatistics.json.range')
    print "...New timeseries imported"
    import_dashboard(cwd+'/dashboard/timeseries.json.range')
    print "...Timeseries imported"
    import_dashboard(cwd+'/dashboard/System.json.range')
    print "...System imported"
    import_dashboard(cwd+'/dashboard/WiredTigerEviction.json.range')
    print "...WiredTiger Eviction imported"
    set_dashboard_preferences()
    print
    return 0

##################################################################################################
#   Function:       get_dashboard_range(ftdc_file)
#   Input:          ftdc_file to import
#   Output:         Return 0 if imported correctly
#   Description:    Get the range of data in the ftdc_file to adapt the dashboards time frame
##################################################################################################

def get_dashboard_range(ftdc_file):
    #Getting the correct range from the first and last file
    print "Setting the dashboard's time and date"
    if ftdc_file:
        tar = tarfile.open(ftdc_file)
        i = 0;
        #For all files in the tar file
        count = 0
        for member in tar.getmembers():
            if 'metrics' in member.name:
                #print count
                #print os.path.basename(member.name)

                idx = tar.getmembers().index(member)
                #If it is a simple file with idx 1, it's the first file we are interested in
                if member.isreg() and idx == 0:
                    #print member
                    member.name = os.path.basename(member.name)
                    #print member.name, idx
                    #Get only the date from it
                    start = member.name[8:18]
                    #end = member.name[8:18]
                #It it is the last file and contains interim, we need to go back to the previous
                if member.isreg() and ("interim" in member.name):
                    last=tar.getmembers()[i-2]
                    last.name = os.path.basename(last.name)
                    end = last.name[8:18]
                # If a single file, just use the same date as start as it will be start at 23:59
                elif count == 0:
                    # Get only the date from it
                    member.name = os.path.basename(member.name)
                    end = member.name[8:18]
                count += 1

    # Initialising start and end time in case it is not possible from the ftdc files
    try:
        end
    except NameError:
        end = get_def_end()

    try:
        start
    except NameError:
        start = get_def_start()


    print
    print 'Diagnostic data in ' + ftdc_file + ' covers from ' + start + ' to ' + end
    print
    #Closing the tar file
    tar.close()
    # We got the ranges so we can set the dashboard to the actual time
    set_dashboards(start, end)

def get_def_start():
    #get_dashboard_start_from_influx()
    startdate = datetime.datetime.strptime(datetime.date.today().strftime("%Y-%m-%d"), "%Y-%m-%d") - datetime.timedelta(
        days=2)
    start = startdate.strftime("%Y-%m-%d")
    #print ("Start date " + start)
    return start

def get_def_end():
    enddate = datetime.datetime.strptime(datetime.date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    end = enddate.strftime("%Y-%m-%d")
    #print ("End date " + end)
    return end

def set_dashboards(start, end):
    #We got the ranges so we can set the dashboard to the actual time
    set_dashboard_range("dashboard/timeseries.json",start,end)
    set_dashboard_range("dashboard/Oplogstatistics.json",start,end)
    set_dashboard_range("dashboard/newTimeseries1.json",start,end)
    set_dashboard_range("dashboard/WiredTigerEviction.json", start, end)
    set_dashboard_range("dashboard/System.json", start, end)
    #print "Dashboards set correctly from "+str(start)+ " to " + str(end)

##################################################################################################
#   Function:       set_dashboard_range(dashboard_file,start_range,end_range)
#   Input:          dashboard_file,start_range,end_range
#   Output:         Return 0 if read correctly
#   Description:    Set the range of data in the ftdc_file to adapt the dashboards time frame
##################################################################################################
def set_dashboard_range(dashboard_file,start_range,end_range):
    #Create a new dashboard file with the new time and date limits
    output = dashboard_file +'.range'
    output_dashboard = open(output, 'w')
    #Open and read the dashboard file to replace time and date
    with open(dashboard_file) as f:
        #for line in f:
            #print line
        map=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
        #Replace start and end time
        for mline in iter(map.readline, ""):
                start=str(start_range)+' 00:00:00'
                end=str(end_range)+' 23:59:59'
                if ("-1h" in mline):
                    mlinen = re.sub('now-1h',start, mline)
                else:
                    mlinen = re.sub(r'now',end, mline)

                output_dashboard.write(mlinen)
        #Close the mmap file
        map.close()
    #close the dashboard file open
    output_dashboard.close()
    return 0

##################################################################################################
#   Function:       set_dashboard_preferences()
#   Input:          None
#   Output:         Return 0 if set correctly
#   Description:    Define dashboard and general grafana preferences
##################################################################################################

def set_dashboard_preferences():
    api = JsonApi('http://localhost:3000/api/', auth=('admin', 'admin'))

    # Setting preferences
    contents = {"theme": "light", "homeDashboardId": 1, "timezone": "UTC"}
    headers = {'Content-Type': 'application/json'}

    # POST request to create dashboard
    api = Url('http://localhost:3000/api/', auth=('admin', 'admin'))
    preferences = api.put('org/preferences', json=contents)
    #print(preferences.json())
    response = api.get('org/preferences')
    #print(response.json())
    return 0


def get_dashboard_start_from_influx():
    # Influx IP
    # Connecting locally so we use localhost
    URI = "influxdb://localhost:8086/" + args['--project'][0]

    InfluxClient = InfluxDBClient.from_DSN(URI, timeout=5)
    #print("Getting start from influx")
    start_rs=InfluxClient.query('select "start" from serverStatus order by time asc limit 1')
    for i in start_rs.get_points(measurement='serverStatus'):
         start_ts=i['start']
    #print start_ts

    start=datetime.datetime.fromtimestamp(int(start_ts/1000)).strftime('%Y-%m-%d')
    #print(start)
    return start

def get_dashboard_end_from_influx():
    # Influx IP
    # Connecting locally so we use localhost
    URI = "influxdb://localhost:8086/" + args['--project'][0]

    InfluxClient = InfluxDBClient.from_DSN(URI, timeout=5)
    #print("Getting End from influx")
    end_rs=InfluxClient.query('select "end" from serverStatus order by time desc limit 1')
    for i in end_rs.get_points(measurement='serverStatus'):
         end_ts=i['end']
    #print end_ts

    end=datetime.datetime.fromtimestamp(int(end_ts/1000)).strftime('%Y-%m-%d')
    #print(end)
    return end

def mseries_restart():
    stop_running()
    create_influxdb()
    create_grafana()
    time.sleep(20)
    import_all_dashboards()
    create_datasource(get_influx_ip(),args['--project'][0])
    print("")
    print("==============================================")
    print "     mseries-dash ready at localhost:3000     "
    print("==============================================")
    print("")

def mseries_stop():
    stop_running()
    print "mseries-dash stopped"

def mseries_start_read():
    stop_mseries()
    stop_running()
    ftdc_file=prepare_ftdc_file(args['<file>'][0])
    #print ("FTDC file in start_read is"+ftdc_file)
    new_ftdc_name= 'import.' + os.path.basename(ftdc_file)
    print new_ftdc_name
    shutil.copy2(ftdc_file, cwd+'/image/'+new_ftdc_name)
    build_mseries(new_ftdc_name)
    stop_running()
    create_influxdb()
    create_grafana()
    time.sleep(30)
    get_dashboard_range(ftdc_file)
    import_all_dashboards()
    create_datasource(get_influx_ip(),args['--project'][0])
    print("")
    print("==============================================")
    print "     mseries-dash ready at localhost:3000     "
    print("==============================================")
    print("")
    read_ftdc(ftdc_file,args['--project'][0])


def mseries_workon():
    from os.path import expanduser
    home = expanduser("~")
    mseries_home = home + "/.mseries/"
    #get_dashboard_range(args['<file>'][0])
    print("Stopping any previous mseries-dash")
    stop_running()
    print("Preparing mseries-dash database...")
    create_influxdb()
    print("Preparing mseries-dash interface on localhost:3000...")
    create_grafana()
    print("Setup almost done, checking the current configuration...")
    time.sleep(30)
    set_dashboards(get_dashboard_start_from_influx(), get_dashboard_end_from_influx())
    import_all_dashboards()
    #print("Project is: "+args['--project'][0])
    if (args['--project']) == 'mseries':
        create_datasource(get_influx_ip(), args['--project'][0])
    else:
        project=mseries_home + args['--project'][0]
        print("Project set to  " + os.path.basename(project))
        create_datasource(get_influx_ip(), os.path.basename(project))
    print("")
    print("==============================================")
    print("     mseries-dash ready at localhost:3000     ")
    print("==============================================")
    print("")


def mseries_read():
    ftdc_file = prepare_ftdc_file(args['<file>'][0])
    # print ("FTDC file in start_read is"+ftdc_file)
    new_ftdc_name = 'import.' + os.path.basename(ftdc_file)
    print
    new_ftdc_name
    shutil.copy2(ftdc_file, cwd + '/image/' + new_ftdc_name)
    build_mseries(new_ftdc_name)
    read_ftdc(ftdc_file, args['--project'][0])


#read_ftdc(args['<file>'][0])


##################################################################################################
#   Function:       __main__
#   Input:          None
#   Output:         Return 0 if correct
#   Description:    Main program (mseries-dash)
##################################################################################################
if __name__ == '__main__':
    from os.path import expanduser
    home = expanduser("~")
    mseries_home=home+"/.mseries/"
    run=0
    #stop_mseries()
    #stop_running()
    print args

    if (args['<command>']) == 'import':
        run=1
        #print args['<command>']
        print args['<file>']
        if (args['<file>']):
            mseries_start_read()
            stop_mseries()
        else:
            print
            print "Missing ftdc file"
            print "Usage: mseries-dash <command> [options...] [<wswfile>...]"

    if (args['<command>']) == 'read':
        # print args['<command>']
        run = 1
        print
        args['<file>']
        if (args['<file>']):
            mseries_read()
            stop_mseries()
        else:
            print
            print
            "Missing ftdc file"
            print
            "Usage: mseries-dash <command> [options...] [<wswfile>...]"

    # WORKON

    elif (args['<command>']) == 'workon':
        run = 1
        if (args['--project'][0]) != 'mseries':
            print("")
            print("Starting workon mode")
            #print("Reading ftdc data from: "+ mseries_home +args['--project'][0]+ "...")
            mseries_workon()
        else:
            print("")
            print("Please define the project to work on")
            print("Usage: ./mseries-dash.py workon --project PROJECT")
            print("")
    # STOP

    elif (args['<command>']) == 'stop':
        run = 1
        print args['<command>']
        mseries_stop()
    # ls
    elif (args['<command>']) == 'ls':
        run = 1
        print("")
        print("List of projects available in "+mseries_home)
        print("")
        from subprocess import call
        call(["ls", "-1",mseries_home])

    # drop
    elif (args['<command>']) == 'drop':
        if (args['--project'][0]) != 'mseries':
            run = 1
            print("")
            print("Dropping project "+args['--project'][0]+" from " + mseries_home)
            print("")
            from subprocess import call
            directory=mseries_home+args['--project'][0]
            print directory
            call(["rm", "-rf", directory])
            print("")
            print("Project " + args['--project'][0] + " removed correctly from " + mseries_home)
            print("")
        else:
            print("")
            print("Please define the project to drop")
            print("Usage: ./mseries-dash.py drop --project PROJECT")
            print("")

    elif run == 0:
        print("")
        print ("mseries-dash "+args['<command>']+" is not a valid command")
        print("Check available commands with mseries-dash --help")

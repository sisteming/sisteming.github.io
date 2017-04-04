mseries-dash
===========


Description
-----

mseries-dash aims to help the analysis of WiredTiger related issues or other general MongoDB issues where we need to analyse in detail the content of ftdc's diagnostic data.

mseries-dash is based on Jim's mseries ftdc parser and adds the automatic deployment of influxdb and grafana, along with the configuration of a new datasource and the import of predefined dashboards to analyse common MongoDB and WiredTiger issues.

Requirements
-----

To run mseries-dash (which includes Jim's ftdc parser, mseries), the following requirements have to be met in your local machine.

**Docker**

- **Mac OSX**:

	**[Docker for Mac (beta)](https://docs.docker.com/docker-for-mac/)**
	
	*Note*: All testing has been done with the beta version, so it is recommended to use the beta instead of the stable release.
	
	Download @ [https://download.docker.com/mac/beta/Docker.dmg](https://download.docker.com/mac/beta/Docker.dmg)

- **Linux**:

	Normal Docker installation through package manager

**Python dependencies**

To make sure you have all dependencies required (using Python 2.7), you would need to install the required libraries with:

```
	pip install -r requirements.txt
```

requirements.txt

```
nap
requests
docker-py
python-dateutil
python-dash
humanfriendly
pytz
influxdb
backports.functools_lru_cache
```

Once all the above is installed, mseries-dash is ready to use.

Using mseries-dash
-----

Depending on the command used, mseries-dash will deploy influxdb and grafana containers to read existing ftdc data or to import new ftdc data.

If you think any other command or mode will be useful, just let me know! ;)

Main commands:

**import:**

i.e.: `
./mseries-dash.py import /Users/marco/Downloads/2016/3.2.10/metrics.tar.gz --sample 20`

	
`mseries-dash import` will perform the following:
	
- Deploy influxdb and grafana containers
- Build mseries-dash image
- Configure influx as grafana datasource
- Import dashboards and set preferences
- Import data from ftdc file

**read**

The read command allow us to go back to existing data previously imported. For this, we need to refer the project name:
		
- project (--project used for import) 


	./mseries-dash.py read --project MDB34

	
**stop**

		- Stop all running containers associated with mseries-dash (influx, grafana, 			mseries)
		
**ls**

List of projects imported with mseries-dash:

```
./mseries-dash.py ls
{'--data': [],
 '--help': 0,
 '--host': ['localhost'],
 '--no-progressbar': 0,
 '--pool': ['4'],
 '--project': ['mseries'],
 '--sample': ['10'],
 '<command>': 'ls',
 '<file>': []}

List of projects available in /Users/marco/.mseries/

lsa
mmm
mseries
ppp
```


**Usage**

```
usage:
   mseries-dash <command> [options...] [<file>...]

Commands:
   import     import the contents of the specified files / paths
   stop       stop mseries-dash
   read       Deploy mseries-dash without a new import
   help       the help
options:
   -p, --project=<project>  the project name [default: mseries]
   -h --help   Show this screen.
   --pool=<processes>     the number of processes in the pool, defaults to all [default: 4].
   --no-progressbar
   -s, --sample=<sample>      the sample ratio, ie. 1 in <sample> [default: 1].
   -d --data <data>       Data directory where the data parsed is stored [default: /Users/ftdc/data].
   -h --host <host>        Database instance to connect to. Defaults to localhost. [default: localhost]


See 'mseries-dash help <command>' for more information on a specific command.
```

ToDo
-----

- Remove command
- Option to change grafana directory
- Improve and add dashboard graphs
- Clean mseries-dash.py code
- Enable proper output streaming
- Fix documentation style
- Configurable ports
- ...

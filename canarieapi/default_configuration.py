# coding: utf-8

"""
Default configuration values for Canarie API.

To have the programs in the package override the values with the values
found in this file, you need to set the environment variable named
"CANARIE_API_CONFIG_FN" to the path of your own copy before launching the program.
"""

MY_SERVER_NAME = 'http://localhost:2000'
SERVER_MAIN_TITLE = 'Canarie API'

# additional_stats: If True, will collect stats for each ip calling every route. Calls are aggregated by hour.
# ip_information: If True, will collect additional information on all callers ips.
from os import environ
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD","simplepass1")


DATABASE = {
    'access_log': '/var/log/nginx/access.log',
    'log_pid': '/var/run/nginx.pid',
    'pg_conn_str': f'dbname=postgres user=postgres password={POSTGRES_PASSWORD} host=127.0.0.1 port=5432',
    'additional_stats' : False,
    'ip_information': False
}

SERVICES = {
    'name': {
        'info': {
            'name': 'service',
            'synopsis': 'synopsis',
            'version': '1.0.0',
            'institution': 'institution',
            'releaseTime': '2017-01-01T00:00:00Z',
            'researchSubject': 'subject',
            'supportEmail': 'support@institution.com',
            'category': 'category',
            'tags': ['tag1', 'tag2']
        },
        'stats': {
            'method': '.*',
            'route': '/name/service/.*'
        },
        'redirect': {
            'doc': 'https://science.canarie.ca/researchsoftware/home/main.html',
            'releasenotes': 'https://science.canarie.ca/researchsoftware/home/main.html',
            'support': 'https://science.canarie.ca/researchsoftware/home/main.html',
            'source': 'https://science.canarie.ca/researchsoftware/home/main.html',
            'tryme': 'https://science.canarie.ca/researchsoftware/home/main.html',
            'licence': 'https://science.canarie.ca/researchsoftware/home/main.html',
            'provenance': 'https://science.canarie.ca/researchsoftware/home/main.html'
        },
        'monitoring': {
            'Component': {
                'request': {
                    'url': 'https://science.canarie.ca/researchsoftware/home/main.html'
                }
            }
        }
    }
}

PLATFORMS = {
    'pf_name': {
        'info': {
            'name': 'service',
            'synopsis': 'synopsis',
            'version': '1.0.0',
            'institution': 'institution',
            'releaseTime': '2017-01-01T00:00:00Z',
            'researchSubject': 'subject',
            'supportEmail': 'support@institution.com',
            'tags': ['tag1', 'tag2']
        },
        'stats': {
            'method': '.*',
            'route': '/pf_name/platform/.*'
        },
        'redirect': {
            'doc': 'https://science.canarie.ca/researchsoftware/home/main.html',
            'releasenotes': 'https://science.canarie.ca/researchsoftware/home/main.html',
            'support': 'https://science.canarie.ca/researchsoftware/home/main.html',
            'source': 'https://science.canarie.ca/researchsoftware/home/main.html',
            'tryme': 'https://science.canarie.ca/researchsoftware/home/main.html',
            'licence': 'https://science.canarie.ca/researchsoftware/home/main.html',
            'provenance': 'https://science.canarie.ca/researchsoftware/home/main.html',
            'factsheet': 'https://science.canarie.ca/researchsoftware/home/main.html'
        },
        'monitoring': {
            'Component': {
                'request': {
                    'url': 'https://science.canarie.ca/researchsoftware/home/main.html'
                }
            }
        }
    }
}

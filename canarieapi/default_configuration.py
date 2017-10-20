# coding: utf-8

"""
Default configuration values for Canarie API.

To have the programs in the package override the values with the values
found in this file, you need to set the environment variable named
"CANARIE_API_CONFIG_FN" to the path of your own copy before launching the program.
"""

MY_SERVER_NAME = 'http://localhost:5000'

DATABASE = {
    'filename': '/opt/local/src/CanarieAPI/stats.db',
    'schema_filename': 'database_schema.sql',
    'access_log': '/var/log/nginx/access_file.log',
    'log_pid': '/var/run/nginx.pid'
}

SERVICES = {
    'node': {
        'info': {
            'name': 'Node',
            'synopsis': 'Node synopsis',
            'version': '1.0.0',
            'institution': 'CRIM',
            'releaseTime': '2017-10-05 00:00',
            'researchSubject': 'Climatology',
            'supportEmail': 'pavics-dev@crim.ca',
            'category': 'Resource/Cloud Management',
            'tags': 'Climatology,Cloud'
        },
        'stats': {
            'method': '(GET|POST|PUT|DELETE)',
            'route': '/node/service/.*'
        },
        'redirect': {
            'doc': 'https://ouranosinc.github.io/pavics-sdi',
            'releasenotes': 'https://ouranosinc.github.io/pavics-sdi/releasenotes/index.html',
            'support': 'https://ouranosinc.github.io/pavics-sdi/support/index.html',
            'source': 'https://github.com/Ouranosinc/PAVICS-frontend',
            'tryme': 'https://ouranosinc.github.io/pavics-sdi',
            'license': 'https://ouranosinc.github.io/pavics-sdi/license/index.html',
            'provenance': 'https://ouranosinc.github.io/pavics-sdi/provenance/index.html'
        },
        'monitoring': {}
    },
    'bias': {
        'info': {
            'name': 'Bias correction',
            'synopsis': 'Bias correction service synopsis',
            'version': '1.0.0',
            'institution': 'CRIM',
            'releaseTime': '2017-10-05 00:00',
            'researchSubject': 'Climatology',
            'supportEmail': 'pavics-dev@crim.ca',
            'category': 'Data Manipulation',
            'tags': 'Climatology,Cloud'
        },
        'stats': {
            'method': 'GET',
            'route': '/bias/service/.*'
        },
        'redirect': {
            'doc': 'https://ouranosinc.github.io/pavics-sdi',
            'releasenotes': 'https://ouranosinc.github.io/pavics-sdi/releasenotes/index.html',
            'support': 'https://ouranosinc.github.io/pavics-sdi/support/index.html',
            'source': 'https://github.com/Ouranosinc/PAVICS-frontend',
            'tryme': 'https://ouranosinc.github.io/pavics-sdi',
            'license': 'https://ouranosinc.github.io/pavics-sdi/license/index.html',
            'provenance': 'https://ouranosinc.github.io/pavics-sdi/provenance/index.html'
        },
        'monitoring': {}
    },
    'indices': {
        'info': {
            'name': 'Climate indices',
            'synopsis': 'Climate indices service synopsis',
            'version': '1.0.0',
            'institution': 'CRIM',
            'releaseTime': '2017-10-05 00:00',
            'researchSubject': 'Climatology',
            'supportEmail': 'pavics-dev@crim.ca',
            'category': 'Data Manipulation',
            'tags': 'Climatology,Cloud'
        },
        'stats': {
            'method': 'GET',
            'route': '/indices/service/.*'
        },
        'redirect': {
            'doc': 'https://ouranosinc.github.io/pavics-sdi',
            'releasenotes': 'https://ouranosinc.github.io/pavics-sdi/releasenotes/index.html',
            'support': 'https://ouranosinc.github.io/pavics-sdi/support/index.html',
            'source': 'https://github.com/Ouranosinc/PAVICS-frontend',
            'tryme': 'https://ouranosinc.github.io/pavics-sdi',
            'license': 'https://ouranosinc.github.io/pavics-sdi/license/index.html',
            'provenance': 'https://ouranosinc.github.io/pavics-sdi/provenance/index.html'
        },
        'monitoring': {}
    },
    'renderer': {
        'info': {
            'name': 'High-resolution spatial gridded data renderer',
            'synopsis': 'High-resolution spatial gridded data renderer synopsis',
            'version': '1.0.0',
            'institution': 'CRIM',
            'releaseTime': '2017-10-05 00:00',
            'researchSubject': 'Climatology',
            'supportEmail': 'pavics-dev@crim.ca',
            'category': 'Data Manipulation',
            'tags': 'Climatology,Cloud'
        },
        'stats': {
            'method': '.*',
            'route': '/renderer/service/.*'
        },
        'redirect': {
            'doc': 'https://ouranosinc.github.io/pavics-sdi',
            'releasenotes': 'https://ouranosinc.github.io/pavics-sdi/releasenotes/index.html',
            'support': 'https://ouranosinc.github.io/pavics-sdi/support/index.html',
            'source': 'https://github.com/Ouranosinc/PAVICS-frontend',
            'tryme': 'https://ouranosinc.github.io/pavics-sdi',
            'license': 'https://ouranosinc.github.io/pavics-sdi/license/index.html',
            'provenance': 'https://ouranosinc.github.io/pavics-sdi/provenance/index.html'
        },
        'monitoring': {}
    },
    'slicer': {
        'info': {
            'name': 'Spatial and temporal data slicer',
            'synopsis': 'Spatial and temporal data slicer synopsis',
            'version': '1.0.0',
            'institution': 'CRIM',
            'releaseTime': '2017-10-05 00:00',
            'researchSubject': 'Climatology',
            'supportEmail': 'pavics-dev@crim.ca',
            'category': 'Data Manipulation',
            'tags': 'Climatology,Cloud'
        },
        'stats': {
            'method': '.*',
            'route': '/slicer/service/.*'
        },
        'redirect': {
            'doc': 'https://ouranosinc.github.io/pavics-sdi',
            'releasenotes': 'https://ouranosinc.github.io/pavics-sdi/releasenotes/index.html',
            'support': 'https://ouranosinc.github.io/pavics-sdi/support/index.html',
            'source': 'https://github.com/Ouranosinc/PAVICS-frontend',
            'tryme': 'https://ouranosinc.github.io/pavics-sdi',
            'license': 'https://ouranosinc.github.io/pavics-sdi/license/index.html',
            'provenance': 'https://ouranosinc.github.io/pavics-sdi/provenance/index.html'
        },
        'monitoring': {}
    }
}

PLATFORMS = {
    'pavics': {
        'info': {
            'name': 'PAVICS',
            'synopsis': 'PAVICS platform synopsis',
            'version': '1.0.0',
            'institution': 'CRIM',
            'releaseTime': '2017-10-05 00:00',
            'researchSubject': 'Climatology',
            'supportEmail': 'pavics-dev@crim.ca',
            'tags': 'Climatology,Cloud'
        },
        'stats': {
            'method': '.*',
            'route': '/pavics/platform/.*'
        },
        'redirect': {
            'doc': 'https://ouranosinc.github.io/pavics-sdi',
            'releasenotes': 'https://ouranosinc.github.io/pavics-sdi/releasenotes/index.html',
            'support': 'https://ouranosinc.github.io/pavics-sdi/support/index.html',
            'source': 'https://github.com/Ouranosinc/PAVICS-frontend',
            'tryme': 'https://ouranosinc.github.io/pavics-sdi',
            'license': 'https://ouranosinc.github.io/pavics-sdi/license/index.html',
            'provenance': 'https://ouranosinc.github.io/pavics-sdi/provenance/index.html',
            'factsheet': 'https://ouranosinc.github.io/pavics-sdi'
        },
        'monitoring': {}
    }
}

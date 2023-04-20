# coding: utf-8

"""
Default configuration values for Canarie API.

To have the programs in the package override the values with the values
found in this file, you need to set the environment variable named
"CANARIE_API_CONFIG_FN" to the path of your own copy before launching the program.
"""

MY_SERVER_NAME = "http://localhost:2000"
SERVER_MAIN_TITLE = "Canarie API"

# If this is True, canarie-api will parse the nginx logs in DATABASE["access_log"] and report statistics
PARSE_LOGS = True

DATABASE = {
    "filename": "/data/stats.db",
    "access_log": "/logs/nginx-access.log"
}

SERVICES = {
    "name": {
        "info": {
            "name": "service",
            "synopsis": "synopsis",
            "version": "1.0.0",
            "institution": "institution",
            "releaseTime": "2017-01-01T00:00:00Z",
            "researchSubject": "subject",
            "supportEmail": "support@institution.com",
            "category": "category",
            "tags": ["tag1", "tag2"]
        },
        "stats": {
            "method": ".*",
            "route": "/name/service/.*"
        },
        "redirect": {
            "doc": "https://www.canarie.ca/software/",
            "releasenotes": "https://www.canarie.ca/software/",
            "support": "https://www.canarie.ca/software/",
            "source": "https://www.canarie.ca/software/",
            "tryme": "https://www.canarie.ca/software/",
            "licence": "https://www.canarie.ca/software/",
            "provenance": "https://www.canarie.ca/software/"
        },
        "monitoring": {
            "Component": {
                "request": {
                    "url": "https://www.canarie.ca/software/"
                }
            }
        }
    }
}

PLATFORMS = {
    "pf_name": {
        "info": {
            "name": "service",
            "synopsis": "synopsis",
            "version": "1.0.0",
            "institution": "institution",
            "releaseTime": "2017-01-01T00:00:00Z",
            "researchSubject": "subject",
            "supportEmail": "support@institution.com",
            "tags": ["tag1", "tag2"]
        },
        "stats": {
            "method": ".*",
            "route": "/pf_name/platform/.*"
        },
        "redirect": {
            "doc": "https://www.canarie.ca/software/",
            "releasenotes": "https://www.canarie.ca/software/",
            "support": "https://www.canarie.ca/software/",
            "source": "https://www.canarie.ca/software/",
            "tryme": "https://www.canarie.ca/software/",
            "licence": "https://www.canarie.ca/software/",
            "provenance": "https://www.canarie.ca/software/",
            "factsheet": "https://www.canarie.ca/software/"
        },
        "monitoring": {
            "Component": {
                "request": {
                    "url": "https://www.canarie.ca/software/"
                }
            }
        }
    }
}

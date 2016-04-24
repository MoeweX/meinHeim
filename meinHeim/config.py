import os

# the configuration for the webserver
conf = {
    'global': {
        'server.socket_port': 8081,
        'server.socket_host': '0.0.0.0',
        'log.error_file': '',
        'log.access_file': '',
        'log.screen': False
    },
    '/': {
        'tools.staticdir.root': os.path.abspath(os.getcwd())
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': './website',
        'tools.staticdir.index': 'index.html'
    }
}

# the logging configuratoin
log_conf = {
    'version': 1,

    'formatters': {
        'void': {
            'format': ''
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'default_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': 'logs/default.log',
            'maxBytes': 10485760,
            'backupCount': 20,
            'encoding': 'utf8'
        },
        'cherrypy_default_error': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'cherrypy_default_error_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': 'logs/cherrypy_default_error.log',
            'maxBytes': 10485760,
            'backupCount': 20,
            'encoding': 'utf8'
        },
        'cherrypy_access': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'void',
            'filename': 'logs/cherrypy_access.log',
            'maxBytes': 10485760,
            'backupCount': 20,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'default_file'],
            'level': 'INFO'
        },
        'cherrypy.access': {
            'handlers': ['cherrypy_access'],
            'level': 'INFO',
            'propagate': False
        },
        'cherrypy.error': {
            'handlers': ['cherrypy_default_error', 'cherrypy_default_error_file'],
            'level': 'INFO',
            'propagate': False
        },
    }
}
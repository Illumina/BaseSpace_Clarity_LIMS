#!/usr/bin/env python

import glsapiutil3
import platform

api = None

def main():

    global api

    stepURI = 'https://demo.claritylims.com/api/v2/steps/24-000'

    api = glsapiutil3.glsapiutil3()
    
    api.setup( username = 'apiuser', password = 'apipass', sourceURI = stepURI )

    return


if __name__ == '__main__':

    main()

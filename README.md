Welcome to the BaseSpace Clarity LIMS GitHub repository!

The aim is to have code examples and API libraries hosted centrally here.

Currently, you will find the mature **glsapiutil.py** library which should be used for production code.

You will also find **glsapiutil3.py**, which is currently a bleeding-edge alpha version of a library that works with both Python v2 and v3. It is currently lacking some error-checking code and extra functionality present in the mature library, so please use it at your own risk!


## Initialising and using the API object (glsapiutil3)

The new API object can be initialised in two ways:

1. The old (glsapiutil.py) way:
```
api = glsapituil3.glsapiutil3()
api.setHostname('https://demo-5-lite.claritylims.com')
api.setVersion('v2')
api.setup( username = 'apiuser', password = 'apipass')
```

2. The slick new way which saves time in cases where a script has a step or process URI provided to it:
```
api = glsapituil3.glsapiutil3()
api.setup( username = 'apiuser', password = 'apipass', 
          sourceURI = 'https://demo-5-lite.claritylims.com/api/v2/steps/24-1234' )
```

The Python console will provide helpful logging messages once the object gets initialised.

From this point, the function calls are exactly like the previous version's API object:

```
api.GET()
api.POST()
api.PUT()
```

The big advantage, of course, is that this new library works with Python 2 and 3, allowing scripts to be more easily ported.

This is a living repository and will be updated with more details, documentation, and examples as we centralise more code.

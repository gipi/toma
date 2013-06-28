SECRET_KEY = 'miao'

DATABASES = {
    'default': {
         'ENGINE': 'django.contrib.gis.db.backends.postgis',
         'NAME': 'geodatabase',
         'USER': 'geouser',
         'PASSWORD': 'geopassword',
     }
}

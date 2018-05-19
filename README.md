# GISMentors Django registration app

This is the Django-based application for registering new attendees to GISmentors
workshops and courses.

## Dependenices

Django and basic geo-stuff

```
pip install -r requirements.txt
```

## Setting up

```
django-admin startproject gismentors
git clone https://github.com/opengeolabs/gismentors-registration.git registration
```

Now you have to adjust the `settings.py` file

1. Add `registration` to `$PYTHONPATH`
2. Add registration apps to `INSTALLED_APPS`
3. Add `django.contrib.gis` to `INSTALLED_APPS`
4. Adjust database engine for support of spatial models https://docs.djangoproject.com/en/1.11/ref/contrib/gis/tutorial/#configure-settings-py
5. If using `spatialite`, use `SPATIALITE_LIBRARY_PATH` settings option

In `settings.py`:

```
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'leaflet',
    'registration.apps.RegistrationConfig',
    'django.contrib.gis',

]

...

SPATIALITE_LIBRARY_PATH = 'mod_spatialite'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

...

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

```


Do further settings modifications.

## Init databse

```
python manage.py makemigrations registration
python manage.py migrate
```

## Testing

```
python manage.py runserver
```

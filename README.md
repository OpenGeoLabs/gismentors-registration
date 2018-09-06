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
    'captcha'

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

...

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASEDIR, "media")

```


Do further settings modifications.

## Init database

```
python manage.py makemigrations registration
python manage.py migrate
```

## Add url

to `gismentors/urls.py` add `registration.urls`:

```
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    ...
    url(r'^courses/', include('registration.urls')),
    url(r'^captcha/', include('captcha.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Testing

```
python manage.py runserver
```

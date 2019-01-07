# GISMentors Django registration app

This is the Django-based application for registering new attendees to GISMentors
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
6. Set `TEST_MAIL`, `TEST_TITLE` and `TEST_KEY` variables

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

SPATIALITE_LIBRARY_PATH = '/usr/lib/x86_64-linux-gnu/mod_spatialite.so'

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
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

```

```
TEST_MAIL = 'madlen.testing@gmail.com'
TEST_KEY = '831239ad-3b93-4624-9529-6bc67970f541'
TEST_TITLE = 'Testing'
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
from django.urls import include

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

# drf-ember-backend
Backend code to enable Ember Data when using the Django REST Framework

## Usage
Steps to use drf-ember-backend in an existing Django REST Framework based project.
It is assumed that the project already has `Django` and `djangorestframework` in requirements.txt

- Add `drf-ember-backend` to requirements.txt specifying the desired version
- `pip install -r requirements.txt`
- update settings.py adding the renderer, parser and exception handler
```
REST_FRAMEWORK = {
...
    'DEFAULT_RENDERER_CLASSES': (
        ...
        'drf_ember_backend.renderers.JSONRootObjectRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        ...
        'drf_ember_backend.parsers.JSONRootObjectParser',
    ),
    'EXCEPTION_HANDLER': 'drf_ember_backend.exception_handlers.switching_exception_handler',
}
```


## Run Tests
```
virtualenv -p python env
source env/bin/activate
pip install -r devRequirements.txt
python manage.py test
```

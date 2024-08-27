# Gymlog Backend

Gymlog is a workout tracking application designed to help users manage and record their fitness routines efficiently. This repository contains the backend code for the Gymlog application, which handles the core logic, data storage, and API endpoints.
The backend is built with a focus on scalability and performance, using modern technologies and best practices.

[![Frontend](https://img.shields.io/badge/frontend-repo-blue)](https://github.com/Alex-Just/gymlog-frontend)
[![Backend CI](https://github.com/Alex-Just/gymlog-backend/actions/workflows/ci.yml/badge.svg?branch=stage)](https://github.com/Alex-Just/gymlog-backend/actions/workflows/ci.yml)

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<div align="center">

<picture>
    <img alt="Logo" src="https://github.com/user-attachments/assets/637388c4-bd2c-4b00-9192-0e892a6a6d58" />
</picture>
<picture>
    <img alt="Logo" src="https://github.com/user-attachments/assets/927a29c3-b3e1-4914-a266-d43aabfab139" />
</picture>

</div>

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Tech Features](#tech-features)
- [Constraints](#constraints)
- [Basic Commands](#basic-commands)
  - [Setting Up Your Users](#setting-up-your-users)
  - [Type Checks](#type-checks)
  - [Test Coverage](#test-coverage)
    - [Running Tests with Pytest](#running-tests-with-pytest)
  - [Celery](#celery)

This updated structure maintains a clear and concise outline for easy navigation of your project's documentation.

## Features

- **Workout Tracking**: Log exercises, sets, and reps for different workouts.
- **Progress Monitoring**: View progress over time with charts and stats.
- **Custom Routines**: Create and manage custom workout routines.
- **Profile Management**: Update personal information and track personal bests.

## Technologies Used

- **Python**: The primary programming language used for backend development.
- **Django**: A high-level Python web framework that encourages rapid development and clean, pragmatic design.
- **Django Rest Framework (DRF)**: A powerful and flexible toolkit for building Web APIs.
- **PostgreSQL**: A powerful, open-source object-relational database system.
- **Celery**: An asynchronous task queue/job queue based on distributed message passing.
- **Redis**: An in-memory data structure store, used as a database, cache, and message broker.
- **Docker**: A set of platform-as-a-service products that use OS-level virtualization to deliver software in packages called containers.
- **GitHub Actions**: Used for continuous integration and deployment.

## Tech Features

- [12-Factor](https://12factor.net) based settings via [django-environ](https://github.com/joke2k/django-environ)
- Secure by default. We believe in SSL.
- Registration via [django-allauth](https://github.com/pennersr/django-allauth)
- Send emails via [Anymail](https://github.com/anymail/django-anymail) (using [Mailgun](http://www.mailgun.com/) by default or Amazon SES if AWS is selected cloud provider, but switchable)
- Media storage using Amazon S3, Google Cloud Storage, Azure Storage or nginx
- Docker support using [docker-compose](https://github.com/docker/compose) for development and production (using [Traefik](https://traefik.io/) with [LetsEncrypt](https://letsencrypt.org/) support)
- [Procfile](https://devcenter.heroku.com/articles/procfile) for deploying to Heroku
- Instructions for deploying to [PythonAnywhere](https://www.pythonanywhere.com/)
- Run tests with unittest or pytest
- Customizable PostgreSQL version
- Default integration with [pre-commit](https://github.com/pre-commit/pre-commit) for identifying simple issues before submission to code review

## Constraints

- Only maintained 3rd party libraries are used.
- Uses PostgreSQL everywhere: 12 - 16.
- Environment variables for configuration (This won't work with Apache/mod_wsgi).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    $ mypy gymlog

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd gymlog
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), you'll need to start the celery beat scheduler service. You can start it as a standalone process:

```bash
cd gymlog
celery -A config.celery_app beat
```

or you can embed the beat service inside a worker with the `-B` option (not recommended for production use):

```bash
cd gymlog
celery -A config.celery_app worker -B -l info
```

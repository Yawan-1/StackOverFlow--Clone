## StackOver Flow - Clone

<a href="https://github.com/Yawan-1/StackOverFlow--Clone/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/Yawan-1/StackOverFlow--Clone"></a>
<a href="https://github.com/Yawan-1/StackOverFlow--Clone/blob/master/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/Yawan-1/StackOverFlow--Clone"></a>

A Clone of StackOver Flow, I implemented almost every functionalities, 
I just wanted to notice and show developers how StackOver-Flow works
, do tasks <b style="color:lightgreen">under the hood</b>, how tasks and queries are executing behind the scenes.

## Images

<img src="/images/animation.gif">

## Demo

Here is a working live demo : <a href="https://stonkoverflow.herokuapp.com/">Demo</a>

## Technology Stack

* [Python 3.7.x](https://www.python.org/)
* [Django Web Framework 3.2.x](https://www.djangoproject.com/)
* [Redis 5.x](https://pypi.org/project/django-redis/)
* [BootStrap 4](https://getbootstrap.com/)
* [Jquery 3](https://api.jquery.com/)
* [Postgresql 4](https://www.postgresql.org/)


## Functionalities


* 50+ Badges are implemented to award
* 20 Privileges to Earn
* Reputation Awarding
* Privilege and Activity Notifications
* Live Q&A MarkDown Preview
* User @mentioning in comments
* Create and award Bounties
* <code>Threading</code> to keep track of the remaining days of Bounty.
* Reviewing Tasks :
  * First Question Review
  * First Answer Review
  * Late Answer Review
  * Review Flag Posts
  * Review Flag Comments
  * Review Close Votes
  * Review ReOpen Votes
  * Review Low-Quality Posts
  * Review Suggested Edits


* And much more. You can find list of all functionalities <a href="https://github.com/Yawan-1/StackOverFlow--Clone/blob/759157fc68f59398d9352ddd705eee396336bb81/Functionalities.md">Here</a>


## Setup Commands

Clone this repository

1. Clone this project using
````
$ git clone URL
````

For Postgresql usage*, you will need to download and install it.

1. Download Postgresql from [this Link](https://www.postgresql.org/download/)
2. After installation, create Database in postgresql shell using these commands
   1. `CREATE DATABASE so_clone;`
   2. `CREATE USER so_clone_user WITH PASSWORD 'password';`
   3. `GRANT ALL PRIVILEGES ON DATABASE so_clone TO so_clone_user;`
3. and fill **database name** , **database password** and **user** in `settings.py` like

  ````
  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'so_clone',
        'USER': 'so_clone_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
  ````

_*Note: You can skip postgresql installation if you're setting up this project using sqlite. simply just comment the postgresql configuration and uncomment sqlite configuration_



Now run make <code>migrations</code> command, running make migrations command will perform Data Migrations to save the "Badges" in the database.
then migrate to load the operations of Data Migrations in database.
````
$ python manage.py makemigrations
$ python manage.py migrate
````

Then, simply run the server using this command.
````
$ python manage.py runserver
````

## Deployment

The following details and steps on how to deploy this application

#### Heroku

See detailed [Deploying django app on Heroku](https://devcenter.heroku.com/articles/django-app-configuration)


## Contributing

If you have any question or issues, It may have bugs that i may have missed. You can create <a href="https://github.com/Yawan-1/StackOverFlow--Clone/pulls">Pull request</a> or you can also contact me.




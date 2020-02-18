# Shelter Database

## Presentation

The goal of this application is to list the shelters deployed around the world.

An instance is available [here](https://shelter-database.org).


## Deployment

### Requirements

```bash
$ sudo apt-get install postgresql npm
```


### Configure and install the application

### Database configuration

```bash
$ ./create_db.sh shelter pgsqluser pgsqlpwd
```

### Application

```bash
~/git$ git clone https://github.com/cedricbonhomme/shelter-database.git
~/git$ cd shelter-database/
~/git/shelter-database$ cp src/conf/conf.cfg-sample src/conf/conf.cfg
~/git/shelter-database$ poetry install
~/git/shelter-database$ poetry shell

(shelter-database-JZplA0Yt) ~/git/shelter-database$ npm install

(shelter-database-JZplA0Yt) ~/git/shelter-database$ ./create_db.sh shelter pgsqluser pgsqlpwd
(shelter-database-JZplA0Yt) ~/git/shelter-database$ ./init_db.sh

(shelter-database-JZplA0Yt) ~/git/shelter-database$ python src/runserver.py
* Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

Read the [documentation](/documentation) for more  information about
the deployment of the application.

## Documentation

To generate the documentation in HTML format:

    ./documentation$ sudo pip install sphinx
    ./documentation$ make html

The result will be in the *_build* folder.


## License

This application is under MIT license.


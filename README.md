# weather
Weather service

To run this application, you will need to install Poetry on your machine.

    With poetry, you will enter in the folder, and tipe: poetry install
    It will install all dependencies need of the project
    After that, run poetry shell to enter in the virtualenv created by poetry and run testes and the application
    You'll need to activate the virtualenv. For example, in my machine, the path to active is c:/Users/Victor Fernandes/AppData/Local/pypoetry/Cache/virtualenvs/weather-g9REWXL8-py3.8/Scripts/activate.bat

To test, we will use pytest. To test, just type "pytest" and see the magic.

To run this application, just type "app.py" to run in debug mode, or flask run to run in "production mode".

These application works with three routes, they are:

    /weather/<string:city_name>
        These route can retrieve information for an especific city if exists, or add and retrieve the information if it are not in cache, and update if the cache already expired.

    /weather
        These route can retrieve the "index" where you'll find a form to look for cities by typing the name.
        When a city is submited in the form, it will look in cache, if it still on cache, the application return it, else, it willbe added or updated and retrieved.

    //weather?max=<max_number>
        These route retrieve all information based on a range informated in the querystring param "max" limited by a max of 5 results.

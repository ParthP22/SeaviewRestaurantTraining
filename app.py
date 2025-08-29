# Note from Parth: make sure you exclude this file whenever you push to GitHub from PyCharm.
# We don't want any merge conflicts.



# Note from Parth: I know PyCharm says that these imports aren't being used,
# but you actually need them in order to link the files together.

from SeaviewRestaurantTraining import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
# Note from Parth: make sure you exclude this file whenever you push to GitHub from PyCharm.
# We don't want any merge conflicts.



# Note from Parth: I know PyCharm says that these imports aren't being used,
# but you actually need them in order to link the files together.



from routes import website


if __name__ == '__main__':
    website.run(debug=True)
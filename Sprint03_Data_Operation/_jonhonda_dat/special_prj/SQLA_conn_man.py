#handles creating/connecting to DB and building common session object
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

dbfilename = 'StrBMPModelDB003'

print ("\nClearing old DB")
try:
    os.remove(dbfilename)
except FileNotFoundError as err:
    print ("no need to remove db file")####it's okay if file doesn't exist. ####
engine = create_engine('sqlite:///' + dbfilename, echo = False)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

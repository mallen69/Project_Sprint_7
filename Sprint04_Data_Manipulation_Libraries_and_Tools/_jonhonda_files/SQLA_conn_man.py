#handles creating/connecting to DB and building common session object
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:', echo = False)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

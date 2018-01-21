from sqlalchemy import *
from SQLA_toy_Base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer,  primary_key=True)
    firstname = Column(String(50))
    fullname = Column(String(50))
    password = Column(String(12))

    def __repr__(self): #used in query function to return values of queried fields
        return "<User(id='%s', firstname='%s', fullname='%s', password='%s')>" % (
                                self.id, self.firstname, self.fullname, self.password)

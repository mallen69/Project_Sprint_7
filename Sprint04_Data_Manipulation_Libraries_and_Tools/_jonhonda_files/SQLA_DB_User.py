from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class People(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    ssn = Column(String(12))
    age = Column(Integer)
    locations = relationship("Locations") #setup 1:many relationship. corresponds w/ people_id fk in Locations table

    def __repr__(self):
        return "<People(name='%s', ssn='%s', age='%s')>" % (
                                self.name, self.ssn, self.age)

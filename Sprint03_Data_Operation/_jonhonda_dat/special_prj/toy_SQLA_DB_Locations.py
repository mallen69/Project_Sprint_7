from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Locations(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)
    city = Column(String())
    country = Column(String(100))
    people_id = Column(Integer, ForeignKey('people.id')) #1 persion can have many locations

    def __repr__(self):
        return "<Locations(city='%s', country='%s', people_id='%s')>" % (
                            self.city, self.country, self.people_id)

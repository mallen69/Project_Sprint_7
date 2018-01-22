from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Facility_Types(Base):
    # defines different facility facility_types
    __tablename__ = 'facility_types'
    id = Column(Integer, primary_key=True)
    Fac_Type = Column(String(), unique=True)

    facility_chars = relationship("Facility_Chars") #setup 1:many relationship between table noted in this line, and this class

    # def __repr__(self):
    #     return "<Locations(city='%s', country='%s', people_id='%s')>" % (
    #                         self.city, self.country, self.people_id)

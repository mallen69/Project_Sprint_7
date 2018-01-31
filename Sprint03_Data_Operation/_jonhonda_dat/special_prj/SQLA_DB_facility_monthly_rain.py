from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Facility_Monthly_Rain(Base):
    # table holding monthly rainfall data obtained from the following website: http://rainfall.geography.hawaii.edu/downloads.html
    __tablename__ = 'facility_monthly_rain'
    id = Column(Integer, primary_key=True)
    January = Column(Float) # month's rain depth in inches
    February = Column(Float) # month's rain depth in inches
    March = Column(Float) # month's rain depth in inches
    April = Column(Float) # month's rain depth in inches
    May = Column(Float) # month's rain depth in inches
    June = Column(Float) # month's rain depth in inches
    July = Column(Float) # month's rain depth in inches
    August = Column(Float) # month's rain depth in inches
    September = Column(Float) # month's rain depth in inches
    October = Column(Float) # month's rain depth in inches
    November = Column(Float) # month's rain depth in inches
    December = Column(Float) # month's rain depth in inches
    facility_chars = relationship("Facility_Chars") #setup 1:many relationship between table noted in this line, and this class

    # def __repr__(self):
    #     return "<Locations(city='%s', country='%s', people_id='%s')>" % (
    #                         self.city, self.country, self.people_id)

from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Pollutant_Removal_Rates(Base):
    __tablename__ = 'pollutant_removal_rates'
    id = Column(Integer, primary_key=True)
    r_tss  = Column(Float)
    r_turbidity  = Column(Float)
    r_p  = Column(Float)
    r_n  = Column(Float)
    r_nn  = Column(Float)
    r_an  = Column(Float)
    r_og  = Column(Float)
    r_cu  = Column(Float)
    r_zn  = Column(Float)
    r_fe  = Column(Float)
    r_phmin  = Column(Float)
    r_phmax = Column(Float)

    # facility_risks = relationship("Facility_Risks") #setup 1:many relationship between table noted in this line, and this class


    #
    # def __repr__(self):
    #     return "<Locations(city='%s', country='%s', people_id='%s')>" % (
    #                         self.city, self.country, self.people_id)

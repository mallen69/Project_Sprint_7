from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Existing_Pollutant_Concentrations(Base):
    #table containing existing pollutant concentrations from sampling data or simulated data
    __tablename__ = 'existing_pollutant_concentrations'
    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey('facility_chars.id')) #this field violates our standard that fac_chars should hold all reference table ids.
                                                                    #but other fac_chars reference fields are 1:1. In this case, we can have 1 fac to many ex_poll_Conc records 
    sample_method = Column(String()) #how numbers were obtained: simulated or infield
    sample_point_name = Column(String())
    sample_date = Column(String())
    c_tss = Column(Float)
    c_turbidity = Column(Float)
    c_p = Column(Float)
    c_n = Column(Float)
    c_nn = Column(Float)
    c_an = Column(Float)
    c_og = Column(Float)
    c_cu = Column(Float)
    c_zn = Column(Float)
    c_fe = Column(Float)
    c_phmin = Column(Float)
    c_phmax = Column(Float)

    #
    # def __repr__(self):
    #     return "<Locations(city='%s', country='%s', people_id='%s')>" % (
    #                         self.city, self.country, self.people_id)

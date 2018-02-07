from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class WRS_Pollutant_Risks(Base):
    __tablename__ = 'wrs_pollutant_risks'
    id = Column(Integer, primary_key=True)
    wrs_tss = Column(Float)
    wrs_turbidity = Column(Float)
    wrs_p = Column(Float)
    wrs_n = Column(Float)
    wrs_nn = Column(Float)
    wrs_an = Column(Float)
    wrs_og = Column(Float)
    wrs_cu = Column(Float)
    wrs_zn = Column(Float)
    wrs_fe = Column(Float)
    wrs_phmin = Column(Float)
    wrs_phmax = Column(Float)

    facility_type_has_nel = relationship("Facility_Type_Has_NEL") #setup 1:many relationship between table noted in this line, and this class
<<<<<<< HEAD
=======
    
>>>>>>> 95e8ddb91b9e507052f3593090bd907e5ebf658c

    #
    # def __repr__(self):
    #     return "<Locations(city='%s', country='%s', people_id='%s')>" % (
    #                         self.city, self.country, self.people_id)

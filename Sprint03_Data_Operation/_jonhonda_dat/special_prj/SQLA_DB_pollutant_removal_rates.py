from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship
<<<<<<< HEAD
=======
from sqlalchemy import insert
>>>>>>> 95e8ddb91b9e507052f3593090bd907e5ebf658c

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
<<<<<<< HEAD

    # facility_risks = relationship("Facility_Risks") #setup 1:many relationship between table noted in this line, and this class


    #
    # def __repr__(self):
    #     return "<Locations(city='%s', country='%s', people_id='%s')>" % (
    #                         self.city, self.country, self.people_id)
=======
    combo_bmps = relationship("Combo_BMPs", uselist = False) #setup 1:1 relationship between table noted in this line, and this class

    def __repr__(self):
        return "<Pollutant_Removal_Rates(id='%s',r_tss='%s', r_turbidity='%s', r_p='%s', r_n='%s', r_nn='%s', r_an='%s', r_og='%s', r_cu='%s', r_zn='%s', r_fe='%s', r_phmin='%s', r_phmax='%s')>" % (
        self.id, self.r_tss, self.r_turbidity, self.r_p, self.r_n, self.r_nn, self.r_an, self.r_og, self.r_cu, self.r_zn, self.r_fe, self.r_phmin, self.r_phmax )
>>>>>>> 95e8ddb91b9e507052f3593090bd907e5ebf658c

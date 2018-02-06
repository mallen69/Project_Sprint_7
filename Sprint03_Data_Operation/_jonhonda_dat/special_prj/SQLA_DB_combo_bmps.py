from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Combo_BMPs(Base):
    #table linking combination bmp with its properties
    #for now, just link to removal rates table record
    __tablename__ = 'combo_bmps'
    id = Column(Integer, primary_key=True)
    bmp_fingerprint = Column(String(), unique=True) #-- a unique hashup of the bmp_option_base_component_ids that comprise this bmp option. FORMAT: |bmp_option_base_component_id||bmp_option_base_component_id| w/ id's given in ascending order
    bmp_option_removal_rate_id = Column(Integer, ForeignKey('pollutant_removal_rates.id'), unique=True) #1:1 relationship
    combo_bmp_feasibility_test_results = relationship("Combo_BMP_Feasibility_Test_Results") #setup 1:many relationship between table noted in this line, and this class

    def __repr__(self):
        return "<Combo_BMPs(id='%s', bmp_fingerprint='%s', bmp_option_removal_rate_id='%s')>" % (
                            self.id, self.bmp_fingerprint, self.bmp_option_removal_rate_id)

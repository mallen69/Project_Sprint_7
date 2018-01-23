from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Facility_Risks(Base):
    # --table holding risk estimates for facility (either existing risks or simulated risk reductions
    __tablename__ = 'facility_risks'
    id = Column(Integer, primary_key=True)
    Category_RiskFactor = Column(Float) # factor = 10^riskpower identified in WRS
    Inherent_BaseRisk = Column(Float)
    HousekeepingBMP_BaseRisk = Column(Float)
    SWPlan_BaseRisk = Column(Float) # stormwater plan risk (effectiveness measure) (training, plan development, inspection deficiencies)
    BMPInspectionDeficiency_Rate = Column(Float) # deficient portion of PC bmp INSPECTION, OR 1 (modeled as fully defient) IF NO PC BMP IMPLEMENTED
    wrs_pollutant_limits_id = Column(Integer, ForeignKey('wrs_pollutant_risks.id')) # pollutant limits (either NEL or other) (store in WRS table for convenience)
    wrs_pollutant_concentrations_id = Column(Integer, ForeignKey('wrs_pollutant_risks.id'))# existing pollutant concentrations from sampling data, or modeled (stor in WRS table for convenience)
    wrs_pollutant_risks_id = Column(Integer, ForeignKey('wrs_pollutant_risks.id')) # WRS pollutant risk score components
    wrs_total_risk = Column(Float)
    wrs_pollutant_limits = relationship('WRS_Pollutant_Risks', foreign_keys = [wrs_pollutant_limits_id])
    wrs_pollutant_concentrations = relationship('WRS_Pollutant_Risks', foreign_keys = [wrs_pollutant_concentrations_id])
    wrs_pollutant_risks = relationship('WRS_Pollutant_Risks', foreign_keys = [wrs_pollutant_risks_id])
    facility_chars = relationship("Facility_Chars") #setup 1:many relationship between table noted in this line, and this class




    # def __repr__(self):
    #     return "<Locations(city='%s', country='%s', people_id='%s')>" % (
    #                         self.city, self.country, self.people_id)

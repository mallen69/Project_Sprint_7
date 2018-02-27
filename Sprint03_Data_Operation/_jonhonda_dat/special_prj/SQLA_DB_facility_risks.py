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
    # nel_sample_class_wet_id Column(Integer, ForeignKey('wrs_pollutant_risks.id'))
    # wrs_pollutant_limits_wet_id = Column(Integer, ForeignKey('wrs_pollutant_risks.id')) # wet season pollutant limits (either NEL or other) (store in WRS table for convenience)
    # wrs_pollutant_limits_dry_id = Column(Integer, ForeignKey('wrs_pollutant_risks.id')) # dry season pollutant limits (either NEL or other) (store in WRS table for convenience)
    wrs_pollutant_base_risks_id = Column(Integer, ForeignKey('wrs_pollutant_risks.id')) # Base, normalized WRS pollutant risk score components
    wrs_total_risk = Column(Float)
    dummy_input = Column(Integer) #dummy input used purely during csv import to force importCSV to associate a column/record in another table w/ some column in this table
    # wrs_pollutant_limits = relationship('WRS_Pollutant_Risks', foreign_keys = [wrs_pollutant_limits_wet_id]) #additional information need when multiple fields in a table use the same foreign_key field *(but not necessarily all pointing to same record)
    # wrs_pollutant_limits = relationship('WRS_Pollutant_Risks', foreign_keys = [wrs_pollutant_limits_dry_id]) #additional information need when multiple fields in a table use the same foreign_key field *(but not necessarily all pointing to same record)
    wrs_pollutant_risks = relationship('WRS_Pollutant_Risks', foreign_keys = [wrs_pollutant_base_risks_id]) #additional information need when multiple fields in a table use the same foreign_key field *(but not necessarily all pointing to same record)
    facility_chars = relationship("Facility_Chars") #setup 1:many relationship between table noted in this line, and this class
    combo_bmp_feasibility_test_results = relationship("Combo_BMP_Feasibility_Test_Results", uselist=False) #setup 1:1 relationship between table noted in this line, and this class


    def __repr__(self):
        return "<Facility_Risks(id='%s', Category_RiskFactor='%s', Inherent_BaseRisk='%s', HousekeepingBMP_BaseRisk='%s', SWPlan_BaseRisk='%s', BMPInspectionDeficiency_Rate='%s', wrs_pollutant_base_risks_id='%s', wrs_total_risk='%s')>" % (
        self.id, self.Category_RiskFactor, self.Inherent_BaseRisk, self.HousekeepingBMP_BaseRisk, self.SWPlan_BaseRisk, self.BMPInspectionDeficiency_Rate, self.wrs_pollutant_base_risks_id, self.wrs_total_risk)

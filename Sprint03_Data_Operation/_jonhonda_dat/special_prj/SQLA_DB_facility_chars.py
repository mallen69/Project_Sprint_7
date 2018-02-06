from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Facility_Chars(Base):
    __tablename__ = 'facility_chars'
    id = Column(Integer, primary_key=True)
    Fac_Name = Column(String(), unique=True)
    Permit_Table = Column(String()) #--permit table (1, 1A, 2, or none)
<<<<<<< HEAD
=======
    PBP_Category = Column(String()) #Priority based plan PBP_Category
    NEL_Column = Column(String()) #nel column(s) assigned to this facility.
                                    #*NOTE: purposely not associated w/ NEL_sample_Classes table b/c some facilities are assigned different wet and dry season columns
                                    #which is represented in this table's NEL_Column field as xx & Yyy
>>>>>>> 95e8ddb91b9e507052f3593090bd907e5ebf658c
    existing_facility_risk_id = Column(Integer, ForeignKey('facility_risks.id')) #-- existing facility risk estimate record_id (modeled or from existing data sources)
    facility_monthly_rain_id = Column(Integer, ForeignKey('facility_monthly_rain.id')) #-- facility monthly rainfall records
    facility_type_id = Column(Integer, ForeignKey('facility_types.id'))## facility types as defined in the facility types table
    Fac_Dept = Column(String())
    Fac_Add = Column(String())
    Fac_TMK = Column(String())
    GW_Risk = Column(String())
    Fac_Area = Column(Float)
    Bldg_Area = Column(Float)
    Pave_Area = Column(Float)
    Imperv = Column(Float)
    Tm = Column(Float)
    Runoff_Coeff = Column(Float)
    Length = Column(Float)
    Char_Ground = Column(String())
    Fac_Slope = Column(Float)
    TC = Column(Float)
    CF = Column(Float)
    Q_Peak = Column(Float)
    WQV = Column(Float)
    Des_Storm_Depth = Column(Float)
    Runoff_Coeff2 = Column(Float)
    Imperv2 = Column(Float)
    Fac_Area2 = Column(Float)
    WQFR = Column(Float)
    Runoff_Coeff3 = Column(Float)
    WQ_Intensity = Column(Float)
    Fac_Area3 = Column(Float)
    OP_Shutdown = Column(String())
    Soil_Type = Column(String())
    FP_100_Year = Column(String())
    Num_Ind_DP = Column(Integer)
    Runoff_Type = Column(String())
    Ex_Struct_BMP = Column(String())
    Count_Pipe = Column(Integer)
    Count_Sheet = Column(Integer)
    Count_CB = Column(Integer)
    Count_Chan = Column(Integer)
    Count_DS = Column(Integer)
    Count_TD = Column(Integer)
    OFFSITE_SD_Exist = Column(String())
    Dmg_Pave = Column(Integer)
    TFMR_Exist = Column(String())
    DS_SS_Exist = Column(String())
    Can_Add_SD = Column(String())
    Unpave_Area = Column(Float)
    EM_Area = Column(Float)
    Drainage_Area_Acres = Column(Float)
<<<<<<< HEAD

    # def __repr__(self):
    #     return "<Locations(city='%s', country='%s', people_id='%s')>" % (
    #                         self.city, self.country, self.people_id)
=======
    base_bmp_feasibility_test_results = relationship("Base_BMP_Feasibility_Test_Results") #setup 1:many relationship between table noted in this line, and this class
    combo_bmp_feasibility_test_results = relationship("Combo_BMP_Feasibility_Test_Results") #setup 1:many relationship between table noted in this line, and this class

    def __repr__(self):
        return "<Facility_Chars(id='%s', Fac_Name ='%s')>" % (
                            self.id, self.Fac_Name)
>>>>>>> 95e8ddb91b9e507052f3593090bd907e5ebf658c

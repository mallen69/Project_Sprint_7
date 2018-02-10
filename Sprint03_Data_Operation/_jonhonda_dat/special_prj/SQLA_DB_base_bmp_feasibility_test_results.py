from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Base_BMP_Feasibility_Test_Results(Base):
    __tablename__ = 'base_bmp_feasibility_test_results'
    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey('facility_chars.id'))
    base_bmp_feasibility_test_definitions_id = Column(Integer, ForeignKey('base_bmp_feasibility_test_definitions.id'))
    is_feasible = Column (Integer) #1 for feasibile result, 0 indicates infeasible result

    def __repr__(self):
        return "<Base_BMP_Feasibility_Test_Results(id='%s', facility_id='%s', base_bmp_feasibility_test_definitions_id='%s', is_feasible='%s')>" % (
                self.id, self.facility_id, self.base_bmp_feasibility_test_definitions_id, self.is_feasible)

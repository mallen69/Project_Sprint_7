from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Combo_BMP_Feasibility_Test_Results(Base):
    #store results of evaluating combo bmp feasibility at a facility
    __tablename__ = 'combo_bmp_feasibility_test_results'
    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey('facility_chars.id')) #1:many (1 facility can have many test results: 1 result/bmp)
    combo_bmps_id = Column(Integer, ForeignKey('combo_bmps.id')) #1:many (1 combo_bmp can have many test results: 1 result/facility)
    is_feasible = Column (Integer) #1 indicates feasible bmp, 0 indicates infeasible
    calc_cip_cost = Column (Float) #calculated bmp cip cost for this facility
    calc_om_cost  = Column (Float) #calculated bmp o&m cost for this facility
    facility_risk_id = Column(Integer, ForeignKey('facility_risks.id')) #1:1 (1 facility's combo_bmp can only have 1 risk score)
                                                                        #facility risk estimate record_id (due to applying this combo bmp to this facility)

    def __repr__(self):
        return "<Combo_BMP_Feasibility_Test_Results(id='%s', facility_id='%s', combo_bmps_id='%s', is_feasible='%s',\
            calc_cip_cost='%s', calc_om_cost='%s', facility_risk_id='%s')>" % (
            self.id, self.facility_id, self.combo_bmps_id, self.is_feasible, self.calc_cip_cost, self.calc_om_cost, self.facility_risk_id)

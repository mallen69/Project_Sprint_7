from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Facility_Type_Has_NEL(Base):
    '''
      -- table indicating if a facility type is subject to an effluent limit (either by Priority Based Plan, Table 3, or as City operational assignment)
      -- data is held as a wrs_pollutant_risk record with a 0 or 1 value:
          -- 0 if no effluent limit exists for the facility type
          -- 1 if effluent limit may exist for the facility type
    '''
    __tablename__ = 'facility_type_has_nel'
    id = Column(Integer, primary_key=True)
    facility_type_id = Column(Integer, ForeignKey('facility_types.id'))
    wrs_pollutant_limits_id = Column(Integer, ForeignKey('wrs_pollutant_risks.id'))
    dummy_input = Column(Integer) #dummy input used purely during csv import to force importCSV to associate fac_type w/ WRS_pollutant record

    # def __repr__(self):
    #     return "<People(name='%s', ssn='%s', age='%s')>" % (
    #                             self.name, self.ssn, self.age)

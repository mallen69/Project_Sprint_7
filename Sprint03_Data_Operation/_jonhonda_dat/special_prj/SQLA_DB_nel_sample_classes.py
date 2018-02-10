from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class NEL_Sample_Classes(Base):
    # holds sampling class types (PBP Appendix L). The effluent limits for each class is stored as a wrs_pollutant_risk record
    __tablename__ = 'nel_sample_classes'
    id = Column(Integer, primary_key=True)
    nel_column = Column(String(), unique = True)
    wrs_pollutant_class_id = Column(Integer, ForeignKey('wrs_pollutant_risks.id'))

    def __repr__(self):
        return "<People(name='%s', ssn='%s', age='%s')>" % (
                                self.name, self.ssn, self.age)

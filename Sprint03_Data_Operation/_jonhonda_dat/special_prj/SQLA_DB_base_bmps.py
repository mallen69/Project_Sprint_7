from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Base_BMPs(Base):
    #--table defining bmp technologies
    __tablename__ = 'base_bmps'
    id = Column(Integer, primary_key=True)
    bmp_name = Column(String(), unique=True)
    bmp_removal_rates_id = Column(Integer, ForeignKey('pollutant_removal_rates.id')) #FK reference to bmp removal rates table
    cip_expression_id = Column(Integer, ForeignKey('expressions.id'))
    om_expression_id = Column(Integer, ForeignKey('expressions.id'))
    bmp_size_expression_id = Column(Integer, ForeignKey('expressions.id'))

    def __repr__(self):
        return "<Base_BMPs(id='%s', bmp_name='%s)>" % (
                            self.id, self.bmp_name)

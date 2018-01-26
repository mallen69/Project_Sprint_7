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

    base_bmp_feasibility_test_definitions = relationship("Base_BMP_Feasibility_Test_Definitions") #setup 1:many relationship between table noted in this line, and this class

    cip_expression = relationship('Expressions', foreign_keys = [cip_expression_id])
    om_expression = relationship('Expressions', foreign_keys = [om_expression_id])
    bmp_size_expression = relationship('Expressions', foreign_keys = [bmp_size_expression_id])


    def __repr__(self):
        return "<Base_BMPs(id='%s', bmp_name='%s)>" % (
                            self.id, self.bmp_name)

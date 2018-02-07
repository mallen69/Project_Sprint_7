from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Base_BMP_Feasibility_Test_Definitions(Base):
    #table holding feasibility test definitions for each base bmp
    __tablename__ = 'base_bmp_feasibility_test_definitions'
    id = Column(Integer, primary_key=True)
    feasibility_test_question_id = Column (Integer, ForeignKey('feasibility_test_questions.id'))
    base_bmp_id = Column(Integer, ForeignKey('base_bmps.id')) #FK reference to the base bmp primary key
    base_bmp_feasibility_test_results = relationship("Base_BMP_Feasibility_Test_Results") #setup 1:many relationship between table noted in this line, and this class

    def __repr__(self):
        return "<Base_BMP_Feasibility_Test_Definitions(id='%s', feasibility_test_question_id='%s', base_bmp_id='%s')>" % (
            self.id, self.feasibility_test_question_id, self.base_bmp_id)

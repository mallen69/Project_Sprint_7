from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Feasibility_Test_Questions(Base):
     # table holding feasibility questions for bmp_feasibility_test_results
    __tablename__ = 'feasibility_test_questions'
    id = Column(Integer, primary_key=True)
    feas_id = Column(String(), unique=True) # id used in input sheets to identify the feasibility question
    question_english = Column(String()) # question in plain english_question,
    question_expression_id = Column(Integer, ForeignKey('expressions.id')) # question as an expression (held in expressions table),
    base_bmp_feasibility_test_definitions = relationship("Base_BMP_Feasibility_Test_Definitions") #setup 1:many relationship between table noted in this line, and this class

    def __repr__(self):
        return "<Feasibility_Test_Questions(id='%s', feas_id='%s', question_english='%s', question_expression_id='%s')>" % (
                            self.id, self.feas_id, self.question_english, self.question_expression_id)

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

    # def __repr__(self):
    #     return "<Locations(city='%s', country='%s', people_id='%s')>" % (
    #                         self.city, self.country, self.people_id)

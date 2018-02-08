from sqlalchemy import *
from SQLA_Base import Base
from sqlalchemy.orm import relationship

class Expressions(Base):
    __tablename__ = 'expressions'
    id = Column(Integer, primary_key=True)
    expression_name = Column(String())
    expression_str = Column(String())
    expression_data_type = Column(String())
    vars = Column(BLOB)
<<<<<<< HEAD

    feasibility_test_questions = relationship("Feasibility_Test_Questions") #setup 1:many relationship between table noted in this line, and this class
    # base_bmps = relationship("Base_BMPs") #setup 1:many relationship between table noted in this line, and this class

    # def __repr__(self):
    #     return "<Locations(city='%s', country='%s', people_id='%s')>" % (
    #                         self.city, self.country, self.people_id)
=======
    feasibility_test_questions = relationship("Feasibility_Test_Questions") #setup 1:many relationship between table noted in this line, and this class

    def __repr__(self):
        return "<Expressions(id='%s', expression_name='%s', expression_str='%s', expression_data_type='%s', vars='%s')>" % (
                self.id, self.expression_name, self.expression_str  , self.expression_data_type, self.vars)
>>>>>>> 95e8ddb91b9e507052f3593090bd907e5ebf658c

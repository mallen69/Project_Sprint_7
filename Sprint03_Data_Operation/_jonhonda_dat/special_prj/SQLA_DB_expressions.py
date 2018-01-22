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

    def __repr__(self):
        return "<Locations(city='%s', country='%s', people_id='%s')>" % (
                            self.city, self.country, self.people_id)

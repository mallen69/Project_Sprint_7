'''
specialty csv importers

'''

from sqlalchemy import Column, Integer, String
from sqlalchemy import update, insert
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship #http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#relationship-patterns
from sqlalchemy import inspect

import SQLA_main as SQLA_main #import main SQLAlchemy functions
from SQLA_Base import Base #module containing declarative_base
from SQLA_conn_man import session, engine #module handling db and connection creation

# functions to help with determining function status
# uses funcStatus list:
#func status is list showing func status: [0] = 0 or 1 (0 if fault, 1 if ok)
#                                         [1] = fault description
def isFuncStatusOK (funcStatus):
    #return 0 if fault, 1 if no fault
    return funcStatus[0]

def getFuncStatusFault (funcStatus):
    return funcStatus[1]

def importFeasibilityQuestionsCSV(importFilePath):
    #import CSV file holding feasibility questions. this is a 2 step process:
    # 1. import expression part
    # 2. insert feasibility record w/ assoc. to expression record
    import csv
    import expression as Expr #expression inserting module
    #define csv column constants:
    C_fid_element = 0
    C_english_element = 1
    C_FacAvailableValVar = 2
    C_BMPReqdValVar = 4
    C_expression_element = 5
    print ('Reading csv for import to Feasibility Questions')
    with open(importFilePath, 'rt', encoding='utf-8-sig') as csvfile:
        csvreader = csv.reader(csvfile,dialect='excel')
        # expect and handle 1st row as header row
        rowi = 0
        for row in csvreader:
            if rowi > 0:
                #read expression definition & write expression to expressions table
                Fid = row[C_fid_element]
                print ('\nReading csv record: ' + Fid)
                Question_english = row[C_english_element]
                Question_expression = row[C_expression_element]
                VarDict = {} #init empty VarDict for expression
    #             build variable def. for db_val types, assume val obtained from fac. char table in db_val field, w/ fac_id as unique queryable field
    #             eval type based on type given. expect passed value to be val_type.value
                retStatus = Expr.procInputVarDecs(VarDict, row[C_FacAvailableValVar], 'facility_chars', 'USEDECVAL', 'facility_id', 'FLOAT')
                if isFuncStatusOK(retStatus[0]) == 1: # check if return status ok
                    retStatus= Expr.procInputVarDecs(VarDict, row[C_BMPReqdValVar], 'facility_chars', 'USEDECVAL', 'facility_id', 'FLOAT')
                    VarDict = retStatus[1]
                if isFuncStatusOK(retStatus[0]) == 0: #check if return status ok
                    print (getFuncStatusFault(retStatus[0]) + '    Fix error and retry.')
                else:
                    VarDict = retStatus[1]
        #          now write expression information:
                    expression_id = Expr.registerExpr (Fid, Question_expression, VarDict)
                    #now write feasibility_test_question record:
                    myRecDict = {'feas_id':Fid, 'question_english':Question_english, 'question_expression_id':expression_id}
                    myTable = Base.metadata.tables['feasibility_test_questions']
                    feasibility_test_question_id= SQLA_main.insertupdateRec(myTable, myRecDict, (lambda expr_nameCol, expr_Val: expr_nameCol == expr_Val)(myTable.c['feas_id'], Fid))
            rowi +=1

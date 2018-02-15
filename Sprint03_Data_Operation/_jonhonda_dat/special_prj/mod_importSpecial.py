'''
name: mod_importSpecial.py

specialty csv importers

'''
#IMPORT python:
import csv
#IMPORT custom mods:
import mod_expression as Expr

#IMPORT SQLA:
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
    #import CSV file holding feasibility questions to the feasibility_test_questions Table
    # this is a 2 step process:
    # 1. import expression part
    # 2. insert feasibility record w/ assoc. to expression record
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
                retStatus = Expr.procInputVarDecs(VarDict, row[C_FacAvailableValVar], 'facility_chars', 'USEDECVAL', 'id', 'FLOAT')
                if isFuncStatusOK(retStatus[0]) == 1: # check if return status ok
                    retStatus= Expr.procInputVarDecs(VarDict, row[C_BMPReqdValVar], 'facility_chars', 'USEDECVAL', 'id', 'FLOAT')
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



'''
importer for Base BMP CSV data.
importBaseBMPsCSV function does the work:
  1. imports definitions for cip costs, o&m costs, and BMP sizing to the expressions table
  2. imports pollutant removal rates into pollutant_removal_rates table
  3. creates a record in the base_bmps table using (1) and (2)
  4. for each base bmp, creates a record in the base_bmp_feasibility_test_definitions for each test CSV assigned test.
        (these test definitions are held in the feasibility_test_question Table)
'''
def _HELPER_ImportBaseBMPsCSV_Expr (importLS, row, csvHeadersLS):
    #import expression and variable at current row.
    #call procInputVarDecs, for current record at CSV column var_unit_ColName
    #if no error then register the expr_name expression uwing information at CSV column expr_ColName
    #return imported expression_id

    '''args:
        importLS: information needed for import. elements includes:
                    [UnitCSVColumnName, ExpressionName, ExprStrCSVColumnName, statusStatment]
        row: csv row that we want to import expression from
        csvHeadersLS: list of header names for each csv column. ORDER ASSUMED TO MATCH ROW
    '''
    VarDict = {} #init empty VarDict for expression
    #proce variable declaration. assume variable's value can be found in the facility_chars table
    retStatus = Expr.procInputVarDecs(VarDict, row[csvHeadersLS.index(importLS[0])], 'facility_chars', 'USEDECVAL', 'id', 'FLOAT')
    if isFuncStatusOK(retStatus[0]) == 0: #check if return status ok
        print (getFuncStatusFault(retStatus[0]) + '    Fix error and retry.')
        my_expr_id=-1234
    else:
        my_expr_id = Expr.registerExpr (importLS[1],  row[csvHeadersLS.index(importLS[2])], VarDict)
    return my_expr_id

def importBaseBMPsCSV(importFilePath):
    #define csv column constants:
    C_feastest_StartCol = 19 #1st column holding feasibility test. assume remaining rows are all feasibility tests, identified by column name
    print ('Reading csv for import to base bmp tables')
    with open(importFilePath, 'rt', encoding='utf-8-sig') as csvfile:
        csvreader = csv.reader(csvfile,dialect='excel')
        csvHeadersLS = next(csvreader) # expect and handle 1st row as header row
        for row in csvreader:
            bmp_name = row[csvHeadersLS.index('BMP_Name')] #get BMP name from CSV row
            '''list expression information needed for import
                each element is a list of information for an expression and includes:
                [UnitCSVColumnName, ExpressionName, ExprStrCSVColumnName, statusStatment,
                base_bmp table field name associated w/ this expression]
            '''
            importExprLS = [
                ['CIP_Unit', 'cip_cost_expr_' + bmp_name, 'CIP_Cost_Equation', 'Reading csv cip cost info...', 'cip_expression_id'],
                ['O&M_Unit', 'om_cost_expr_' + bmp_name, 'O&M_Cost_Equation', 'Reading csv o&m cost info...', 'om_expression_id'],
                ['BMP_SIZE_Unit', 'bmp_size_expr_' + bmp_name, 'BMP_SIZE_Equation', 'Reading csv bmp sizing info...', 'bmp_size_expression_id']
                ]
            #use dict. comprehension to represent association between the _HELPER_ImportBaseBMPsCSV returned record_id
            #and a foreign key field name. Dictionary is of form: {foreign_key_field_name:record_id}
            print ('\nReading csv record: ' + bmp_name)

            cip_om_sizeDict = {element[4]: _HELPER_ImportBaseBMPsCSV_Expr(element, row, csvHeadersLS) for element in importExprLS}

            #write pollutant removal rates to pollutant_removal_rates Table
            print ('Reading pollutant removal rate info...')
            pollLS = ['r_tss','r_turbidity','r_og','r_fe','r_cu','r_zn','r_n','r_p','r_nn','r_an','r_phmax'] #list of pollutants corresponding to csv headr names
            myRecDict = {rp:row[csvHeadersLS.index(rp)] for rp in pollLS} #create dictionary of pollutant values by looking up index of header corresponding to pollutant.
            myTable = Base.metadata.tables['pollutant_removal_rates']
            PRR_id= SQLA_main.insertupdateRec(myTable, myRecDict,(lambda expr_nameCol, expr_Val: expr_nameCol == expr_Val)(myTable.c['id'], -1234))

            #we now have information needed to create base_bmp record
            tmpDict = {'bmp_name':bmp_name, 'bmp_removal_rates_id':PRR_id}
            myRecDict = {**tmpDict, **cip_om_sizeDict}
            myTable = Base.metadata.tables['base_bmps']
            mybase_bmp_id = SQLA_main.insertupdateRec(myTable, myRecDict,(lambda x,y: x == y)(myTable.c['bmp_name'], bmp_name))

        #use base bmp record to create bmp_feasibility_test_definition:
            #check that we have base_bmp record:
            if mybase_bmp_id > 0:
                print ('Linking feasibility tests w/ base bmp: ' + str(mybase_bmp_id))
                myTable = Base.metadata.tables['base_bmp_feasibility_test_definitions']
                #'DELETE old feasibility test definitions for the base bmp
                result = session.query(myTable).filter(myTable.c['base_bmp_id'] == mybase_bmp_id).delete(synchronize_session = False)
                print ('Removed: ', result, ' old feasibility test defs for the base bmp')
                #if feas test at csv column is not N/A then add record
                for csvCol in range(C_feastest_StartCol, len(row)):
                    if row[csvCol] != 'N/A':
                        ftq_id = session.query(Base.metadata.tables['feasibility_test_questions'].c['id']).filter(Base.metadata.tables['feasibility_test_questions'].c['feas_id'] == csvHeadersLS[csvCol]).first()
                        if ftq_id is None:
                            print ('!!!!WARNING!!!! No record for feas_id: ', csvHeadersLS[csvCol], ' in Feasibility_Test_Questions table. Skipping...')
                        else:
                            myRecDict = {'feasibility_test_question_id':ftq_id[0], 'base_bmp_id':mybase_bmp_id}
                            myRecID = SQLA_main.insertupdateRec(myTable,myRecDict,(lambda x,y: x == y)(myTable.c['id'],-1234))
                            print ('Added feasibility test def as record: ', myRecID)

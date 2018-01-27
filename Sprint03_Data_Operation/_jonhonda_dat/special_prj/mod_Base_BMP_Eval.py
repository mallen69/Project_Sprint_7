'''
Name: BASE_BMP_Eval.py
evaluate Base BMPs (feasibility and costs)

'''
#IMPORT python:

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
#Table definitions as SQLA classes:
from SQLA_DB_base_bmp_feasibility_test_results import Base_BMP_Feasibility_Test_Results as BBFTR
from SQLA_DB_base_bmp_feasibility_test_definitions import Base_BMP_Feasibility_Test_Definitions as BBFTD
from SQLA_DB_base_bmps import Base_BMPs
from SQLA_DB_expressions import Expressions
from SQLA_DB_facility_chars import Facility_Chars
from SQLA_DB_feasibility_test_questions import Feasibility_Test_Questions as FTQ
Base.metadata.create_all(engine, checkfirst=True) #create SQLA classes

######################################### FEASIBILITY EVALUATORS #####################################################################
#EVALUATE base_bmp feasibility:
def is_base_bmp_feasible(myFacility, aBMP):
    #use PREVIOUSLY CALCULATED db feasibility data to determine if base bmp is feasible for the given facility.
    print ('Determine feasibility of base bmp: ' + aBMP.bmp_name + '  at Facility: ' + myFacility.Fac_Name)
    '''need joint data from Tables:
                    BBFTD: base_bmp_feasibility_definitions
                    BBFTR: base_bmp_feasibility_test_results
                    FTQ: facility_test_questions
        joins:  BBFTR.base_bmp_feasibility_definition_id == BBFTD.id
                BBFTD.feasibility_test_question_id == FTQ.id
                BBFTR.facility_id == myFacility.id
                BBFTD.base_bmp_id == aBMP.id
    '''
    Tests = session.query(BBFTR.is_feasible, FTQ.feas_id).filter(BBFTR.base_bmp_feasibility_test_definitions_id == BBFTD.id).filter(
                        BBFTD.feasibility_test_question_id == FTQ.id).filter(
                        BBFTR.facility_id == myFacility.id).filter(BBFTD.base_bmp_id == aBMP.id)
    is_bb_feasible = 1 #start w/ bmp feasibility as true (necessary start condition for bool and ops to work correctly)
    for Test in Tests:
        print ('  Test Question ID: ', Test.feas_id, ' Test Result: ', Test.is_feasible)
        is_bb_feasible = is_bb_feasible * Test.is_feasible #bool op to determine bmp feasibility
    print ('  Result: ' + str(bool(is_bb_feasible)))
    return is_bb_feasible

def Eval_base_bmp_feasibility_tests(myFacility, myBaseBMP):
    #evaluate feasibility tests for a single facility in facility_char table & a single base_bmp from the base_bmps table
    for row in session.query(BBFTD.feasibility_test_question_id, FTQ.question_expression_id, BBFTD.id).filter(
        BBFTD.feasibility_test_question_id == FTQ.id).filter(BBFTD.base_bmp_id == myBaseBMP.id):
        #build QryOnUnqFieldValsDict:
        print ('\n  Attempting eval of feasibility_test ID: ', row.feasibility_test_question_id)
        QryOnUnqFieldValsDict = {'facility_chars.id': myFacility.id,
                                 'base_bmps.bmp_name':myBaseBMP.bmp_name} #bmp_name is needed b/c the test's expression may be unique to a particular bmp
        #get expression record for the question_expression:
        myExpr = session.query(Expressions).filter(Expressions.id == row.question_expression_id)
        if myExpr.first() is not None: #then record retrieved
#             print (myExpr.first())
            is_feasible = bool(Expr.EvalExpr(myExpr.first(), QryOnUnqFieldValsDict))
            print ('  Writing to DB Feasibility Test Result: ' + str(is_feasible) + '(' + str(int(is_feasible)) + ')')
            #insert/update feasibility test result:
            myTable = Base.metadata.tables['base_bmp_feasibility_test_results']
            recID = SQLA_main.insertupdateRec(myTable, {'facility_id':myFacility.id,
                                         'base_bmp_feasibility_test_definitions_id':row.id,
                                        'is_feasible':is_feasible},
                                (myTable.c['facility_id'] == myFacility.id) &
                                 (myTable.c['base_bmp_feasibility_test_definitions_id'] == row.id))
            q = session.query(BBFTR, BBFTD).filter(BBFTR.id == recID).filter(BBFTR.base_bmp_feasibility_test_definitions_id == BBFTD.id)
            print ('  Wrote to base_bmp_feasibility_test_results as recordID: ' + str(recID))
#             KEEP FOR DEBUGGING print ('  Here is a record of what was written: ', q.first())
        else:
            print ('!!!! FAULT! expression_id: ' + row[1] + ' not found in expressions table. this should not happen.')
            return False


#############################################COST EVALUATOR################################################
#evaluate base bmp cip and o&m costs
def evalFacility_BaseBMPCosts(myFacility):
    #for the given facility, compute base bmp costs only if base bmp is feasible at facility
    #return dictionary of cip and om costs for feasibile base bmps. Format:
        #{key = base_bmp_id: [cip_cost, om_cost]}
        #cost list is defaulted as none values. remains none until overwritten by evaluation result. remains none if no result obtained. useful for detecting undefined conditions
    print ('\nEvaluating base bmp costs at Facility: ' + myFacility.Fac_Name)
    myBMPs = session.query(Base_BMPs)
    CostDict = {}
    for aBMP in myBMPs:
        QryOnUnqFieldValsDict = {'facility_chars.id': myFacility.id,
             'base_bmps.bmp_name': aBMP.bmp_name} #bmp_name is needed b/c the test's expression may be unique to a particular bmp
        if is_base_bmp_feasible(myFacility, aBMP):
            print ('base bmp: ' + aBMP.bmp_name + '  at Facility: ' + myFacility.Fac_Name + ' is feasible. estimate costs:')
            CostLS = [None,None] #use None as the defaults in cost list
            print ('  Estimate CIP costs:')
            myExpr = session.query(Expressions).filter(Expressions.id == aBMP.cip_expression_id)
            if myExpr.first() is not None:
                CostLS[0] = Expr.EvalExpr(myExpr.first(), QryOnUnqFieldValsDict) #write cip cost to cost list
                print ('CIP Cost: ' + str(CostLS[0]))
            print ('  Estimate O&M costs:')
            myExpr = session.query(Expressions).filter(Expressions.id == aBMP.om_expression_id)
            if myExpr.first() is not None:
                CostLS[1] = Expr.EvalExpr(myExpr.first(), QryOnUnqFieldValsDict) #write om cost to cost list
                print ('O&M Cost: ' + str(CostLS[1]))
            CostDict[aBMP.id] = CostLS #write cip and om costs to bmp entry in cost dictionary
    return CostDict

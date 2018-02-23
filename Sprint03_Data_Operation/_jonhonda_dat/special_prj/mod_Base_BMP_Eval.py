'''
Name: mod_BASE_BMP_Eval.py
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
def is_base_bmp_feasible(myFacility_ID, aBMP):
    #use PREVIOUSLY CALCULATED db feasibility data to determine if base bmp is feasible for the given facility.
    # print ('Determine feasibility of base bmp: ' + aBMP.bmp_name + '  at Facility: ' + myFacility_ID.Fac_Name)
    '''need joint data from Tables:
                    BBFTD: base_bmp_feasibility_definitions
                    BBFTR: base_bmp_feasibility_test_results
                    FTQ: facility_test_questions
        joins:  BBFTR.base_bmp_feasibility_definition_id == BBFTD.id
                BBFTD.feasibility_test_question_id == FTQ.id
                BBFTR.facility_id == myFacility_ID
                BBFTD.base_bmp_id == aBMP.id
    '''
    Tests = session.query(BBFTR.is_feasible, FTQ.feas_id).filter(BBFTR.base_bmp_feasibility_test_definitions_id == BBFTD.id).filter(
                        BBFTD.feasibility_test_question_id == FTQ.id).filter(
                        BBFTR.facility_id == myFacility_ID).filter(BBFTD.base_bmp_id == aBMP.id)
    is_bb_feasible = 1 #start w/ bmp feasibility as true (necessary start condition for bool and ops to work correctly)
    for Test in Tests:
        # print ('  Test Question ID: ', Test.feas_id, ' Test Result: ', Test.is_feasible)
        is_bb_feasible = is_bb_feasible * Test.is_feasible #bool op to determine bmp feasibility
    # print ('  Result: ' + str(bool(is_bb_feasible)))
    return is_bb_feasible

def Eval_base_bmp_feasibility_tests(myFacility_ID, myBaseBMP, ShowCalculations):
    #evaluate feasibility tests for a single facility in facility_char table & a single base_bmp from the base_bmps table
    #put evaluation results into the base_bmp_feasibility_test_results table
    for row in session.query(BBFTD.feasibility_test_question_id, FTQ.question_expression_id, BBFTD.id).filter(
        BBFTD.feasibility_test_question_id == FTQ.id).filter(BBFTD.base_bmp_id == myBaseBMP.id):
        #build QryOnUnqFieldValsDict:
        if ShowCalculations: print ('\n  Attempting eval of feasibility_test ID: ', row.feasibility_test_question_id)
        QryOnUnqFieldValsDict = {'facility_chars.id': myFacility_ID,
                                 'base_bmps.bmp_name':myBaseBMP.bmp_name} #bmp_name is needed b/c the test's expression may be unique to a particular bmp
        #get expression record for the question_expression:
        myExpr = session.query(Expressions).filter(Expressions.id == row.question_expression_id)
        if myExpr.first() is not None: #then record retrieved
#             print (myExpr.first())
            is_feasible = bool(Expr.EvalExpr(myExpr.first(), QryOnUnqFieldValsDict, ShowCalculations))
            if ShowCalculations: print ('  Writing to DB Feasibility Test Result: ' + str(is_feasible) + '(' + str(int(is_feasible)) + ')')
            #insert/update feasibility test result:
            myTable = Base.metadata.tables['base_bmp_feasibility_test_results']
            recID = SQLA_main.insertupdateRec(myTable, {'facility_id':myFacility_ID,
                                         'base_bmp_feasibility_test_definitions_id':row.id,
                                        'is_feasible':is_feasible},
                                (myTable.c['facility_id'] == myFacility_ID) &
                                 (myTable.c['base_bmp_feasibility_test_definitions_id'] == row.id))
            q = session.query(BBFTR, BBFTD).filter(BBFTR.id == recID).filter(BBFTR.base_bmp_feasibility_test_definitions_id == BBFTD.id)
            if ShowCalculations: print ('  Wrote to base_bmp_feasibility_test_results as recordID: ' + str(recID))
#             KEEP FOR DEBUGGING print ('  Here is a record of what was written: ', q.first())
        else:
            if ShowCalculations: print ('!!!! FAULT! expression_id: ' + row[1] + ' not found in expressions table. this should not happen.')
            return False


#############################################COST EVALUATOR################################################
#evaluate base bmp feasibiilty, cip and o&m costs
def evalFacility_BaseBMP(myFacility_ID, ShowCalculations=None):
    '''
    for each bmp at the given facility;
        use feasibility test results to evaluate base bmp feasibility at the facility_id
        compute base bmp costs only if base bmp is feasible at facility
    #return list of dictionaries. 1 dict per bmp: bmp_id, feasibility, cip and om costs for feasibile base bmps. Format:
        #[{base_bmp_id:val, base_bmp_name:val, is_feasible:val, calc_cip_cost:val, calc_om_cost:val},{base_bmp_id:val, is_feasible:val, calc_cip_cost:val, calc_om_cost:val}]
        #costs in list is defaulted as none values. remains none until overwritten by evaluation result. remains none if no result obtained. useful for detecting undefined conditions

    #ShowCalculations: optional variable. if True, then show steps, if false, then hide printouts, if None, then assume show steps
    '''
    if ShowCalculations is None:#value not passed, then default to printing steps
        ShowCalculations = True
    if ShowCalculations:
        session.query(Facility_Chars.Fac_Name).filter(Facility_Chars.id == myFacility_ID).first()
        print ('\nEvaluating base bmps for Facility: ' + session.query(Facility_Chars.Fac_Name).filter(Facility_Chars.id == myFacility_ID).first()[0])
    myBMPs = session.query(Base_BMPs)
    retLS=[]
    for aBMP in myBMPs:
        QryOnUnqFieldValsDict = {'facility_chars.id': myFacility_ID,
             'base_bmps.bmp_name': aBMP.bmp_name} #bmp_name is needed b/c the test's expression may be unique to a particular bmp
        tmpDict = {'Facility_ID':None,'base_bmp_id':None,'base_bmp_name':None, 'is_feasible': False, 'calc_cip_cost': None, 'calc_om_cost': None} #make temp dictionary from template
        tmpDict['Facility_ID'] = myFacility_ID
        tmpDict['base_bmp_id'] = aBMP.id
        tmpDict['base_bmp_name'] = aBMP.bmp_name
        tmpDict['is_feasible'] = is_base_bmp_feasible(myFacility_ID, aBMP)
        if tmpDict['is_feasible']: #if base bmp is feasibile, then calculate costs
            # print ('base bmp: ' + aBMP.bmp_name + '  at Facility: ' + myFacility_ID.Fac_Name + ' is feasible. estimate costs:')
            if ShowCalculations: print ('  Estimate CIP costs:')
            myExpr = session.query(Expressions).filter(Expressions.id == aBMP.cip_expression_id)
            if myExpr.first() is not None:
                 tmpDict['calc_cip_cost']= Expr.EvalExpr(myExpr.first(), QryOnUnqFieldValsDict, ShowCalculations) #write cip cost to cost list
                # print ('CIP Cost: ' + str(retLS[1]))
            if ShowCalculations: print ('  Estimate O&M costs:')
            myExpr = session.query(Expressions).filter(Expressions.id == aBMP.om_expression_id)
            if myExpr.first() is not None:
                tmpDict['calc_om_cost'] = Expr.EvalExpr(myExpr.first(), QryOnUnqFieldValsDict, ShowCalculations) #write om cost to cost list
                # print ('O&M Cost: ' + str(retLS[2]))
        retLS.append(tmpDict)
    return retLS

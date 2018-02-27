'''
Name: mod_expression.py
routines to help insert expressions to the database and evaluate expressions
 NOTES ON INSERTION:


 NOTES ON EVALUATION:
  THERE IS A COUNTER FOR EVAL ERRORS!
  SEE BELOW FOR RETRIEVING ERROR COUNT AND RESETTING IT.

'''
#IMPORT python:
import csv
#IMPORT custom mods:


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
from SQLA_DB_expressions import Expressions
Base.metadata.create_all(engine, checkfirst=True) #create SQLA classes

def procInputVarDecs (VarDict, VarDecStr, WriteToTable, WriteToField, QryOnUniqueField, DataType):
#function to process variable declarations;
# return tuple: (funcStatus, VarDict)
#func status is list showing func status: [0] = 0 or 1 (0 if fault, 1 if ok)
#                                         [1] = fault description
# VarDict is the dictionary object that we will write to and return
# use the project standard VarDict:
#    key = var name: [VarName, VarType, StoredTable, StoredField, QryOnUniqueField, DataType]
# VarDecStr is the string holding the csv variable declaration
#   expected format: var_type DELIMITER val
#           var_type: val; exp; dxp; val
#           DELIMITER: |
#           DECval:      var name; expr name; dynamic expr format:
#                dynamic_expr_format: dyn expr name(exprID_tablename~exprID_fieldname~unqFieldName)
#                identifies what table and field name holds reference to the expression_id, and the unique field  of the table that identifies the record.


# WriteToTable & WriteToField are the table and field db_var type variable can be found at
# QryOnUniqueField is field that we should query on when trying to retrieve val from db table and db field
    funcStatus = [1,''] #start with okay status
    DELIMITER = '|'
    mySplitter = VarDecStr.split(DELIMITER) #split declaration into its 2 parts
    if len(mySplitter) != 2:
        if mySplitter[0] == 'N/A':
            return (funcStatus,VarDict)
        funcStatus = [0,'!!!!FAULT in procInputVarDecs: VarDecStr missing 2 parts: ' + str(VarDecStr)]
        return (funcStatus,VarDict)
    if WriteToField == 'USEDECVAL': #use declaration value as name for writing field
        WriteToField = mySplitter[1]
    if mySplitter[0] == 'var': #then it's value is held in the database
        VarDict =  _add2VarDict(VarDict, mySplitter[1], 'val', WriteToTable,WriteToField, QryOnUniqueField, DataType)
    elif mySplitter[0] == 'exp': #then it's value is defined by a static database held expression
        VarDict =  _add2VarDict(VarDict, mySplitter[1], 'exp', 'expressions','expression_str', 'id', DataType)
    elif mySplitter[0] == 'dxp': #then it's value is defined by a dynamically defined expression
        FullVarName = mySplitter[1] #'dyn expr name(exprID_tablename~exprID_fieldname~unqFieldName)'
        ParamPart = FullVarName[FullVarName.find('('):] #slice string to just the Parameter part, including open and close parens,
        ParamPart = ParamPart[1:len(ParamPart)-1] #revise ParamPart to exclude open and close parens
        ParamSplitter = ParamPart.split('~')
#         dyn_expr_name = initstr[:len(initstr)-len(ParamPart)]
#         print ('my dxp: ' + dyn_expr_name)
        VarDict =  _add2VarDict(VarDict, FullVarName, 'dxp', ParamSplitter[0],ParamSplitter[1], ParamSplitter[2], DataType)
    elif mySplitter[0] != 'val': #the only other possible dec type is val. fault if not val
        funcStatus = [0,'!!!!FAULT in procInputVarDecs: Unknown var_type: ' + str(mySplitter[0])]
        return (funcStatus,VarDict)
    return (funcStatus,VarDict)

def _add2VarDict (VarDict, VarName, VarType, StoredTable, StoredField, QryOnUniqueField, DataType):
# function to add variable definition to the given dictionary of variables
# use the project standard VarDict:
#    key = var name: [VarName, VarType, StoredTable, StoredField, QryOnUniqueField, DataType]
    # print('Adding to variable dictionary: ' + VarName)
    defList = [VarName, VarType, StoredTable, StoredField, QryOnUniqueField, DataType] #variable definition list
    key = VarName
    VarDict.update({key: defList})
    return VarDict

def registerExpr (expression_name, expression_str, VarDict):
#function to register expressions in db.
#provide expression Str and var dict object
# assume any expressions in bar dict are already registered.
#Return expression id
#determine if expression is in table
    import os
    import pickle
#     print ('Registering expression: ' + expression_name + '=' + expression_str)
# Pickle the 'data' dictionary using the highest protocol available.
# use the dumps command to write pickle to a string
    pickled_VarDict = pickle.dumps(VarDict, pickle.HIGHEST_PROTOCOL) ####uses the latest pickling version
#insert/update expression record, depending on if vars has data or not (if not, then it's assumed to be a const. val):
    if len(VarDict) >0:
        myRecDict = {'expression_name':expression_name,'expression_str':expression_str,'expression_data_type':'FLOAT','vars':pickled_VarDict}
    else:
        myRecDict = {'expression_name':expression_name, 'expression_str':expression_str,'expression_data_type':'FLOAT'}
    myTable = Base.metadata.tables['expressions']
    expression_id = SQLA_main.insertupdateRec(myTable, myRecDict, (lambda expr_nameCol, expr_nameVal: expr_nameCol == expr_nameVal)(myTable.c['expression_name'], expression_name))
    return expression_id

################EXPRESSION EVALUATOR:
import pickle
#### DEFINE GLOBALLY SCOPED CONSTANTS TO HELP UNDERSTAND WHAT ARRAY ELEMENT WE'RE ACCESSING:
C_VarDict_VarName = 0 #### Constant for Var Dict Key
#### Constants for Var Dict Array:
# use the project standard VarDict:
#    key = var name: [VarName, VarType, StoredTable, StoredField, QryOnUniqueField, DataType]
C_VarDict_VarName = 0
C_VarDict_VarType = 1
C_VarDict_StoredTable = 2
C_VarDict_StoredField = 3
C_VarDict_QryOnUniqueField = 4
C_VarDict_DataType = 5

_EVAL_ERROR_COUNT = 0

def ResetEvalErrorCount():
    #RESET ERROR COUNTER TO 0
    global _EVAL_ERROR_COUNT
    _EVAL_ERROR_COUNT = 0

def _IncrementEvalErrorCount():
    #increment counter
    global _EVAL_ERROR_COUNT
    _EVAL_ERROR_COUNT += 1

def CountEvalErrors():
    #return number of errors that occured during evaluating an expression since the last error count reset
    global _EVAL_ERROR_COUNT
    return _EVAL_ERROR_COUNT

def EvalExpr(myExpression, QryOnUnqFieldValsDict, ShowCalculations = None): #### pass in expression record as a sqlalchemy query record
    #myExpression: the expression record (a sqla query result) that we want to evaluate
    #QryOnUnqFieldValsDict: dictionary of table-fieldname and values that we should use in queries to obtain
    #values we should use in evaluating myExpression.
    #FORMAT:
        #{key = table.fieldname: item = unique value}
        #this allows us to define, for example, the unique facility and base-bmp pair to query for:
            #{facility_chars.facility_id: 2,
            # base_bmps.bmp_name: 'hydrodynamic_separator'
            #}
    #ShowCalculations: optional variable. if True, then show steps, if false, then hide printouts, if None, then assume show steps
    if ShowCalculations is None: #value not passed, then default to printing steps
        ShowCalculations = True
    if myExpression.vars is None: #will be NoneType if no vars are a part of this expression record (expression is probably a constant)
#         print ('empty')
        Vars= {} #make empty vars dictionary
    else:
        Vars = pickle.loads(myExpression.vars) #unpickle to Vars variable (Dictionary type)
    if ShowCalculations: print('proccessing expression: ' +  myExpression.expression_name + '=' + myExpression.expression_str)
    myExprStr = myExpression.expression_str
    for aVar in Vars.items(): #iterate thru each Var in Vars, replacing procstr's Var instances w/ Var's value
        myExprStr = myExprStr.replace(aVar[C_VarDict_VarName],_getVal(aVar,QryOnUnqFieldValsDict, ShowCalculations))
    try:
        myVal = eval(myExprStr)
    except Exception as e:
        if ShowCalculations: print ('  FAULT!!!! Error occured while evaluating expression: ', myExprStr, ': ', e)
        if ShowCalculations: print ('  I will set evaluation to NoneType')
        _IncrementEvalErrorCount() #INCREMENT EVALUATION ERROR COUNTER
        myVal = None
    if ShowCalculations: print ('  eval(' + str(myExprStr) + ')=' + str(myVal))
    return myVal

def _getVal(aVar, QryOnUnqFieldValsDict, ShowCalculations = None): #retrieve DB value, or call expression evaluation of passed variable (expects tuple of expression Query)
    #QryOnUnqFieldValsDict: dictionary of the value that value obtaining query should query against. FORMAT:
        #{key = table.fieldname: item = unique value}
        #this allows us to define, for example, the unique facility and base-bmp pair to query for:
            #{facility_chars.facility_id: 2,
            # base_bmps.bmp_name: 'hydrodynamic_separator'
            #}
    #ShowCalculations: optional variable. if True, then show steps, if false, then hide printouts, if None, then assume show steps
    if ShowCalculations is None: #value not passed, then default to printing steps
        ShowCalculations = True
    if ShowCalculations: print('    attempting to retrieve value for: ', aVar)
    strdbVal = 'fault_if_still_this'
    #unpack serialized data:
    dbTableName = aVar[1][C_VarDict_StoredTable]
    dbFieldName = aVar[1][C_VarDict_StoredField]
    dbQryOnUniqueField = aVar[1][C_VarDict_QryOnUniqueField]
    UnqFieldValsDict_Key = dbTableName + '.' + dbQryOnUniqueField

    if aVar[1][C_VarDict_VarType] == 'val': #### value is housed somewhere in database. get value
        #find matching table-field in QryOnUnqFieldValsDict:
        try:
            QryOnUniqueFieldVal = QryOnUnqFieldValsDict[UnqFieldValsDict_Key]#[dbTableName + '.' + dbFieldName]
        except KeyError:
            if ShowCalculations: print ('     FAULT!!!! While evaluating the expression, I came upon a variable whos querying table name + field name: ', UnqFieldValsDict_Key,
            ' was not included with the passed QryOnUnqFieldValsDict: ', QryOnUnqFieldValsDict, '.  I would have given it the key: ', UnqFieldValsDict_Key)
            return strdbVal
        myTable = Base.metadata.tables[dbTableName]
        myQrys = session.query(myTable.c[dbFieldName]).filter(myTable.c[dbQryOnUniqueField] == QryOnUniqueFieldVal)
        if myQrys.first() is not None: #handle empty record
            dbVal = myQrys.first()[0] #### return record as value
            if type(dbVal) == str:
                strdbVal = '\'' + dbVal + '\'' #encapsulate in quotes so python eval reads as str and not var
            else: #assume numeric
                strdbVal = str(dbVal) #### cast to string
            if ShowCalculations: print('       QUERY RESULT: ' + aVar[C_VarDict_VarName] + '=' + strdbVal)

    elif aVar[1][C_VarDict_VarType]=='exp':
        if ShowCalculations: print ('      This is an expression. Prepare to re-enter EvalExpr...')
        #get expression record for the question_expression:
        myExpr = session.query(Expressions).filter(Expressions.expression_name == aVar[C_VarDict_VarName])
        if myExpr.first() is not None: #then record retrieved
            dbVal = myQrys.first() #### return record as value
            if ShowCalculations: print('       Reentering EvalExpr....')
            strdbVal = str(EvalExpr(dbVal,ShowCalculations)) #### cast to string<--there may be an error here. dbVal is a tuple?

    elif aVar[1][C_VarDict_VarType]=='dxp':
    #                dynamic_expr_format: dyn expr name(exprID_tablename~exprID_fieldname~unqFieldName)
    #                identifies what table and field name holds reference to the expression_id, and the unique field  of the table that identifies the record.
        if ShowCalculations: print ('     This is a dynamic expression. Query for static expression using provided unique identifiers')
        UnqFieldValsDict_Key = dbTableName + '.' + dbQryOnUniqueField
        #get ready to query for expression id:
        #get unique value to query on:
        try:
            QryOnUniqueFieldVal = QryOnUnqFieldValsDict[UnqFieldValsDict_Key]#[dbTableName + '.' + dbFieldName]
        except KeyError:
            if ShowCalculations: print ('     FAULT!!!! While evaluating expression: DB stored table name + field name: ' + dbTableName + '.' + dbFieldName + ' for the var was not included with QryOnUnqFieldValsDict')
            return strdbVal

        myTable = Base.metadata.tables[dbTableName]
        myQrys = session.query(myTable.c[dbFieldName]).filter(myTable.c[dbQryOnUniqueField] == QryOnUniqueFieldVal)
        if myQrys.first() is not None: #handle empty record
            #now query for static expression record:
            myExpr = session.query(Expressions).filter(Expressions.id == myQrys.first()[0])
            if ShowCalculations: print ('       dynamic expression: ' + aVar[0] + ' = ' + ' static expression: ' + myExpr.first().expression_name)
            if ShowCalculations: print ('       Reentering EvalExpr...')
            strdbVal = str(EvalExpr(myExpr.first(), QryOnUnqFieldValsDict,ShowCalculations))
        else:
                if ShowCalculations: print ('     FAULT!!!! While evaluating expression: DB stored table name + field name: ' + dbTableName + '.' + dbFieldName + ' dxp expression query has no record')
    else:
        if ShowCalculations: print (strdbVal)
    return strdbVal

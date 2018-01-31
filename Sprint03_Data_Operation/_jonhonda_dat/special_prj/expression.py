'''
Name: expression.py
routines to help insert expressions to the database and evaluate expressions

'''

from sqlalchemy import Column, Integer, String
from sqlalchemy import update, insert
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship #http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#relationship-patterns
from sqlalchemy import inspect

import SQLA_main as SQLA_main #import main SQLAlchemy functions
from SQLA_Base import Base #module containing declarative_base
from SQLA_conn_man import session, engine #module handling db and connection creation

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
        VarDict =  _add2VarDict(VarDict, mySplitter[1], 'exp', 'expressions','expression_str', 'expression_id', DataType)
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
    print('Adding to variable dictionary: ' + VarName)
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

'''
name: importCSV.py
Main Routine: importCSV

import records in a csv file where csv columns belong to one or more tables.
The routine uses csv column names (form: TABLENAME.FIELDNAME) to identify what table and filed the particular datavalue should be inserted/updated to
Routine determines wheter to insert or update record using a sqlAlchemy Where clause passed into the function as a dictionary of {TAbleName: Lambda WHere Clause}
Routine will do primary key-foreign key id association for necessary table records using sqlAlchemy's database SCHEMA
'''
#IMPORT python:
import csv


#IMPORT custom mods:


#IMPORT SQLA:emy import Column, Integer, String
from sqlalchemy import update, insert
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship #http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#relationship-patterns
from sqlalchemy import inspect

import SQLA_main as SQLA_main #import main SQLAlchemy functions
from SQLA_Base import Base #module containing declarative_base
from SQLA_conn_man import session, engine #module handling db and connection creation

def _HELPER_MakeNoneType(val):
    #make none type if passed value matches an acceptable type (for now, just 'None'):
    if val == 'None':
        return None
    else:
        return val

def _HELPER_importCSVrow(headersDict, CSVrow, updateWhereLF = False):
    #importCSV helper function to handle inserting a single CSV row
        #headersDict: dictionary of form: {table.field:[table,field]}
        #CSVrow: single row of a csv reader loop
            #replace 'None' string with NoneType
        #updateWhereLF:where Clause as a lambda function to pass to insert/updater to determinE record existance
                        #False to force insert
    #return primary keys inserted/updated using CSVrow values
    C_TABLE = 0 #header 0th element is table name
    C_FIELD = 1 #header 1st element is field name
    myTempRecDicts = {aheader[C_TABLE]:{} for aheader in headersDict.values()} #initialize dictionary of tables #and their associated list of  records. note the empty dict. needed b/c we will update that empty dict
    for aheader, avalue in zip(headersDict.values(),CSVrow): #write current header-value pair to a temp dictionary
        mytmpDict = {aheader[C_FIELD]:_HELPER_MakeNoneType(avalue)}
        myTempRecDicts[aheader[C_TABLE]].update(mytmpDict) #place temp dictionary value into current rec's dictionary of tables an assoc. header-values
    myRowRecDict={} #dictionary of record ids inserted/updated for current row: {PKName:PK_ID}
    for myTableName,myRecDict in myTempRecDicts.items():
        #insert table and record's return primary
        myTable = Base.metadata.tables[myTableName]
        PKLS = SQLA_main.getPKFieldNames(myTable)#get primary key field for myTable
        if updateWhereLF==False or updateWhereLF[myTableName] == False:#force insert (update if PKid==-1234 which can't happen)
            PKCol = myTable.c[PKLS] #get sqlAlchemy object for PK Field
            rec_id =  SQLA_main.insertupdateRec(myTable, myRecDict, (lambda PKid: PKid == -1234)(PKCol))
        else: #use where clause lambda function to evaluate insert/update
            rec_id =  SQLA_main.insertupdateRec(myTable, myRecDict, updateWhereLF[myTableName](myRecDict))
        myRowRecDict.update({myTableName + '.' + PKLS:rec_id}) #add PK id to record of rows added
    return myRowRecDict

def _HELPER_assocKEYS(myRecsLS, tablesLS):
    #helper function to associate primary-foreign key pairings during importCSV of mixed tables:
        #retrieves pk-fk relationships from sqlAlchemy's schema for tables mentioned in at least 1 CSV column name (passed in as tablesLS)
     #find PK-FK links between tables
    PkFkLS = [] #init empty pk-fk list, of assumed form: [[PKTable.PKCOL,FKTable.FKCol],[PKTable.PKCOL,FKTable.FKCol],...]
    for myTable in tablesLS:
        for col in Base.metadata.tables[myTable].c:
            if col.foreign_keys:PkFkLS.append([str(list(col.foreign_keys)[0].column),str(col)])
    C_PK=0
    C_FK=1
    C_TABLE = 0 #header 0th element is table name
    C_FIELD = 1 #header 1st element is field name
    #update the foreign key id for each PK-FK relationship affected by csv row data import:
    for aRec in myRecsLS:
        for aPkFk in PkFkLS:
            arecPKid=-1234
            if aPkFk[C_PK] in aRec: #if current PkFk pair is part of aRec then
            #update FK_TABLE SET FK_ID = xxx WHERE FK_TABLE'S PK = XXX
            #get data we need:
                FkLS = aPkFk[C_FK].split('.') #make [tablename, fieldname] of the Table-Field holding the Fk we want to update
                FkTable = Base.metadata.tables[FkLS[C_TABLE]] #assign foreign key table
                FkFKField = FkTable.c[FkLS[C_FIELD]] #assign FK table's FK field
                FkPKFieldName = [PKname.key for PKname in inspect(FkTable).primary_key][0] #get FK Table.primary key using inspector. inspector requires iterator, so iterate pk into a list
                FkPKField = FkTable.c[FkPKFieldName] #assign FK table's PK field
                arecPKid = aRec[aPkFk[C_PK]] #get PKid for aRec[aPkFk] corresponding to current aPkFk's PK name
                #now build updater:
                constrVal = aRec[FkTable.name + '.' + FkPKField.name]
                SQLA_main.updateRec(FkTable, {FkFKField.name:arecPKid}, (lambda x,y: x == y)(FkPKField, constrVal))

def importCSV(csvPath, unqTests):
    '''
    ****IMPORTANT NOTE: function assumes csv in the utf-8-sig file format. weird things happen if its not in this format!!!

    Dictionary of "SQLAlchemy where clause lambda functions" that importCSV uses to test record uniqueness.
    used as the where clause in sqlalchemy queries, updates and deletes
    Form:
        TableName:Lambda Function

        TableName is the table name we want to define uniqueness test for
        Lambda Function can take on any form but must be made to evaluate the CSV row passed as a dictionary (CSVRowDict in this explanation):
            CSVRowDict: {FieldName:CSVColValue, DBTableFieldName:CSVColValue...}
                Where: DBTableFieldName is the name of the field associated with the value at CSVColValue on the current row
                   CSVColValue: a value in the CSV's current row+column corresponding to the DBTableFieldName
            *this assumes that field names are unique across table. if not, then method fails (maybe need to extend method?)

    e.g.: lambda myRowVal: Base.metadata.tables['people'].c['name'] == CSVRowDict['name']
            using lambda function in query will search for CSVRowDict's value for 'name' in the table people, field name
    if table has no record uniqueness requirement, then enter: TableName:False

        # unqTests = {
        #     'people': lambda CSVRowDict: Base.metadata.tables['people'].c['name'] == CSVRowDict['name'],
        #     'locations': False
        # }
    '''

    C_TABLE = 0 #header 0th element is table name
    C_FIELD = 1 #header 1st element is field name
    with open(csvPath, 'rt', encoding='utf-8-sig') as csvfile:
        csvreader = csv.reader(csvfile,dialect='excel')
        rawheadersLS = next(csvreader) #read raw csv headers to list
        headersDict = {myheader:myheader.split('.') for myheader in rawheadersLS} #collect rawheader (Table.FieldName) and its table & field compenent
        #make list of tables:
        tablesLS=[]
        for aheader in headersDict.values():
            if aheader[C_TABLE] not in tablesLS:
                tablesLS.append(aheader[C_TABLE])
        #record primary keys inserted/updated during importing of csv row data.
                    #represent as a list of dicts {Table.PKName:PKid} for table of a given record. Each record is 1 element of list
        print('importing data in CSV rows...')
        myRecsLS = [_HELPER_importCSVrow(headersDict,CSVrow, unqTests) for CSVrow in csvreader]
        print ('imported records in ', len(myRecsLS), ' rows')
        print ('associating records...')
    _HELPER_assocKEYS(myRecsLS, tablesLS)

#FOR TESTING PURPOSES:
# '''
#
# Dictionary of "SQLAlchemy where clause lambda functions" that tests record uniqueness.
# e.g. entries in the 'name' field of the people table must be unique.
# Therefore, we determine whether to insert/update a csv row into the people table based on
# whether the csv row's name field value exists in the people table.
#
# if table has no record uniqueness requirement, then enter: TableName:False
# '''
# unqTests = {
#     'people': lambda RowVal: Base.metadata.tables['people'].c['name'] == RowVal['name'],
#     'locations': False
# }
#
# importCSV('testlab\\2_table_input.csv', unqTests)
# #test some reords
# for u, a in session.query(People, Locations).filter(People.id==Locations.people_id):
#     print (u,a)

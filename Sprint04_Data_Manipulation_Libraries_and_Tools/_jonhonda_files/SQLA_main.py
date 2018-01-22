#Make prototype for a separate script file by cleaning up code in above cell.
#import a single csv containing 2 or more tables. Tables can have PK-FK relations.
#build SQLAlchemy objects, build DB:
#connect to SQLite DB w/ SQLAlchemy ORM:
# from sqlalchemy import create_engine
import os
#deprecate working w/ dbs located on disk for now.
# dbfilename = '_jonhonda_files//test.db' #right now code writes to memory, later change to write to disk not used right now.
# print ("\nClearing old DB")
# try:
#     os.remove(dbfilename)
# except FileNotFoundError as err:
#     print ("no need to remove db file")####it's okay if file doesn't exist. ####
# engine = create_engine('sqlite:///'+ dbfilename, echo = False)

from SQLA_Base import Base

#for now work w/ dbs in memory
# engine = create_engine('sqlite:///:memory:', echo = False)

#NOW DEFINE DB SCHEMA (THIS DOESN'T WRITE SCHEMA TO DB, JUST TO SQLALCHEMY CLASSES AND OBJECTS)
#define an SQLAlchemy base class to maintain catalog of classes and tables relative to this base
from SQLA_DB_User import People
from SQLA_DB_Locations import Locations
from SQLA_conn_man import session, engine

Base.metadata.create_all(engine, checkfirst=True)

#now generate session object:
# from sqlalchemy.orm import sessionmaker
# Session = sessionmaker(bind=engine) #define Session class, which is a factory for making session objects (poor naming choice, in my opinion - why the do it this way??!)
# session = Session() #make a session


#use the base class to define mapped classes in terms of it:
from sqlalchemy import Column, Integer, String
from sqlalchemy import update, insert
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship #http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html#relationship-patterns
from sqlalchemy import inspect

#NOW WRITE SCHEMA TO DB (THIS WRITES TO SQLITE DB):
# Base.metadata.create_all(engine) #build DB schema from Base objects

def getPKFieldNames (myTable):
    """Gets primary key field for the given table.

    Uses SQLAlchemy's .primary_key table attribute.
    Since SQLAlchemy's .primary_key table attribut returns a list, we will use just the 1'st value

    Args:
        myTable: the metadata.table that we want to insert/update on.

    Returns
        the primary key field as an integer

    Raises:
        None.
        """Inserts or updates values into a table's fields subject to some constraints.
    """
     #get Table.primary key using inspector. inspector requires iterator, so iterate pk into a list
    return [PKname.key for PKname in inspect(myTable).primary_key][0]#Use 1st element of list.

def insertupdateRec(myTable, setFieldVals, whereConstraint):
    Only works on one record row at a time. So only pass in 1 record's args


    Args:
        myTable: the metadata.table that we want to insert/update on.
        setFieldVals: a single record represented as a dictionary of fields
                    and values to be inserted/updated {fieldname:val, fieldname:val}
        whereConstraint: where clause used to determine if record already exists/update on
                    passed in as a lambda function

    Returns
        the primary key id value of the table we updated/inserted to.
        primary key is returned as an integer.

    Raises:
        None.
    """
    PKName = getPKFieldNames(myTable) #shove parts of this into getPKFieldNames
    ret = session.query(myTable.c[PKName]).filter(whereConstraint) #determine existance of record w/ whereConstraint
    try:
        PKid = ret.one()[0] #get value of matching record. errors if no record exists
        updateRec(myTable, setFieldVals, whereConstraint)
    except:
        PKid = insertRec(myTable, setFieldVals)
    return PKid

def insertRec(myTable, setFieldVals):
 #insert a single record:
        #ex: insertRec(FkTable, {FkFKField.name:arecPKid})
        #updateTable: table to update
        #setFieldVals: dictionary of fields and vals to be updated: {fieldname:val,fieldname:val}
    rec = session.execute(myTable.insert(),setFieldVals)
    return rec.inserted_primary_key[0]

def updateRec(updateTable, setFieldVals, updateWhereLF):
    #update a single records:
        #ex: updateRecs(FkTable, {FkFKField.name:arecPKid}, (lambda x,y: x == y)(FkPKField, constrVal))
        #updateTable: table to update
        #setFieldVals: dictionarinserted_proimary_key[0]y of fields and vals to be updated: {fieldname:val,fieldname:val}
        #updateWhereLF: update constraints where constraint, passed as a lambda function, is true
    u = update(updateTable) #make a SQLAlchemy update object for updateTable
    u = u.values(setFieldVals) #set update values
    u = u.where(updateWhereLF) #define update's where clause
    rec = session.execute(u) #execute the update

def _HELPER_importCSVrow(headersDict, CSVrow, updateWhereLF = False):
    #importCSV helper function to handle inserting a single CSV row
    #currently forces insert (will be changed to discriminate based on existance of record using lambda function)
        #headersDict: dictionary of form: {table.field:[table,field]}
        #CSVrow: single row of a csv reader loop
        #updateWhereLF:where Clause as a lambda function to pass to insert/updater to determinE record existance
                        #False to force insert
    #return primary keys inserted/updated using CSVrow values
    C_TABLE = 0 #header 0th element is table name
    C_FIELD = 1 #header 1st element is field name
    myTempRecDicts = {aheader[C_TABLE]:{} for aheader in headersDict.values()} #initialize dictionary of tables #and their associated list of  records. note the empty dict. needed b/c we will update that empty dict
    for aheader, avalue in zip(headersDict.values(),CSVrow): #write current header-value pair to a temp dictionary
        mytmpDict = {aheader[C_FIELD]:avalue}
        myTempRecDicts[aheader[C_TABLE]].update(mytmpDict) #place temp dictionary value into current rec's dictionary of tables an assoc. header-values
    myRowRecDict={} #dictionary of record ids inserted/updated for current row: {PKName:PK_ID}
    for myTableName,myRecDict in myTempRecDicts.items():
        #insert table and record's return primary key
        myTable = Base.metadata.tables[myTableName]
        PKLS = getPKFieldNames(myTable)#get primary key field for myTable
        if updateWhereLF==False or updateWhereLF[myTableName] == False:#force insert (update if PKid==-1234 which can't happen)
            PKCol = myTable.c[PKLS] #get sqlAlchemy object for PK Field
            rec_id = insertupdateRec(myTable, myRecDict, (lambda PKid: PKid == -1234)(PKCol))
        else: #use where clause lambda function to evaluate insert/update
            rec_id = insertupdateRec(myTable, myRecDict, updateWhereLF[myTableName](myRecDict))
        myRowRecDict.update({myTableName + '.' + PKLS:rec_id}) #add PK id to record of rows added
    return myRowRecDict

def _HELPER_assocKEYS(myRecsLS, tablesLS):
    #helper function to associate primary-foreign key pairings during importCSV of mixed tables:
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
                updateRec(FkTable, {FkFKField.name:arecPKid}, (lambda x,y: x == y)(FkPKField, constrVal))

def importCSV(csvPath, unqTests):
    #assume header given in form: tablename.fieldname
    # assume all table and header names match database table and field names
    import csv
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
        myRecsLS = [_HELPER_importCSVrow(headersDict,CSVrow, unqTests) for CSVrow in csvreader]
    _HELPER_assocKEYS(myRecsLS, tablesLS)
    session.commit()

'''
Dictionary of "SQLAlchemy where clause lambda functions" that tests record uniqueness.
e.g. entries in the 'name' field of the people table must be unique.
Therefore, we determine whether to insert/update a csv row into the people table based on
whether the csv row's name field value exists in the people table.

if table has no record uniqueness requirement, then enter: TableName:False
'''
unqTests = {
    'people': lambda RowVal: Base.metadata.tables['people'].c['name'] == RowVal['name'],
    'locations': False
}


importCSV('2_table_input.csv', unqTests)
#test some reords
for u, a in session.query(People, Locations).filter(People.id==Locations.people_id):
    print (u,a)

session.close()
engine.dispose()

from SQLA_Base import Base
from SQLA_conn_man import session, engine

#NOW DEFINE DB SCHEMA (THIS DOESN'T WRITE SCHEMA TO DB, JUST TO SQLALCHEMY CLASSES AND OBJECTS)
#define an SQLAlchemy base class to maintain catalog of classes and tables relative to this base

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
    """
     #get Table.primary key using inspector. inspector requires iterator, so iterate pk into a list
    return [PKname.key for PKname in inspect(myTable).primary_key][0]#Use 1st element of list.

def insertupdateRec(myTable, setFieldVals, whereConstraint):
    """Inserts or updates values into a table's fields subject to some constraints.

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
<<<<<<< HEAD
    PKName = getPKFieldNames(myTable) #shove parts of this into getPKFieldNames
=======
    PKName = getPKFieldNames(myTable) #shove partzs of this into getPKFieldNames
>>>>>>> 95e8ddb91b9e507052f3593090bd907e5ebf658c
    ret = session.query(myTable.c[PKName]).filter(whereConstraint) #determine existance of record w/ whereConstraint
    if ret.first() is None: #then no record exists. do insert
        PKid = insertRec(myTable, setFieldVals)
    else: #record exists. update it using whereConstraint to get matching record
        PKid = ret.first()[0] #get value of matching record. errors if no record exists
<<<<<<< HEAD
=======
        # print('update', PKid
>>>>>>> 95e8ddb91b9e507052f3593090bd907e5ebf658c
        updateRec(myTable, setFieldVals, (lambda x,y: x == y)(myTable.c[PKName], PKid))
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
<<<<<<< HEAD
        #setFieldVals: dictionarinserted_proimary_key[0]y of fields and vals to be updated: {fieldname:val,fieldname:val}
        #updateWhereLF: update constraints where constraint, passed as a lambda function, is
=======
        #setFieldVals: dictionary of fields and vals to be updated: {fieldname:val,fieldname:val}
        #updateWhereLF: update constraints where constraint, passed as a lambda function, is
    # print (setFieldVals)
>>>>>>> 95e8ddb91b9e507052f3593090bd907e5ebf658c
    u = update(updateTable) #make a SQLAlchemy update object for updateTable
    u = u.values(setFieldVals) #set update values
    u = u.where(updateWhereLF) #define update's where clause
    rec = session.execute(u) #execute the update

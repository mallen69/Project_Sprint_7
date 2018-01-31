'''
Name: Combo_BMP_Eval.py
evaluate combo BMPs (right now just create combos: find combos, find max pollutant_removal_rates, insert/update records in db)

'''
#IMPORT python:
import pandas as pd
import itertools     #FOR MAKING COMBOS. https://docs.python.org/3/library/itertools.html

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
#Table definitions as SQLA classes (only import what we need):
from SQLA_DB_base_bmps import Base_BMPs
from SQLA_DB_combo_bmps import Combo_BMPs
from SQLA_DB_pollutant_removal_rates import Pollutant_Removal_Rates as PRR
Base.metadata.create_all(engine, checkfirst=True) #create SQLA classes

######################################### COMBO CREATOR #####################################################################
#Build bmp options (combos of base_bmps)
def _Make_bmp_fingerprint(base_BMP_components):
    #create fingerprint of the passed list of base_bmp_ids
    #fingerprint is just a | separated list of ids of the base bmps that make up the combo bmp
    #corresponds to bmp_options table's bmp_fingerprint field
    #FORMAT: |bmp_option_base_component_id||bmp_option_base_component_id| w/ id's given in ascending order
    fingerprint = '|' + '|'.join(str(id) + '|' for id in base_BMP_components)
    return fingerprint
# print (Make_bmp_fingerprint([1]))
# print (Make_bmp_fingerprint([1,2]))
# print (Make_bmp_fingerprint([1,2,3]))

def _Max_bmp_combo_removal_rates(base_BMP_components, r_polls_pd, r_polls):
    #find max removal rate of the passed bmp combo using the passed list of base bmps and pandas dataframe of pollutants, and pollutant removal rates (r_polls)
    #r_polls exprectd as list of pollutant types ['r_tss', 'r_turbidity', 'r_p', 'r_n', 'r_nn', 'r_an', 'r_og', 'r_cu', 'r_zn', 'r_fe', 'r_phmin', 'r_phmax']
    #dataframe expected to include:
        #base_Bmp_id as the index
        #r_polls as column headers
    #insert max rates into pollutant_removal_rates table.

    #get fingerprint
    bmp_fingerprint = _Make_bmp_fingerprint(base_BMP_components)
    #get existing combo bmp id or make new one (determine existance be seeing if record w/ bmp_fingerprint exists in Combo_BMPs table)
    Combo_BMPs_metatable = Base.metadata.tables['combo_bmps']
    Combo_BMPs_pkid = SQLA_main.insertupdateRec(Combo_BMPs_metatable,{'bmp_fingerprint':bmp_fingerprint},Combo_BMPs.bmp_fingerprint == bmp_fingerprint)
    myComboBMP = session.query(Combo_BMPs).filter(Combo_BMPs.id == Combo_BMPs_pkid).first() #get combo bmp record

    #find max removal rates for combo bmp:
    r_max = r_polls_pd.loc[list(base_BMP_components)].loc[:,r_polls].max() #get all polllutants' max removal rates for the combo set
    myRecDict = {idx:val for idx, val in zip(r_max.index, r_max)} #write results to dictionary: {poll_type: maxVal}

    #write bmp combo's max removal rates to PRR record:
    myPRRTable = Base.metadata.tables['pollutant_removal_rates']
    #insert new PRR record if record doesn't exist for myComboBMP (i.e. myComboBMP.bmp_option_removal_rate_id IS NONE)
    #otherwise, update existing PRR record
    PRR_pkid = SQLA_main.insertupdateRec(myPRRTable, myRecDict, myPRRTable.c['id'] == myComboBMP.bmp_option_removal_rate_id)

    #place PRR_pkid into Combo_BMP's bmp_option_removal_rate_id field
    myComboBMP.bmp_option_removal_rate_id = PRR_pkid
    session.flush()

def Make_ALL_bmp_base_option_combos():
    #make all possible combinations of BMPs by permuting larger and larger sets, starting w/ 1 BMP, then 2, etc.
    #CLEAR component tables:

    #get pandas datafram of each base bmp's pollutant removal rate
    #make query of base bmp removal rates
    q = session.query(Base_BMPs.bmp_name, Base_BMPs.id.label('Base_BMP_id'),
                  PRR.id.label('PRR_id'),
                  PRR.r_tss, PRR.r_turbidity, PRR.r_p, PRR.r_n, PRR.r_nn, PRR.r_an,
                  PRR.r_og, PRR.r_cu, PRR.r_zn, PRR.r_fe, PRR.r_phmin, PRR.r_phmax
                ).filter(Base_BMPs.bmp_removal_rates_id == PRR.id)
    #use query to create pandas object using SQLA query, set Base_BMP_id to be pandas index
    r_polls_pd = pd.read_sql_query(q.statement,session.bind).set_index("Base_BMP_id")
    r_polls = ['r_tss', 'r_turbidity', 'r_p', 'r_n', 'r_nn', 'r_an', 'r_og', 'r_cu', 'r_zn', 'r_fe', 'r_phmin', 'r_phmax']

#     now the magic: make BMP combos of increasing length, starting w/ 1 BMP, then 2, ...
    makeCnt = 0
    for CBOLen in range(1,len(r_polls_pd.index)):
    # for CBOLen in range(1,3): #+1 so it's inclusive of last count
        print (' Making BMP Combos of length: ' + str(CBOLen))
        #make list of CBOLen long combo lists using r_poll_pd index (which is the base_bmp_ids in Pandas object)
        print (' Find max pollutant removal rates for each BMP Combo of length: ', CBOLen)
        for combo in  itertools.combinations(r_polls_pd.index,CBOLen):
            _Max_bmp_combo_removal_rates(combo, r_polls_pd, r_polls)
        print ('  Made ', len(list(itertools.combinations(r_polls_pd.index,CBOLen))), ' combos')

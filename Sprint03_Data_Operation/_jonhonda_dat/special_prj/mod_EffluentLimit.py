'''
Name: mod_EffluentLimit.py

This module is related to the estimation of effluent limits, exceedances, and polluant risk scores

Effluent Limit Calculations:
    Main Function: Get
functions related to caclulating effluent limits for facilities, as well as exceedances of effluent limits

'''
#IMPORT python:
import pandas as pd
import numpy as np
import math
import datetime
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
#Table definitions as SQLA classes (only import what we need):
from SQLA_DB_facility_type_has_nel import Facility_Type_Has_NEL
from SQLA_DB_nel_sample_classes import NEL_Sample_Classes
from SQLA_DB_wrs_pollutant_risks import WRS_Pollutant_Risks
Base.metadata.create_all(engine, checkfirst=True) #create SQLA classes




######################################### CALCULATE EFFLUENT LIMITS #####################################################################
'''
Estimate the Numeric Effluent Limits (NELs) for a GIVEN facility.
Return wet and dry season NELs in 2 separate dataframes:
    pd_FacsNELs_Wet & pd_FacsNELs_Dry
Estimate NELs using the EffLim module's GetNELs function call.
 The GetNELs function call will differentiate between wet and dry season limits
 (if limits are the same between wet & dry season, then the same limit will be placed into the wet and dry
  dataframes.)
 The GetNEls function calculates a pollutant constituent NEL using this formula:
    NEL = fTypeHas_NEL * SampleClass_NEL
    Where:
      fTypeHas_NEL is a [0,1] value from PBP Table 3, based on facility type (stored in SQLA_DB_facility_type_has_nel)
      SampleClass_NEL is pollutant concentration based on facility's sample class, based on PBP Appendix L
'''
def _HELPER_Get_pd_NEL_Values (WetORDry_Field):
    #helper function to get pandas df the NEL values based on the given facility's NEL_Column from the NEL_sample_Classes table
    #for the given facility, for the wet or dry season
    #rename columns to be prefixed by 'nel_'
    wrsid = session.query(NEL_Sample_Classes.wrs_pollutant_class_id).filter(WetORDry_Field ==
                                                                            NEL_Sample_Classes.nel_column)
    if wrsid.first() is None:
        return None
    q = session.query(
        WRS_Pollutant_Risks.wrs_tss,
        WRS_Pollutant_Risks.wrs_turbidity,
        WRS_Pollutant_Risks.wrs_p,
        WRS_Pollutant_Risks.wrs_n,
        WRS_Pollutant_Risks.wrs_nn,
        WRS_Pollutant_Risks.wrs_an,
        WRS_Pollutant_Risks.wrs_og,
        WRS_Pollutant_Risks.wrs_cu,
        WRS_Pollutant_Risks.wrs_zn,
        WRS_Pollutant_Risks.wrs_fe,
        WRS_Pollutant_Risks.wrs_phmin,
        WRS_Pollutant_Risks.wrs_phmax
    ).filter(WRS_Pollutant_Risks.id == wrsid.first()[0])
    pd_tmp = pd.read_sql(q.statement,session.bind) #write to DataFrame
    return  pd_tmp

def _HELPER_Get_pd_FacTypeHas_NEL (recFac):
    #helper function to get whether fac type requires NEL for each constituent (0 or 1) from the facility_type_has_nels table for the given recFac's fac_Type
    wrsid = session.query(Facility_Type_Has_NEL.wrs_pollutant_limits_id).filter(recFac.facility_type_id ==
                                                                                Facility_Type_Has_NEL.facility_type_id)
    if wrsid.first() is None:
        return None
    q = session.query(
        WRS_Pollutant_Risks.wrs_tss,
        WRS_Pollutant_Risks.wrs_turbidity,
        WRS_Pollutant_Risks.wrs_p,
        WRS_Pollutant_Risks.wrs_n,
        WRS_Pollutant_Risks.wrs_nn,
        WRS_Pollutant_Risks.wrs_an,
        WRS_Pollutant_Risks.wrs_og,
        WRS_Pollutant_Risks.wrs_cu,
        WRS_Pollutant_Risks.wrs_zn,
        WRS_Pollutant_Risks.wrs_fe,
        WRS_Pollutant_Risks.wrs_phmin,
        WRS_Pollutant_Risks.wrs_phmax
    ).filter(WRS_Pollutant_Risks.id == wrsid.first()[0])
    return pd.read_sql(q.statement,session.bind)

def GetNELs(recFac, OutputResults):
    #return 2 dataframes for the facility's NELs during wet and dry seasons
    #for each constituent, determine limit as intersection of Facility_Type_Has_NEL and NEL Column Values:
    #input: recFac: a facility_chars table record
    #input: OutputResults: bool indicating if we should output calculations and results
    #output: list of dictionaries: {}
    #get wet and dry season effluent limits for the facility's assigned NEL_Column:
    pd_NELColumn_Wet = _HELPER_Get_pd_NEL_Values(recFac.NEL_Column_Wet)
    pd_NELColumn_Dry = _HELPER_Get_pd_NEL_Values(recFac.NEL_Column_Dry)

    #get effluent limit requirements based on facility's facility_type (value is 0 or 1). 0 if not exist. 1 if exist:
    pd_NELRequired = _HELPER_Get_pd_FacTypeHas_NEL(recFac)

    #DO: NEL = fTypeHas_NEL * SampleClass_NEL
    try:
        pd_FacNELs_Wet = pd_NELColumn_Wet.mul(pd_NELRequired,1)
    except AttributeError: #error occurs if none type was passed into one of the vars for this facility
        return None, None
    try:
        pd_FacNELs_Dry = pd_NELColumn_Dry.mul(pd_NELRequired,1)
    except AttributeError: #occurs if none type was passed into one of the variables
        return None, None

        # return None,None #return 2 none types
    #Since we know no NEL = 0. We know that result of mult. being 0 is the same as N/A . so assign NaN values to any 0 element.
    pd_FacNELs_Wet = pd_FacNELs_Wet.applymap(lambda x: float('nan') if x == 0 else x)
    pd_FacNELs_Dry = pd_FacNELs_Dry.applymap(lambda x: float('nan') if x == 0 else x)

    #no longer need column names to match. rename columns from 'wrs' to 'nel'
    ls_cols = list(pd_FacNELs_Wet.columns)
    dict_repl = {col: col.replace('wrs','nel',1) for col in ls_cols}
    pd_FacNELs_Wet = pd_FacNELs_Wet.rename(columns = dict_repl)
    dict_repl = {col: col.replace('wrs','nel',1) for col in ls_cols}
    pd_FacNELs_Dry = pd_FacNELs_Dry.rename(columns = dict_repl)

    #for show-your-work purposes, make a summary dataframe:
    if OutputResults:
        df_new = pd.concat([pd.concat([pd.concat( [pd.concat([pd_NELColumn_Dry, pd_NELColumn_Wet]),pd_NELRequired]), pd_FacNELs_Dry]),pd_FacNELs_Wet])
        df_new.insert(0, 'description', 'x')
        df_new.iloc[[0],[0]]='Dry Season NELs* (Col. ' + recFac.NEL_Column_Dry + '): '
        df_new.iloc[[1],[0]]='Wet Season NELs* (Col. ' + recFac.NEL_Column_Wet + '): '
        df_new.iloc[[2],[0]]='NEL Exists**: '
        df_new.iloc[[3],[0]]='Facility Dry Season NELs: '
        df_new.iloc[[4],[0]]='Facility Wet Season NELs: '
        df_new = df_new.set_index('description')
        print ('\nSummary of Wet & Dry Season NEL Determination for: ', recFac.Fac_Name)
        display(df_new)
        print ('   Notes: *Per PBP Appendix L; **Facility Type Requires this NEL (0: No; 1: Yes)')

    #insert in facility id column
    pd_FacNELs_Wet.insert(0,'Facility_ID',recFac.id)
    pd_FacNELs_Wet = pd_FacNELs_Wet.set_index('Facility_ID')
    pd_FacNELs_Dry.insert(0,'Facility_ID',recFac.id)
    pd_FacNELs_Dry = pd_FacNELs_Dry.set_index('Facility_ID')

    return pd_FacNELs_Wet, pd_FacNELs_Dry

######################################### ESTIMATE EXCEEDANCE LEVELS #####################################################################
def Get_pd_NEL_WetOrDry(SampleDate,pd_FacsNELs_Wet, pd_FacsNELs_Dry):
    '''
    Given the pd_FacsNELs_Wet and pd_FacsNELs_Dry dataframes, return one of the 2 depending on the given SampleDate
    Wet Season is from: January 1 through April 30 and November 1 through December 31
    Dry Season is from: May 1 through October 31

    Input:
        SampleDate: date type object. Represents the date we want to get NEL data for.
    Global Variables assumed to exist:
        pd_FacsNELs_Wet: pandas dataframe of wet season NELs
        pd_FacsNELs_Dry: pandas dataframe of dry season NELs
    '''
    SampleDate = SampleDate.date()
    #Wet Season part 1 (between Jan. 1 of sampledate year and April 30 of sampledate year)
    if datetime.date(SampleDate.year, 1,1) <= SampleDate <= datetime.date(SampleDate.year, 4,30):
        return pd_FacsNELs_Wet
    #dry season (between May. 1 of sampledate year and October 31 of sampledate year)
    elif datetime.date(SampleDate.year, 5,1) <= SampleDate <= datetime.date(SampleDate.year, 10,31):
        return pd_FacsNELs_Dry
    #wet season part 2 (between November 1 and December 31 of sample date year i.e. rest of year not covered by conditions above)
    else:
        return pd_FacsNELs_Wet

def _HELPER_IndexInPD(Idx, WRS_Constituent, pd_FacsNELs_Wet, pd_FacsNELs_Dry):
    '''
    function to determine if index and wrs_constituent exists in pd_FacsNELs_Dry and pd_FacsNELs_Wet
    return true if Exists
    return false if does not exist
    '''
    try:
        t = pd_FacsNELs_Wet.loc[Idx, WRS_Constituent]
    except:
        return False

    try:
        t = pd_FacsNELs_Dry.loc[Idx, WRS_Constituent]
    except:
        return False
    return True #if get here then okay.

def ExceedanceCalc(myRow, Constituent, FacID, pd_FacsNELs_Wet, pd_FacsNELs_Dry, ShowCalculations):
    '''
    pass in pandas row of: Sample_Date, PollunantSampleConcentrations
    pass in Pollutant constituent we need to calculate exceedance for
    pass in Facility ID we want to evaluate
    pass in ShowCalculations indicating if we should output steps
    return: exceedance value

    function considers whether sample was taken during wet or dry season
    '''
    #do preliminary checks on data:
    if _HELPER_IndexInPD(FacID, 'nel_' + Constituent, pd_FacsNELs_Wet, pd_FacsNELs_Dry) == False:
        return float('nan')
    if math.isnan(myRow['c_'+Constituent]): #if parameter value is NAN then return Nan
        return float('nan')
    if math.isnan(Get_pd_NEL_WetOrDry(myRow['sample_date'],pd_FacsNELs_Wet, pd_FacsNELs_Dry).loc[FacID, 'nel_'+Constituent]): #if NEL value is NAN then return Nan
        return float('nan')

    #if get to this point, prelim checks passed. handle based on constituent type:
    if Constituent == 'phmin':
        # try:
        ParamVal = max(0.0, Get_pd_NEL_WetOrDry(myRow['sample_date'],pd_FacsNELs_Wet, pd_FacsNELs_Dry).loc[FacID, 'nel_'+Constituent] - myRow['c_'+Constituent])
        # except:
        #     ParamVal = float('nan')
#             print(Constituent)
    elif Constituent == 'phmax':
        # try:
        ParamVal = max(0.0,myRow['c_'+Constituent]  -  Get_pd_NEL_WetOrDry(myRow['sample_date'],pd_FacsNELs_Wet, pd_FacsNELs_Dry).loc[FacID, 'nel_'+Constituent])
        # except:
            # ParamVal = float('nan')
#             print(Constituent)
    else:
        # try:
        ParamVal = max(0.0,myRow['c_'+Constituent]  -  Get_pd_NEL_WetOrDry(myRow['sample_date'],pd_FacsNELs_Wet, pd_FacsNELs_Dry).loc[FacID, 'nel_'+Constituent])
        # except:
            # ParamVal = float('nan')
#             print(Constituent)
    # print (ParamVal)
    return ParamVal


    ######################################### ESTIMATE POLLUTANT EXCEEDANCE AGE FACTOR WEIGHTED AVERAGES #####################################################################
def Calc_AFWtdExceedances(pd_FacExceedances, pollLS, ShowCalculations):
    '''
    CALCULATE AGE FACTOR WEIGHTED AVERAGE FOR EACH CONSTITUENT:

    Age factor acknowledges fact that more recent samples are a better representation of facility pollutant discharge
    (i.e. sampling data) and housekeeping-operations (i.e. inspections) realities. But, historic data as a whole also tells part
    of story (i.e. we want to dampen whipsaw effects that may occur if we only considered most recent data).

    AF = exp(-SampleRank)
    SampleRank = Newest sample = 1
                  Second Newest sample = 2
                  ...
                  nth Newest Sample = n (out of n samples)

    INPUTS:
        pd_FacExceedances: dataframe holding exceedances
            FORMAT: ExPollConc.id, Facility_ID, Sample_Date, exceedance concentrations
        pollLS: list of polluant constituents that can be found in the dataframe's exceedance concentrations
        ShowCalculations: True if you want output of calculation summary. false if not

    RETURN:
        DataFrame of age factor weighted averages.
        FORMAT: Facility_ID, AFwtd_c_conc...
    '''
    # group dataframe by date
    grouped = pd_FacExceedances.groupby('sample_date')
    #make age factored exceedence dataframe. Only include max concentration for each of the facility's sample date
    pd_FacExceedances= pd.DataFrame(grouped.agg(np.max)) #write max concs for each date to the pd_AFFacExeedances dataframe.
    #establish sorted order. we want most recent data to be assigned lowest rank
    pd_FacExceedances = pd_FacExceedances.sort_index(ascending=False) #sort by date, which is currently the data frame's index. most recent at top

    #add facility id and sample date to a new dataframe called pd_AFFAcExceedances, which will hold AF related calcs for the concs
    #as we calc data for each conc, we'll add it to this dataframe
    pd_AFFacExceedances = pd_FacExceedances.loc[:,['Facility_ID']]
    for Constituent in pollLS:
        pd_temp = pd_FacExceedances.loc[:,['c_' + Constituent]] #copy the current pollutant exceedance value into a temp dataframe
        pd_temp.insert(pd_temp.shape[1],'c_' + Constituent + '_SR', float('nan')) #make sample rank column
        pd_temp.insert(pd_temp.shape[1],'c_' + Constituent + '_AF', float('nan')) #make age factor column
        pd_temp.insert(pd_temp.shape[1],'c_' + Constituent + '_AF*c', float('nan')) #make age factor weighted column

        #establish sample rank for each row. Only rank rows where Concentration value is not NaN
        SampleRank=-1 #initialize sample rank
        #ITERATE THROUGH EACH ROW. Use Row's index to locate concentration value
        for idx in pd_temp.index:
            if not math.isnan(pd_temp.loc[idx]['c_' + Constituent]): #if not NaN then make sample rank & calc AF
                SampleRank += 1
                AF = math.exp(-SampleRank)
                AFc = AF * pd_temp.loc[idx]['c_' + Constituent]
                #write results to temp dataframe:
                pd_temp.loc[idx]['c_' + Constituent + '_SR'] = SampleRank
                pd_temp.loc[idx]['c_' + Constituent + '_AF'] = math.exp(-SampleRank)
                pd_temp.loc[idx]['c_' + Constituent + '_AF*c'] = AFc
        pd_AFFacExceedances = pd.concat([pd_AFFacExceedances, pd_temp], axis=1)
    FacID = pd_AFFacExceedances['Facility_ID'].iloc[0]
    if ShowCalculations:
        print('Calculation Details for Facilty ID: ', FacID)
        display(pd_AFFacExceedances)
#     #calculate age factor weighted average for each constituent. Put into new dataframe called pd_AFWFacExceedances
    pd_AFWtdAvg=pd.DataFrame({'Facility_ID':[FacID]})#insert facility id into pd_AFWtdAvg
    for Constituent in pollLS:
        AFSum = pd_AFFacExceedances['c_' + Constituent + '_AF'].sum()
        AFcSum = pd_AFFacExceedances['c_' + Constituent + '_AF*c'].sum()
        try:
            pd_AFWtdAvg['AFWtd_c_' + Constituent]  = AFcSum / AFSum
        except ZeroDivisionError:
            pd_AFWtdAvg['AFWtd_c_' + Constituent] = float('nan')
    if ShowCalculations:
        print ('Age Factor Weighted Averages')
        display(pd_AFWtdAvg)
    return(pd_AFWtdAvg)

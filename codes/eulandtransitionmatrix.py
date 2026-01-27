import os
import argparse
import pathlib
import glob
import pandas as pd
import numpy as np
from countrylist import euls,euplusls,noneuls,allcountryls, allcountryls_missing

land_transition_matrix_sheet = 'Table4.1'
#Rows for FROM Land Use Class in Table4.1
from_ls = ["Forest land \(managed\)","Forest land \(unmanaged\)","Cropland","Grassland \(managed\)","Grassland \(unmanaged\)",
           "Wetlands \(managed","Wetlands \(unmanaged\)","Settlements","Other land"]
#Result sheet names for Land use change classes
sheet_name_dict = {0:[r'FL(manag.)->FL(manag.)',r'FL(manag.)->FL(unmanag.)',r'FL(manag.)->CL',
                      r'FL(manag.)->GL(manag.)',r'FL(manag.)->GL(unmanag.)',r'FL(manag.)->WL(manag.)',r'FL(manag.)->WL(unmanag.)',
                      r'FL(manag.)->SL',r'FL(manag.)->OL'],
                   1:[r'FL(unmanag.)->FL(manag.)',r'FL(unmanag.)->FL(unmanag.)',r'FL(unmanag.)->CL',
                      r'FL(unmanag.)->GL(manag.)',r'FL(unmanag.)->GL(unmanag.)',r'FL(unmanag.)->WL(manag.)',r'FL(unmanag.)->WL(unmanag.)',
                      r'FL(unmanag.)->SL',r'FL(unmanag.)->OL'],
                   2:[r'CL->FL(manag.)',r'CL->FL(unmanag.)',r'CL->CL',
                      r'CL->GL(manag.)',r'CL->GL(unmanag.)',r'CL->WL(manag.)',r'CL->WL(unmanag.)',
                      r'CL->SL',r'CL->OL'],
                   3:[r'GL(manag.)->FL(manag.)',r'GL(manag.)->FL(unmanag.)',r'GL(manag.)->CL',
                      r'GL(manag.)->GL(manag.)',r'GL(manag.)->GL(unmanag.)',r'GL(manag.)->WL(manag.)',r'GL(manag.)->WL(unmanag.)',
                      r'GL(manag.)->SL',r'GL(manag.)->OL'],
                   4:[r'GL(unmanag.)->FL(manag.)',r'GL(unmanag.)->FL(unmanag.)',r'GL(unmanag.)->CL',
                      r'GL(unmanag.)->GL(manag.)',r'GL(unmanag.)->GL(unmanag.)',r'GL(unmanag.)->WL(manag.)',r'GL(unmanag.)->WL(unmanag.)',
                      r'GL(unmanag.)->SL',r'GL(unmanag.)->OL'],
                   5:[r'WL(manag.)->FL(manag.)',r'WL(manag.)->FL(unmanag.)',r'WL(manag.)->CL',
                      r'WL(manag.)->GL(manag.)',r'WL(manag.)->GL(unmanag.)',r'WL(manag.)->WL(manag.)',r'WL(manag.)->WL(unmanag.)',
                      r'WL(manag.)->SL',r'WL(manag.)->OL'],
                   6:[r'WL(unmanag.)->FL(manag.)',r'WL(unmanag.)->FL(unmanag.)',r'WL(unmanag.)->CL',
                      r'WL(unmanag.)->GL(manag.)',r'WL(unmanag.)->GL(unmanag.)',r'WL(unmanag.)->WL(manag.)',r'WL(unmanag.)->WL(unmanag.)',
                      r'WL(unmanag.)->SL',r'WL(unmanag.)->OL'],
                   7:[r'SL->FL(manag.)',r'SL->FL(unmanag.)',r'SL->CL',
                      r'SL->GL(manag.)',r'SL->GL(unmanag.)',r'SL->WL(manag.)',r'SL->WL(unmanag.)',
                      r'SL->SL',r'SL->OL'],
                   8:[r'OL->FL(manag.)',r'OL->FL(unmanag.)',r'OL->CL',
                      r'OL->GL(manag.)',r'OL->GL(unmanag.)',r'OL->WL(manag.)',r'OL->WL(unmanag.)',
                      r'OL->SL',r'OL->OL']
                   }

def CreateLandTransitionMatrix(writer,directory,countryls,sheet:str,sheet_name:str,from_row:str,to_col:int,start:int,end:int):
    """
    Read CRFReporter Reporting tables and create Land transition sheets for each country and year.
    Use Excel sheet Table 4.1 Land Transition Matrix
    \param writer Excel writer
    \param directory The direactory where the Reporting tables are located
    \param countryls List of countries to be used
    \param sheet Land Transition Matrix sheet name
    \param sheet_name Excel sheet for a single Land Transition results
    \param from_row Name of the row name in *from_ls* (*FROM* Land Use classes Table4.1)
    \param to_col Column number for *TO*  Land Use Class
    \param start Inventory start year (1990)
    \param end Inventory end year
    """
    
    datarowlss=[]
    for country in countryls:
        rowls=[]
        #List all excel files and sort the files in ascending order (1990,1991,...,2021)
        #Exclude years in 1980's that some countries report
        # excelfilels=list(set(glob.glob(directory+'/'+country+'/*.xlsx'))-set(glob.glob(directory+'/'+country+'/*_198??*.xlsx')))
        # excelfilels=sorted(excelfilels)

        # MOD: 2024 require that the filename starts with letter A-Z or a-z
        excelfilels = list(set(glob.glob(directory+'/'+country+'/[A-z]*.xlsx'))-set(
            glob.glob(directory+'/'+country+'/*[_,-]198??*.xlsx')))
        excelfilels = sorted(excelfilels)
        print(country,sheet_name)
        # print(excelfilels)
        i = start
        for file in excelfilels:
            print(file)
            if i>end:
                break
            xlsx = pd.ExcelFile(file)
            df = pd.read_excel(xlsx,sheet,keep_default_na=False,na_values=[''], header=7, usecols='B:M')
            row = df[df[df.columns[0]].str.contains(from_row)==True]
            rowls.append(row.iloc[0,to_col])
            i = i+1
        datarowlss.append(rowls)
    dftotal = pd.DataFrame(datarowlss)
    dftotal.index = countryls
    dftotal.columns =  list(range(start,end+1))
    dftotal.to_excel(writer,sheet_name,na_rep='NaN')
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--directory",dest="f1",required=True,help="Inventory Parties Directory")
    parser.add_argument("-s","--start",dest="f2",required=True,help="Inventory start year (usually 1990)")
    parser.add_argument("-e","--end",dest="f3",required=True,help="Inventory end year")
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--eu",action="store_true",dest="eu",default=False,help="EU countries")
    group.add_argument("--euplus",action="store_true",dest="euplus",default=False,help="EU countries plus GBR, ISL and NOR")
    group.add_argument("-a","--all",action="store_true",dest="all",default=False,help="All countries (EU+others")
    group.add_argument("-c","--countries",dest="country",type=str,nargs='+',help="List of countries")
    group.add_argument("-l","--list",action="store_true",dest="countryls",default=False,
                       help="List files in Inventory Parties Directory")
    group.add_argument("--amissing", action="store_true", dest="all_missing", default=False,
                    help='All countries where some are missing. See allcountryls_missing in countrylist.py')
              
    args = parser.parse_args()
    directory=args.f1
    print("Inventory Parties directory",directory)
    inventory_start=int(args.f2)
    print("Inventory start",inventory_start)
    inventory_end=int(args.f3)
    print("Inventory end",inventory_end)
    file_prefix = 'EU'
    if args.eu:
        print("Using EU  countries")
        countryls=euls
    elif args.euplus:
        print("Using EU  countries plus GBR, ISL, NOR")
        countryls=euplusls
        file_prefix = 'EU_GBR_ISL_NOR'
    elif args.all:
        print("Using all countries")
        countryls = euls+noneuls
        file_prefix='EU_and_Others'
    elif args.countryls:
        print("Listing countries in",args.f1)
        ls = glob.glob(args.f1+'/???')
        countryls = [pathlib.Path(x).name for x in ls]
        countryls.sort()
        file_prefix = pathlib.Path(args.f1).name
    elif args.all_missing:
        print("Using allcountry list missing")
        countryls = allcountryls_missing
        file_prefix = 'all_countries_some_missing'
    else:
        print("Using countries", args.country) 
        countryls=args.country
        file_prefix=countryls[0]
        for country in countryls[1:]:
            file_prefix = file_prefix+"_"+country

    writer = pd.ExcelWriter(file_prefix+'_Table4.1_Land_Transition_Matrix_'+str(inventory_start)+'_'+str(inventory_end)+'.xlsx',
                            engine='xlsxwriter')
    #1. Table4.1 Land transition matrix
    index = 0
    for land_use_class in from_ls:
        col=1
        sheet_name_ls = sheet_name_dict[index]
        index=index+1
        for sheet_name in sheet_name_ls:
            CreateLandTransitionMatrix(writer,directory,countryls,land_transition_matrix_sheet,sheet_name,land_use_class,col,
                                       inventory_start,inventory_end)
            col=col+1
    writer.close()

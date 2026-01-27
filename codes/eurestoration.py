import os
import argparse
import pathlib
import glob
import pandas as pd
import numpy as np
from countrylist import euls, euplusls, noneuls, allcountryls, allcountryls_missing, allcountryls_missing_noeua
import EUutility

pd.set_option('display.max_colwidth', None)

# Excel sheets needed
sheet_ls = ['Table4.A', 'Table4.B', 'Table4.C', 'Table4.D']
sheet_ext_ls = [' FL', ' CL', ' GL', ' WL']
nan_list = ['NO', 'NA', 'IE', 'NE']
# Search dataframe row with these names
substr_ls = ['A. Total forest land', 'B. Total cropland',
             'C. Total grassland', 'D. Total wetlands']
# Column names in the resulting excel. Note a bit different sheet structure.
Table4A_columns_ls = ['TotalArea(kha)', 'MineralSoil(kha)', 'OrganicSoil(kha)', 'LivingBMGains(tC/ha)', 'LivinBMLosses(tC/ha)', 'LivingBMNetChange(tC/ha)',
                      'DeadWoodNetChange(tC/ha)', 'LitterNetChange(tC/ha)', 'MineralSoilsNetChange(tC/ha)', 'OrganicSoilsNetChange(tC/ha)',
                      'LivingBMGains(ktC)', 'LivingBMLosses(ktC)', 'LivingBMNetChange(ktC)', 'DeadwoodNetChange(ktC)', 'LitterNetChange(ktC)',
                      'MineralSoilsNetChange(ktC)', 'OrganicSoilsNetChange(ktC)', 'NetCO2(ktCO2)']

Table4B_columns_ls = ['TotalArea(kha)', 'MineralSoil(kha)', 'OrganicSoil(kha)', 'LivingBMGains(tC/ha)', 'LivinBMLosses(tC/ha)', 'LivingBMNetChange(tC/ha)',
                      'DeadOrganicNetChange(tC/ha)', 'MineralSoilsNetChange(tC/ha)', 'OrganicSoilsNetChange(tC/ha)',
                      'LivingBMGains(ktC)', 'LivingBMLosses(ktC)', 'LivingBMNetChange(ktC)', 'DeadOrganicNetChange(ktC)',
                      'MineralSoilsNetChange(ktC)', 'OrganicSoilsNetChange(ktC)', 'NetCO2(ktCO2)']
Table4C_columns_ls = Table4B_columns_ls
Table4D_columns_ls = Table4B_columns_ls
columns_lss = [Table4A_columns_ls, Table4B_columns_ls,
               Table4C_columns_ls, Table4D_columns_ls]


def CreateEUTable4Total1(writer, data_dir, countryls: list, inv_start: int, inv_end: int):
    """
    Collect row 10 from CRFReporter Excel files Table4 A,B,C and D 
    \pre It is assumed that immediate subdirectory of data_dir contains country directories denoted by three letter acronym.
    For each country
       For each Table4.[A,B,C,D]
          For each each year
            Collect row 10 (Total) to dataframe from CRFReporter Excel files
          Create excel sheet
    Save Excel file
    \param writer  Excel writer
    \param data_dir Data location
    \param countryls List of countries
    \param inv_start Inventroy start year, 1990
    \param inv_end Inventory end year
    \return the Excle writer with data
    \post Units are as in Excel files (no conversion to CO2)
    """
    excelfilels = list(set(glob.glob(directory+'/'+country+'/*.xlsx')) -
                       set(glob.glob(directory+'/'+country+'/*_198??*.xlsx')))
    excelfilels = sorted(excelfilels)
    for (sheet, row_name, columns_ls) in zip(sheet_ls, substr_ls, columns_lss):
        print(country, sheet)
        data_row_lss = []
        i = inv_start
        for excel_file in excelfilels:
            if i > inv_end:
                break
            i = i+1
            xlsx = pd.ExcelFile(excel_file)
            df = pd.read_excel(
                xlsx, sheet, keep_default_na=False, na_values=['MISSING_VALUE'])
            # Find row by its name as Dataframe
            row_df = df[df[df.columns[1]].str.contains(
                substr_ls[substr_ls.index(row_name)]) == True]

            # Row as Series
            row_s = row_df.iloc[0, :]
            # Row as list
            row_ls = list(row_s)
            # Delete two first element: Title and Subdivision in CRFReporter excel
            del row_ls[0:2]
            # Append one year data
            data_row_lss.append(row_ls)
            # Data collected for one sheet, create data frame
        df = pd.DataFrame(data_row_lss)
        df.columns = columns_ls
        df.index = list(range(inv_start, (inv_end+1)))
        df.to_excel(writer, sheet_name=country+sheet, na_rep='NaN')
    return writer


def CreateEUTable4Total2(writer, data_dir, countryls: list, inv_start: int, inv_end: int):
    """
    Collect row 10 from CRFReporter Excel files Table4 A,B,C and D 
    \pre It is assumed that immediate subdirectory of data_dir contains country directories denoted by three letter acronym.
    For each Table4.[A,B,C,D]
       For each country
          For each each year
            Collect row 10 (Total) to dataframe from CRFReporter Excel files
       Create excel sheet
    Save Excel file
    \param writer  Excel writer
    \param data_dir Data location
    \param countryls List of countries
    \param inv_start Inventroy start year, 1990
    \param inv_end Inventory end year
    \return the Excle writer with data
    \post Units are as in Excel files (no conversion to CO2)
    """
    for (sheet, sheet_ext, row_name, columns_ls) in zip(sheet_ls, sheet_ext_ls, substr_ls, columns_lss):
        df_merge = pd.DataFrame()
        for country in countryls:
            # excelfilels = list(set(glob.glob(directory+'/'+country+'/*.xlsx')) -
            #                    set(glob.glob(directory+'/'+country+'/*_198??*.xlsx')))
            # excelfilels.sort()
            # List all excel files and sort the files in ascending order (1990,1991,...,2015)
            # Exclude years in 1980's
            # MOD: 2024 require that the filename starts with letter A-Z or a-z
            excelfilels = list(set(glob.glob(directory+'/'+country+'/[A-z]*.xlsx'))-set(
                glob.glob(directory+'/'+country+'/*[_,-]198??*.xlsx')))
            excelfilels = sorted(excelfilels)
            print(country, sheet)
            data_row_lss = []
            i = inv_start
            for excel_file in excelfilels:
                if i > inv_end:
                    break
                i = i+1
                print(excel_file)
                xlsx = pd.ExcelFile(excel_file)
                df = pd.read_excel(
                    xlsx, sheet, keep_default_na=False, na_values=['MISSING_VALUE'])
                # print(df.head())
                # Find row by its name as Dataframe
                row_df = df[df[df.columns[1]].str.contains(
                    substr_ls[substr_ls.index(row_name)]) == True]
                # print('printing columns')
                # print(df[df.columns[1]])
                # Row as Series
                row_s = row_df.iloc[0, :]
                # Row as list
                row_ls = list(row_s)
                # Delete two first element: Title and Subdivision in CRFReporter excel
                del row_ls[0:2]
                # Append one year data
                data_row_lss.append(row_ls)
            # Data collected for one country, create data frame
            df = pd.DataFrame(data_row_lss)
            # Insert inventory years
            df.insert(0, "Year", list(range(inv_start, inv_end+1)))
            # Set the country code as index
            df.index = [country]*len(range(inv_start, inv_end+1))
            # Merge dataframes
            # df_merge=df_merge.append(df)
            df_merge = pd.concat((df_merge, df))
        # The data we want is between two empty columns. Find first the columns
        empty_col_ind = [i for i in range(df_merge.shape[1]) if (
            df_merge.iloc[:, i] == '').all()]
        df_merge = df_merge.iloc[:, empty_col_ind[0]:empty_col_ind[1]]
        # Title row
        df_merge.columns = ['Year']+columns_ls

        # set all strings to NaN
        for col in df_merge.columns:
            df_merge[col] = pd.to_numeric(df_merge[col], errors='coerce')

        # This is quick hack to return years to the dataframe. They get deleted from some reason because
        # of the nan setting operation
        df_merge['Year'] = list(range(inv_start, inv_end+1))*len(countryls)
        # All countries for one sheet done
        df_merge.to_excel(writer, sheet_name=sheet+sheet_ext, na_rep='NaN')
    return writer


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", dest="f1",
                        required=True, help="Inventory Parties Directory")
    parser.add_argument("-s", "--start", type=int, dest="f2",
                        required=True, help="Inventory start year (1990)")
    parser.add_argument("-e", "--end", type=int, dest="f3",
                        required=True, help="Inventory end year")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--eu", action="store_true", dest="eu",
                       default=False, help="EU countries")
    group.add_argument("--euplus", action="store_true", dest="euplus",
                       default=False, help="EU countries plus GBR, ISL, NOR")
    group.add_argument("-a", "--all", action="store_true",
                       dest="all", default=False, help="All countries (EU+others")
    group.add_argument("-l", "--list", action="store_true", dest="countryls", default=False,
                       help="List files in Inventory Parties Directory")
    group.add_argument("-c", "--countries", dest="country", type=str, nargs='+',
                       help="List of countries from the official acronyms separated by spaces")
    group.add_argument("--amissing", action="store_true", dest="all_missing", default=False,
                       help='All countries where some are missing. See allcountryls_missing in countrylist.py')
    args = parser.parse_args()
    directory = args.f1
    print("Inventory Parties data directory:", directory)
    inventory_start = int(args.f2)
    print("Inventory start:", inventory_start)
    inventory_end = int(args.f3)
    print("Inventory end:", inventory_end)
    file_prefix = 'EU'
    countryls = []
    if args.eu:
        print("Using EU  countries")
        countryls = euls
    elif args.euplus:
        print("Using EU  countries plus GBR, ISL and NOR")
        countryls = euplusls
        file_prefix = 'EU_GBR_ISL_NOR'
    elif args.all:
        print("Using all countries")
        countryls = allcountryls
        file_prefix = 'EU_and_Others'
    elif args.countryls:
        print("Listing countries in", args.f1)
        ls = glob.glob(args.f1+'/???')
        countryls = [pathlib.Path(x).name for x in ls]
        countryls.sort()
        file_prefix = pathlib.Path(args.f1).name
    elif args.all_missing:
        print("Using allcountry list missing")
        countryls = allcountryls_missing
        file_prefix = 'all_countries'
    else:
        print("Using countries:", args.country)
        countryls = args.country
        file_prefix = args.country[0]
        for country in args.country[1:]:
            file_prefix = file_prefix+"_"+country
    file_name = file_prefix+'_Restoration_' + \
        str(inventory_start)+'_'+str(inventory_end)+'.xlsx'
    countryls = sorted(countryls)
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    # countryls=['AUT','FIN']
    writer = CreateEUTable4Total2(
        writer, directory, countryls, inventory_start, inventory_end)
    print("Writing results to:", file_name)
    writer.close()
    print("Done")

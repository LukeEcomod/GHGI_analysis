import pathlib
import pandas as pd
import numpy as np
import math
import numbers
import glob
import argparse
import fnmatch
from countrylist import euls, euplusls, noneuls, allcountryls, allcountryls_missing, allcountryls_missing_noeua

directory = 'EU-MS/2017'
inventory_start = 1990
inventory_end = 2015

# List of excel sheets needed
sheetls = ['Table4.Gs1']
table4Gs1_sheet_name_ls = ['Table4.Gs1 Total HWP', 'Table4.Gs1 Total HWP Domestic', 'Table4.Gs1 Total HWP Exported',
                           'Table4.Gs1 Solid wood Tot', 'Table4.Gs1 Solid Domestic', 'Table4.Gs1 Solid Exported',
                           'Table4.Gs1 Paper+pboard Tot', 'Table4.Gs1 Paper+pboard Dom', 'Table4.Gs1 Paper+pboard Exp',
                           'Table4.Gs1 Other Tot', 'Table4.Gs1 Other Domestic', 'Table4.Gs1 Other Exported']
table4Gs1_row_ls = ['TOTAL HWP', 'Total', 'Solid wood',
                    'Paper and paperboard', 'Other']
patter_ls = [None, None, r'4.G*1*', r'4.G*2*', r'4.G*3*']

# List here countries that have summed exported and domestic to domestic
country_ls_included_in_domestic = ['ita']


def get_row_values(df, title_col, value_col, str_to_contain, num_expected, pat=None):
    """MOD 2024 Helper function to extract data from rows that match str_to_contain

    Args:
        df (pd.DataFrame): Excel file that is read as pandas dataframe
        title_col (str): column name which includes the titles to search for str_to_contain. title col elements have to be strings.
        value_col (int): column number from which to extract the data with df.iloc
        str_to_contain (str): string that the title col row has to contain for data to be extracted
        num_expected (int): how many values are expected
        pat (str): pattern to search for if the str_to_contain returns more rows than 
    """

    # Choose only rows that contain the string
    mask = df[title_col].str.lower().str.contains(str_to_contain.lower())
    mask = mask & mask.notna()  # if the title col contains nans
    values = df[mask].iloc[:, value_col].values
    if values.shape[0] != num_expected:
        print(
            f'Warning: got more rows than expected when searching for {str_to_contain}')
        print('This can happen especially when searching for rows starting with "other"')
        if pat is not None:
            print(f'Choosing {num_expected} first values that match pat')
            titles_mask_no_na = df[title_col].notna()
            titles_list = list(df[titles_mask_no_na].loc[:, title_col])
            rows = fnmatch.filter(titles_list, pat=pat+rf'{str_to_contain}*')
            print(pat+rf'{str_to_contain}*')
            print(rows)
            values = df.loc[df[title_col].where(
                df[title_col].isin(rows)).notna(), :].iloc[:, value_col]
            values = np.array(
                [np.nan if isinstance(i, str) else i for i in values])
        else:
            print('No pattern to search for')
            print(f'Choosing {num_expected} first values')
            values = values[:num_expected]
    return values


def append_to_lists(lists, values):
    # append in order
    for l, val in zip(lists, values):
        l.append(val)
    return lists


def remove_rows_startwith(df, title_col, title_starts_with):
    mask = df[title_col].str.strip().str.lower(
    ).str.startswith(title_starts_with)
    mask = mask & mask.notna()
    mask = ~mask
    return df[mask]


def CreateHWPExcelSheet(writer, directory, countryls, sheet, row_name_ls, col, sheet_name_ls, start, end):
    """Read CRFReporter Reporting table files (excel) for given EU countries
       for each inventory year. Find the given sheet and the given row (inventory item)
       and create a data frame row for each country for the CO2 net emission for each inventory year
       (last cell in the given row). This way one excel sheet is created including all EU countries.
       \param writer: excel writer that collects all Reporting tables into one excel file
       \param directory: directory for the countries (each country is a directory containing excel files) 
       \param countryls: list of (EU) countries
       \param sheet: the name of the excel sheet to be read
       \param row_name_ls: the row names to pick up in the sheet
       \param col: column index to data
       \parsheet_name_ls: sheet names (1.HWP Total, 2.HWP Domestic, 3.HW Exported) in the output excel file
       \param start: inventory start year
       \param end: inventory end year
    """
    # Total HWP, total HWP domestic and total HWP exported
    data_row_ls0 = []
    data_row_ls1 = []
    data_row_ls2 = []
    # Solid wood total
    data_row_ls3 = []
    # Solid wood domestic
    data_row_ls4 = []
    # Solid wood exported
    data_row_ls5 = []
    # Paper and paperboard total
    data_row_ls6 = []
    # Paper and paperboard domestic
    data_row_ls7 = []
    # Paper and paperboard exported
    data_row_ls8 = []
    # Other total
    data_row_ls9 = []
    # Other domestic
    data_row_ls10 = []
    # Other exported
    data_row_ls11 = []
    approachA_set = set()
    for country in countryls:
        # country=country.lower()
        # List all excel files and sort the files in ascending order (1990,1991,...,2015)
        # Exclude years in 1980's
        # MOD: 2024 require that the filename starts with letter A-Z or a-z
        # excelfilels=list(set(glob.glob(directory+'/'+country+'/*.xlsx'))-set(glob.glob(directory+'/'+country+'/*_198??*.xlsx')))
        excelfilels = list(set(glob.glob(directory+'/'+country+'/[A-z]*.xlsx'))-set(
            glob.glob(directory+'/'+country+'/*[_,-]198??*.xlsx')))
        excelfilels = sorted(excelfilels)
        print(country.upper(), sheet_name_ls[0],
              sheet_name_ls[1], sheet_name_ls[2])
        row_ls0 = []
        row_ls1 = []
        row_ls2 = []
        # Solid wood total
        row_ls3 = []
        # Solid wood domestic
        row_ls4 = []
        # Solid wood exported
        row_ls5 = []
        # Paper and paperboard total
        row_ls6 = []
        # Paper and paperboard domestic
        row_ls7 = []
        # Paper and paperboard exported
        row_ls8 = []
        # Other total
        row_ls9 = []
        # Other domestic
        row_ls10 = []
        # Other exported
        row_ls11 = []
        i = start
        print(excelfilels)
        if excelfilels == []:
            print("Missing country", country)
            row_ls0 = [pd.NA]*len(list(range(start, (end+1))))
            row_ls1 = [pd.NA]*len(list(range(start, (end+1))))
            row_ls2 = [pd.NA]*len(list(range(start, (end+1))))
            row_ls3 = [pd.NA]*len(list(range(start, (end+1))))
            row_ls4 = [pd.NA]*len(list(range(start, (end+1))))
            row_ls5 = [pd.NA]*len(list(range(start, (end+1))))
            row_ls5 = [pd.NA]*len(list(range(start, (end+1))))
            row_ls6 = [pd.NA]*len(list(range(start, (end+1))))
            row_ls7 = [pd.NA]*len(list(range(start, (end+1))))
            row_ls8 = [pd.NA]*len(list(range(start, (end+1))))
            row_ls9 = [pd.NA]*len(list(range(start, (end+1))))
            row_ls10 = [pd.NA]*len(list(range(start, (end+1))))
            row_ls11 = [pd.NA]*len(list(range(start, (end+1))))
        for file in excelfilels:
            if i > end:
                break
            print(i)
            i = i+1
            xlsx = pd.ExcelFile(file)
            # The default set if missing values include NA,override default values and set
            # empty string ('') as the missing value
            df1 = pd.read_excel(xlsx, sheet, keep_default_na=False, na_values=[
                                '']).dropna(axis=1, how='all').dropna(axis=0, how='all')
            index = list(df1.columns)[0]

            # MOD 2024: remove rows starting with '('. These corresponds to rows that have text explanation of the footnotes
            # and make selecting rows harder
            df1 = remove_rows_startwith(df1, index, '(')

            # MOD 2024: countries that have 'TOTAL HWP' report import+exported only, countries that don't have 'TOTAL HWP' report
            # import and export separately and searching for 'total' substring should return exactly two values first for domestic
            # and second for exported

            # MOD 2024: First check is there 'TOTAL HWP'
            is_total_hwp = df1[index].str.contains(row_name_ls[0]).any()

            if country.lower() in country_ls_included_in_domestic:
                # Country has summed exported and domestic to domestic. Take only the domestic part
                # of the array and continue
                print(
                    f'Country {country} has reported that the domestic and exported hwp are summed in domestic')
                print('Removing exported part of the table')
                mask_exported = df1.iloc[:, 0].str.lower(
                ).str.contains('exported')
                mask_exported = mask_exported & mask_exported.notna()
                rows_before_exported = [
                    i for i, me in enumerate(mask_exported) if me]
                df1 = df1.iloc[:rows_before_exported[0], :]
                is_total_hwp = True  # Set true because there is no TOTAL HWP string

            if is_total_hwp:
                # Country has reported only total hwp emissions, take that and append to row_ls0
                # mask = df1[index].str.contains(row_name_ls[0]) # Should return only one row
                # mask = mask & mask.notna() # If there are NaNs in the index column those transfer to NaNs in mask -> this line transfers NaN to False
                # total_rows = df1.loc[mask, :].iloc[:, col].values
                if country.lower() in country_ls_included_in_domestic:
                    total_rows = get_row_values(
                        df1, index, col, 'total', num_expected=1)
                else:
                    total_rows = get_row_values(
                        df1, index, col, row_name_ls[0], num_expected=1)
                if total_rows.shape[0] == 1:
                    row_ls0.append(total_rows[0])
                    # Since the country reports only total, append nan to
                    # Total hwp domestic and total hwp exported
                    row_ls1.append(np.nan)
                    row_ls2.append(np.nan)
                else:
                    print(
                        f'{country} - {file}: Total hwp reported but country has not exactly 1 total hwp row in Table4.Gs1')
                    print('Outputting nan to total, domestic and exported hwp')
                    row_ls0.append(np.nan)
                    row_ls1.append(np.nan)
                    row_ls2.append(np.nan)
            else:
                # Country has reported both total and domestic hwp emissions
                # Searches for rows that include 'total'. Should return two values. First is for domestic HWP and second for exported HWP emissions
                # mask = df1[index].str.lower().str.contains(row_name_ls[1].lower())
                # mask = mask & mask.notna() # If there are NaNs in the index column those transfer to NaNs in mask -> this line transfers NaN to False
                # total_rows = df1[mask]
                total_rows = get_row_values(
                    df1, index, col, row_name_ls[1], num_expected=2)
                # Warn if the country has something else than two rows
                if total_rows.shape[0] == 2:
                    row_ls0.append(np.sum(total_rows))
                    row_ls1.append(total_rows[0])
                    row_ls2.append(total_rows[1])
                else:
                    print(
                        f'{country} - {file}: No total hwp reported but country has not exactly 2 total rows in Table4.Gs1')
                    print('Outputting nan to total, domestic and exported hwp')
                    row_ls0.append(np.nan)
                    row_ls1.append(np.nan)
                    row_ls2.append(np.nan)

            # MOD 2024: Start collecting detailed emission information
            # It seems that every country uses Approach B so simply collect the correct rows based on is_total_hwp
            if is_total_hwp:
                # Country has only one set of detailed information
                # NB! Here we go through staticly row_ls_3-11. Better approach
                # would be to e.g., have a list of lists that can be traversed
                # with a loop. This solution keeps the old variable structure for now.
                # Consider changing in the future

                solid_wood_rows = get_row_values(
                    df1, index, col, row_name_ls[2], 1, pat=patter_ls[2])
                row_ls3.append(solid_wood_rows[0])
                row_ls4.append(np.nan)
                row_ls5.append(np.nan)

                paper_and_paperboard_rows = get_row_values(
                    df1, index, col, row_name_ls[3], 1, pat=patter_ls[3])
                row_ls6.append(paper_and_paperboard_rows[0])
                row_ls7.append(np.nan)
                row_ls8.append(np.nan)

                other_rows = get_row_values(
                    df1, index, col, row_name_ls[4], 1, pat=patter_ls[4])
                row_ls9.append(other_rows[0])
                row_ls10.append(np.nan)
                row_ls11.append(np.nan)

            else:
                solid_wood_rows = get_row_values(
                    df1, index, col, row_name_ls[2], 2, pat=patter_ls[2])
                row_ls3.append(np.sum(solid_wood_rows))
                row_ls4.append(solid_wood_rows[0])
                row_ls5.append(solid_wood_rows[1])

                paper_and_paperboard_rows = get_row_values(
                    df1, index, col, row_name_ls[3], 2, pat=patter_ls[3])
                row_ls6.append(np.sum(paper_and_paperboard_rows))
                row_ls7.append(paper_and_paperboard_rows[0])
                row_ls8.append(paper_and_paperboard_rows[1])

                other_rows = get_row_values(
                    df1, index, col, row_name_ls[4], 2, pat=patter_ls[4])
                row_ls9.append(np.sum(other_rows))
                row_ls10.append(other_rows[0])
                row_ls11.append(other_rows[1])

            # #'TOTAL HWP' give two rows
            # row0=df1[df1[index].str.contains(row_name_ls[0])==True]
            # #'Total' also gives two rows, choose both
            # row=df1[df1[index].str.contains(row_name_ls[1])==True]
            # row_ls1.append(row.iloc[0,col])
            # row_ls2.append(row.iloc[1,col])
            # To ease data processing in excel add up Domestic HWP and Exported HWP Totals
            # and insert the sum to row_ls0 instead of NaN from TOTAL HWP
            # The options are 1) notation key, 2) number or 3) missing value
            # Check first if both are string
            # if isinstance(row.iloc[0,col],str) and isinstance(row.iloc[1,col],str):
            #     row_ls0.append(row.iloc[0,col]+','+row.iloc[1,col])
            # #If either is a string the return the other one. It must be a number
            # elif not isinstance(row.iloc[0,col],str) and  isinstance(row.iloc[1,col],str):
            #     row_ls0.append(row.iloc[0,col])
            # elif isinstance(row.iloc[0,col],str) and not isinstance(row.iloc[1,col],str):
            #     row_ls0.append(row.iloc[1,col])
            # #Now we can check against NaN (missing value), both must be numbers
            # elif not np.isnan(row.iloc[0,col]) and not np.isnan(row.iloc[1,col]):
            #     row_ls0.append(row.iloc[0,col]+row.iloc[1,col])
            # else:
            #     #Party (country) has reported total only
            #     #'TOTAL HWP' give two rows.
            #     #Test if the second one has NaN or not
            #     #If notnull is true, i.e. data exists, then the country has used Approach B
            #     if pd.notnull(row0.iloc[1,col]):
            #         row_ls0.append(row0.iloc[1,col])
            #     #Otherwise this is Approach A
            #     else:
            #         row_ls0.append(row0.iloc[0,col])
            #         approachA_set.add(country.upper())
            # Collect more detailed data: 1. Solid wood, 2. Paper and paperboard and 3. Other
            # The common levels to all countries, details vary.
            # It seems countries report Apporoach B either Total HWP only or dividing between
            # Domestic and Exported (i.e. the logic above unnecessary complicated)
            # 1. Collect Solid wood, query gives 6 rows
            # df_solid_rows = df1[df1[index].str.contains(row_name_ls[2])==True]
            # #The second row gives Approach A Total HWP
            # solid = df_solid_rows.iloc[1,col]
            # if pd.notnull(solid):
            #     #There is Total HWP only
            #     row_ls3.append(solid)
            # else:
            #     #There is division between Domestic and Exported
            #     #Third and fourth row give Domestic and Exported respectively
            #     solid_domestic = df_solid_rows.iloc[2,col]
            #     solid_exported =  df_solid_rows.iloc[3,col]
            #     row_ls4.append(solid_domestic)
            #     row_ls5.append(solid_exported)
            # #2. Collect paper and paperboard, query gives 6 rows
            # df_paper_rows = df1[df1[index].str.contains(row_name_ls[3])==True]
            # paper = df_paper_rows.iloc[1,col]
            # if pd.notnull(paper):
            #     #There is Total HWP only
            #     row_ls6.append(paper)
            # else:
            #     #There is division between Domestic and Exported
            #     #Third and fourth row give Domestic and Exported respectively
            #     paper_domestic = df_paper_rows.iloc[2,col]
            #     paper_exported =  df_paper_rows.iloc[3,col]
            #     row_ls7.append(paper_domestic)
            #     row_ls8.append(paper_exported)
            # #3. Collect Other, query gives 6 rows
            # df_other_rows = df1[df1[index].str.contains(row_name_ls[4])==True]
            # other = df_paper_rows.iloc[1,col]
            # if pd.notnull(other):
            #     #There is  Total HWP only
            #     row_ls9.append(other)
            # else:
            #     #There is division between Domestic and Exported
            #     #Third and fourth row give Domestic and Exported respectively
            #     other_domestic = df_other_rows.iloc[2,col]
            #     other_exported =  df_other_rows.iloc[3,col]
            #     row_ls10.append(other_domestic)
            #     row_ls11.append(other_exported)
        # One excel done, append data
        data_row_ls0.append(row_ls0)
        data_row_ls1.append(row_ls1)
        data_row_ls2.append(row_ls2)
        data_row_ls3.append(row_ls3)
        data_row_ls4.append(row_ls4)
        data_row_ls5.append(row_ls5)
        data_row_ls6.append(row_ls6)
        data_row_ls7.append(row_ls7)
        data_row_ls8.append(row_ls8)
        data_row_ls9.append(row_ls9)
        data_row_ls10.append(row_ls10)
        data_row_ls11.append(row_ls11)
    # data_row_ls0.append(sorted(list(approachA_set))+['']*(len(list(range(start,end+1)))-len(list(approachA_set))))
    # All is done, create dataframes
    df_total = pd.DataFrame(data_row_ls0)
    df_domestic = pd.DataFrame(data_row_ls1)
    df_export = pd.DataFrame(data_row_ls2)
    df_solid = pd.DataFrame(data_row_ls3)
    df_solid_domestic = pd.DataFrame(data_row_ls4)
    df_solid_exported = pd.DataFrame(data_row_ls5)
    df_paper = pd.DataFrame(data_row_ls6)
    df_paper_domestic = pd.DataFrame(data_row_ls7)
    df_paper_exported = pd.DataFrame(data_row_ls8)
    df_other = pd.DataFrame(data_row_ls9)
    df_other_domestic = pd.DataFrame(data_row_ls10)
    df_other_exported = pd.DataFrame(data_row_ls11)
    # Create excel sheets
    # Total
    df_total.index = countryls  # +['Approach A']
    df_total.columns = list(range(start, end+1))
    # df_total.to_excel(writer,sheet_name=sheet_name_ls[0],na_rep='NaN')
    df_domestic.index = countryls
    df_domestic.columns = list(range(start, end+1))
    # df_domestic.to_excel(writer,sheet_name=sheet_name_ls[1],na_rep='NaN')
    df_export.index = countryls
    df_export.columns = list(range(start, end+1))
    # df_export.to_excel(writer,sheet_name=sheet_name_ls[2],na_rep='NaN')
    # Solid
    df_solid.index = countryls
    df_solid.columns = list(range(start, end+1))
    # df_solid.to_excel(writer,sheet_name=sheet_name_ls[3],na_rep='NaN')
    df_solid_domestic.index = countryls
    df_solid_domestic.columns = list(range(start, end+1))
    # df_solid_domestic.to_excel(writer,sheet_name=sheet_name_ls[4],na_rep='NaN')
    df_solid_exported.index = countryls
    df_solid_exported.columns = list(range(start, end+1))
    # df_solid_exported.to_excel(writer,sheet_name=sheet_name_ls[5],na_rep='NaN')
    # Paper and paperboard
    df_paper.index = countryls
    df_paper.columns = list(range(start, end+1))
    # df_paper.to_excel(writer,sheet_name=sheet_name_ls[6],na_rep='NaN')
    df_paper_domestic.index = countryls
    df_paper_domestic.columns = list(range(start, end+1))
    # df_paper_domestic.to_excel(writer,sheet_name=sheet_name_ls[7],na_rep='NaN')
    df_paper_exported.index = countryls
    df_paper_exported.columns = list(range(start, end+1))
    # df_paper_exported.to_excel(writer,sheet_name=sheet_name_ls[8],na_rep='NaN')
    # Other
    df_other.index = countryls
    df_other.columns = list(range(start, end+1))
    # df_other.to_excel(writer,sheet_name=sheet_name_ls[9],na_rep='NaN')
    df_other_domestic.index = countryls
    df_other_domestic.columns = list(range(start, end+1))
    # df_other_domestic.to_excel(writer,sheet_name=sheet_name_ls[10],na_rep='NaN')
    df_other_exported.index = countryls
    df_other_exported.columns = list(range(start, end+1))
    # df_other_exported.to_excel(writer,sheet_name=sheet_name_ls[11],na_rep='NaN')
    # Save dataframes to excel
    for i, data in enumerate([df_total, df_domestic, df_export, df_solid, df_solid_domestic,
                              df_solid_exported, df_paper, df_paper_domestic, df_paper_exported,
                              df_other, df_other_domestic, df_other_exported]):
        data = data.transpose().unstack().reset_index().rename(columns={
            'level_0': 'country', 'level_1': 'year', 0: 'Net emissions / removals from HWP in use (kt CO2)'})
        data.to_excel(writer, sheet_name=sheet_name_ls[i], na_rep='NaN')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", dest="f1",
                        required=True, help="Inventory Parties Directory")
    parser.add_argument("-s", "--start", dest="f2", required=True,
                        help="Inventory start year (usually 1990)")
    parser.add_argument("-e", "--end", dest="f3",
                        required=True, help="Inventory end year")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--eu", action="store_true", dest="eu",
                       default=False, help="EU countries")
    group.add_argument("--euplus", action="store_true", dest="euplus",
                       default=False, help="EU countries plus GBR, ISL and NOR")
    group.add_argument("-a", "--all", action="store_true",
                       dest="all", default=False, help="All countries (EU+others")
    group.add_argument("-c", "--countries", dest="country",
                       type=str, nargs='+', help="List of countries")
    group.add_argument("-l", "--list", action="store_true", dest="countryls", default=False,
                       help="List files in Inventory Parties Directory")
    group.add_argument("--amissing", action="store_true", dest="all_missing", default=False,
                       help='All countries where some are missing. See allcountryls_missing in countrylist.py')
    group.add_argument("--amissingnoeua", action="store_true", dest="all_missing_no_eua", default=False,
                help='All countries where some are missing, no EUA. See allcountryls_missing in countrylist.py')

    args = parser.parse_args()
    directory = args.f1
    print("Inventory Parties directory", directory)
    inventory_start = int(args.f2)
    print("Inventory start", inventory_start)
    inventory_end = int(args.f3)
    print("Inventory end", inventory_end)
    file_prefix = 'EU'
    if args.eu:
        print("Using EU  countries")
        countryls = euls
    elif args.euplus:
        print("Using EU  countries plus GBR, ISL, NOR")
        countryls = euplusls
        file_prefix = 'EU_GBR_ISL_NOR'
    elif args.all:
        print("Using all countries")
        countryls = euls+noneuls
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
        file_prefix = 'all_countries_some_missing'
    elif args.all_missing_no_eua:
        print("Using allcountry list missing")
        countryls = allcountryls_missing_noeua
        file_prefix = 'all_countries_no_EUA'
    else:
        print("Using countries", args.country)
        countryls = args.country
        file_prefix = countryls[0]
        for country in countryls[1:]:
            file_prefix = file_prefix+"_"+country
    # countryls = ['AUT','FIN','ITA']
    writer = pd.ExcelWriter(file_prefix+'_Table4.Gs1_HWP_'+str(inventory_start)+'_'+str(inventory_end)+'.xlsx',
                            engine='xlsxwriter')
    # 1. Table4G.s1
    CreateHWPExcelSheet(writer, args.f1, countryls, sheetls[0],
                        table4Gs1_row_ls, 5, table4Gs1_sheet_name_ls, inventory_start, inventory_end)

    # CreateHWPExcelSheet(writer, args.f1, ['ITA'], sheetls[0],
    #                 table4Gs1_row_ls, 5, table4Gs1_sheet_name_ls, inventory_start, inventory_end)
    writer.close()

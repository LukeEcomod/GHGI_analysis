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
table4Gs1_sheet_name_ls = ['Total HWP gains', 'Total HWP losses',
                           'Total HWP Domestic gains', 'Total HWP Domestic losses',
                           'Total HWP Exported gains', 'Total HWP Exported losses',
                           'Solid wood Tot gains', 'Solid wood Tot losses',
                           'Solid Domestic gains', 'Solid Domestic losses',
                           'Solid Exported gains', 'Solid Exported losses',
                           'Paper+pboard Tot gains', 'Paper+pboard Tot losses',
                           'Paper+pboard Dom gains', 'Paper+pboard Dom losses',
                           'Paper+pboard Exp gains', 'Paper+pboard Exp losses',
                           'Other Tot gains', 'Other Tot losses',
                           'Other Domestic gains', 'Other Domestic losses',
                           ' Other Exported gains', 'Other Exported losses']
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


def CreateHWPExcelSheet(writer, directory, countryls, sheet, row_name_ls, cols, sheet_name_ls, start, end):
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
    data_row_ls0_gains = []
    data_row_ls1_gains = []
    data_row_ls2_gains = []

    data_row_ls0_losses = []
    data_row_ls1_losses = []
    data_row_ls2_losses = []
    # Solid wood total
    data_row_ls3_gains = []
    data_row_ls3_losses = []
    # Solid wood domestic
    data_row_ls4_gains = []
    data_row_ls4_losses = []
    # Solid wood exported
    data_row_ls5_gains = []
    data_row_ls5_losses = []
    # Paper and paperboard total
    data_row_ls6_gains = []
    data_row_ls6_losses = []
    # Paper and paperboard domestic
    data_row_ls7_gains = []
    data_row_ls7_losses = []
    # Paper and paperboard exported
    data_row_ls8_gains = []
    data_row_ls8_losses = []
    # Other total
    data_row_ls9_gains = []
    data_row_ls9_losses = []
    # Other domestic
    data_row_ls10_gains = []
    data_row_ls10_losses = []
    # Other exported
    data_row_ls11_gains = []
    data_row_ls11_losses = []
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
        row_ls0_gains = []
        row_ls0_losses = []

        row_ls1_gains = []
        row_ls1_losses = []

        row_ls2_gains = []
        row_ls2_losses = []

        # Solid wood total
        row_ls3_gains = []
        row_ls3_losses = []

        # Solid wood domestic
        row_ls4_gains = []
        row_ls4_losses = []

        # Solid wood exported
        row_ls5_gains = []
        row_ls5_losses = []

        # Paper and paperboard total
        row_ls6_gains = []
        row_ls6_losses = []

        # Paper and paperboard domestic
        row_ls7_gains = []
        row_ls7_losses = []

        # Paper and paperboard exported
        row_ls8_gains = []
        row_ls8_losses = []

        # Other total
        row_ls9_gains = []
        row_ls9_losses = []

        # Other domestic
        row_ls10_gains = []
        row_ls10_losses = []

        # Other exported
        row_ls11_gains = []
        row_ls11_losses = []

        i = start
        print(excelfilels)
        if excelfilels == []:
            print("Missing country", country)
            row_ls0_gains = [pd.NA]*len(list(range(start, (end+1))))
            row_ls1_gains = [pd.NA]*len(list(range(start, (end+1))))
            row_ls2_gains = [pd.NA]*len(list(range(start, (end+1))))
            row_ls3_gains = [pd.NA]*len(list(range(start, (end+1))))
            row_ls4_gains = [pd.NA]*len(list(range(start, (end+1))))
            row_ls5_gains = [pd.NA]*len(list(range(start, (end+1))))
            row_ls6_gains = [pd.NA]*len(list(range(start, (end+1))))
            row_ls7_gains = [pd.NA]*len(list(range(start, (end+1))))
            row_ls8_gains = [pd.NA]*len(list(range(start, (end+1))))
            row_ls9_gains = [pd.NA]*len(list(range(start, (end+1))))
            row_ls10_gains = [pd.NA]*len(list(range(start, (end+1))))
            row_ls11_gains = [pd.NA]*len(list(range(start, (end+1))))

            row_ls0_losses = [pd.NA]*len(list(range(start, (end+1))))
            row_ls1_losses = [pd.NA]*len(list(range(start, (end+1))))
            row_ls2_losses = [pd.NA]*len(list(range(start, (end+1))))
            row_ls3_losses = [pd.NA]*len(list(range(start, (end+1))))
            row_ls4_losses = [pd.NA]*len(list(range(start, (end+1))))
            row_ls5_losses = [pd.NA]*len(list(range(start, (end+1))))
            row_ls6_losses = [pd.NA]*len(list(range(start, (end+1))))
            row_ls7_losses = [pd.NA]*len(list(range(start, (end+1))))
            row_ls8_losses = [pd.NA]*len(list(range(start, (end+1))))
            row_ls9_losses = [pd.NA]*len(list(range(start, (end+1))))
            row_ls10_losses = [pd.NA]*len(list(range(start, (end+1))))
            row_ls11_losses = [pd.NA]*len(list(range(start, (end+1))))
        for file in excelfilels:
            if i > end:
                break
            print(i)
            i = i+1
            print(file)
            xlsx = pd.ExcelFile(file)
            # MOD 2026: for some reason EUA has now "Table4.Gs1 " (with trailing whitespace)
            # The loop below finds the correct sheet name
            for sheet_name in xlsx.sheet_names:
                if sheet.strip().lower() == sheet_name.strip().lower():
                    sheet_to_use = sheet_name

            print(f'Using sheet name {sheet_to_use} (correct one was {sheet})')

            # The default set if missing values include NA,override default values and set
            # empty string ('') as the missing value

            df1 = pd.read_excel(xlsx, sheet_to_use, keep_default_na=False, na_values=[
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
                    gains_rows = get_row_values(
                        df1, index, cols[0], 'total', num_expected=1)
                    losses_rows = get_row_values(
                        df1, index, cols[1], 'total', num_expected=1)
                else:
                    gains_rows = get_row_values(
                        df1, index, cols[0], row_name_ls[0], num_expected=1)
                    losses_rows = get_row_values(
                        df1, index, cols[1], row_name_ls[0], num_expected=1)
                    # total_rows = get_row_values(df1, index, cols[0], row_name_ls[0], num_expected=1)
                if gains_rows.shape[0] == 1:
                    row_ls0_gains.append(gains_rows[0])
                    # Since the country reports only total, append nan to
                    # Total hwp domestic and total hwp exported
                    row_ls1_gains.append(np.nan)
                    row_ls2_gains.append(np.nan)
                else:
                    print(
                        f'{country} - {file}: Total hwp reported but country has not exactly 1 total hwp row in Table4.Gs1')
                    print('Outputting nan to total, domestic and exported hwp')
                    row_ls0_gains.append(np.nan)
                    row_ls1_gains.append(np.nan)
                    row_ls2_gains.append(np.nan)

                if losses_rows.shape[0] == 1:
                    row_ls0_losses.append(losses_rows[0])
                    # Since the country reports only total, append nan to
                    # Total hwp domestic and total hwp exported)
                    row_ls1_losses.append(np.nan)
                    row_ls2_losses.append(np.nan)
                else:
                    print(
                        f'{country} - {file}: Total hwp reported but country has not exactly 1 total hwp row in Table4.Gs1')
                    print('Outputting nan to total, domestic and exported hwp')
                    row_ls0_losses.append(np.nan)
                    row_ls1_losses.append(np.nan)
                    row_ls2_losses.append(np.nan)
            else:
                # Country has reported both total and domestic hwp emissions
                # Searches for rows that include 'total'. Should return two values. First is for domestic HWP and second for exported HWP emissions
                # mask = df1[index].str.lower().str.contains(row_name_ls[1].lower())
                # mask = mask & mask.notna() # If there are NaNs in the index column those transfer to NaNs in mask -> this line transfers NaN to False
                # total_rows = df1[mask]
                gains_rows = get_row_values(
                    df1, index, cols[0], row_name_ls[1], num_expected=2)
                losses_rows = get_row_values(
                    df1, index, cols[1], row_name_ls[1], num_expected=2)
                # Warn if the country has something else than two rows
                if gains_rows.shape[0] == 2:
                    row_ls0_gains.append(np.sum(gains_rows))
                    row_ls1_gains.append(gains_rows[0])
                    row_ls2_gains.append(gains_rows[1])
                else:
                    print(
                        f'{country} - {file}: No total hwp reported but country has not exactly 2 total rows in Table4.Gs1')
                    print('Outputting nan to total, domestic and exported hwp')
                    row_ls0_gains.append(np.nan)
                    row_ls1_gains.append(np.nan)
                    row_ls2_gains.append(np.nan)

                if losses_rows.shape[0] == 2:
                    row_ls0_losses.append(np.sum(losses_rows))
                    row_ls1_losses.append(losses_rows[0])
                    row_ls2_losses.append(losses_rows[1])
                else:
                    print(
                        f'{country} - {file}: No total hwp reported but country has not exactly 2 total rows in Table4.Gs1')
                    print('Outputting nan to total, domestic and exported hwp')
                    row_ls0_losses.append(np.nan)
                    row_ls1_losses.append(np.nan)
                    row_ls2_losses.append(np.nan)

            # MOD 2024: Start collecting detailed emission information
            # It seems that every country uses Approach B so simply collect the correct rows based on is_total_hwp
            if is_total_hwp:
                # Country has only one set of detailed information
                # NB! Here we go through staticly row_ls_3-11. Better approach
                # would be to e.g., have a list of lists that can be traversed
                # with a loop. This solution keeps the old variable structure for now.
                # Consider changing in the future

                solid_wood_rows_gains = get_row_values(
                    df1, index, cols[0], row_name_ls[2], 1, pat=patter_ls[2])
                row_ls3_gains.append(solid_wood_rows_gains[0])
                row_ls4_gains.append(np.nan)
                row_ls5_gains.append(np.nan)

                solid_wood_rows_losses = get_row_values(
                    df1, index, cols[1], row_name_ls[2], 1, pat=patter_ls[2])
                row_ls3_losses.append(solid_wood_rows_losses[0])
                row_ls4_losses.append(np.nan)
                row_ls5_losses.append(np.nan)

                paper_and_paperboard_rows_gains = get_row_values(
                    df1, index, cols[0], row_name_ls[3], 1, pat=patter_ls[3])
                row_ls6_gains.append(paper_and_paperboard_rows_gains[0])
                row_ls7_gains.append(np.nan)
                row_ls8_gains.append(np.nan)

                paper_and_paperboard_rows_losses = get_row_values(
                    df1, index, cols[1], row_name_ls[3], 1, pat=patter_ls[3])
                row_ls6_losses.append(paper_and_paperboard_rows_losses[0])
                row_ls7_losses.append(np.nan)
                row_ls8_losses.append(np.nan)

                other_rows_gains = get_row_values(
                    df1, index, cols[0], row_name_ls[4], 1, pat=patter_ls[4])
                row_ls9_gains.append(other_rows_gains[0])
                row_ls10_gains.append(np.nan)
                row_ls11_gains.append(np.nan)

                other_rows_losses = get_row_values(
                    df1, index, cols[1], row_name_ls[4], 1, pat=patter_ls[4])
                row_ls9_losses.append(other_rows_losses[0])
                row_ls10_losses.append(np.nan)
                row_ls11_losses.append(np.nan)

            else:
                solid_wood_rows_gains = get_row_values(
                    df1, index, cols[0], row_name_ls[2], 2, pat=patter_ls[2])
                row_ls3_gains.append(np.sum(solid_wood_rows_gains))
                row_ls4_gains.append(solid_wood_rows_gains[0])
                row_ls5_gains.append(solid_wood_rows_gains[1])

                solid_wood_rows_losses = get_row_values(
                    df1, index, cols[1], row_name_ls[2], 2, pat=patter_ls[2])
                row_ls3_losses.append(np.sum(solid_wood_rows_losses))
                row_ls4_losses.append(solid_wood_rows_losses[0])
                row_ls5_losses.append(solid_wood_rows_losses[1])

                paper_and_paperboard_rows_gains = get_row_values(
                    df1, index, cols[0], row_name_ls[3], 2, pat=patter_ls[3])
                row_ls6_gains.append(np.sum(paper_and_paperboard_rows_gains))
                row_ls7_gains.append(paper_and_paperboard_rows_gains[0])
                row_ls8_gains.append(paper_and_paperboard_rows_gains[1])

                paper_and_paperboard_rows_losses = get_row_values(
                    df1, index, cols[1], row_name_ls[3], 2, pat=patter_ls[3])
                row_ls6_losses.append(np.sum(paper_and_paperboard_rows_losses))
                row_ls7_losses.append(paper_and_paperboard_rows_losses[0])
                row_ls8_losses.append(paper_and_paperboard_rows_losses[1])

                other_rows_gains = get_row_values(
                    df1, index, cols[0], row_name_ls[4], 2, pat=patter_ls[4])
                row_ls9_gains.append(np.sum(other_rows_gains))
                row_ls10_gains.append(other_rows_gains[0])
                row_ls11_gains.append(other_rows_gains[1])

                other_rows_losses = get_row_values(
                    df1, index, cols[1], row_name_ls[4], 2, pat=patter_ls[4])
                row_ls9_losses.append(np.sum(other_rows_losses))
                row_ls10_losses.append(other_rows_losses[0])
                row_ls11_losses.append(other_rows_losses[1])
        # One excel done, append data
        data_row_ls0_gains.append(row_ls0_gains)
        data_row_ls1_gains.append(row_ls1_gains)
        data_row_ls2_gains.append(row_ls2_gains)

        data_row_ls0_losses.append(row_ls0_losses)
        data_row_ls1_losses.append(row_ls1_losses)
        data_row_ls2_losses.append(row_ls2_losses)
        data_row_ls3_gains.append(row_ls3_gains)
        data_row_ls4_gains.append(row_ls4_gains)
        data_row_ls5_gains.append(row_ls5_gains)
        data_row_ls6_gains.append(row_ls6_gains)
        data_row_ls7_gains.append(row_ls7_gains)
        data_row_ls8_gains.append(row_ls8_gains)
        data_row_ls9_gains.append(row_ls9_gains)
        data_row_ls10_gains.append(row_ls10_gains)
        data_row_ls11_gains.append(row_ls11_gains)

        data_row_ls3_losses.append(row_ls3_losses)
        data_row_ls4_losses.append(row_ls4_losses)
        data_row_ls5_losses.append(row_ls5_losses)
        data_row_ls6_losses.append(row_ls6_losses)
        data_row_ls7_losses.append(row_ls7_losses)
        data_row_ls8_losses.append(row_ls8_losses)
        data_row_ls9_losses.append(row_ls9_losses)
        data_row_ls10_losses.append(row_ls10_losses)
        data_row_ls11_losses.append(row_ls11_losses)
    # data_row_ls0.append(sorted(list(approachA_set))+['']*(len(list(range(start,end+1)))-len(list(approachA_set))))
    # All is done, create dataframes
    df_total_gains = pd.DataFrame(data_row_ls0_gains)
    df_domestic_gains = pd.DataFrame(data_row_ls1_gains)
    df_export_gains = pd.DataFrame(data_row_ls2_gains)

    df_total_losses = pd.DataFrame(data_row_ls0_losses)
    df_domestic_losses = pd.DataFrame(data_row_ls1_losses)
    df_export_losses = pd.DataFrame(data_row_ls2_losses)
    df_solid_gains = pd.DataFrame(data_row_ls3_gains)
    df_solid_domestic_gains = pd.DataFrame(data_row_ls4_gains)
    df_solid_exported_gains = pd.DataFrame(data_row_ls5_gains)
    df_paper_gains = pd.DataFrame(data_row_ls6_gains)
    df_paper_domestic_gains = pd.DataFrame(data_row_ls7_gains)
    df_paper_exported_gains = pd.DataFrame(data_row_ls8_gains)
    df_other_gains = pd.DataFrame(data_row_ls9_gains)
    df_other_domestic_gains = pd.DataFrame(data_row_ls10_gains)
    df_other_exported_gains = pd.DataFrame(data_row_ls11_gains)

    df_solid_losses = pd.DataFrame(data_row_ls3_losses)
    df_solid_domestic_losses = pd.DataFrame(data_row_ls4_losses)
    df_solid_exported_losses = pd.DataFrame(data_row_ls5_losses)
    df_paper_losses = pd.DataFrame(data_row_ls6_losses)
    df_paper_domestic_losses = pd.DataFrame(data_row_ls7_losses)
    df_paper_exported_losses = pd.DataFrame(data_row_ls8_losses)
    df_other_losses = pd.DataFrame(data_row_ls9_losses)
    df_other_domestic_losses = pd.DataFrame(data_row_ls10_losses)
    df_other_exported_losses = pd.DataFrame(data_row_ls11_losses)
    # Create excel sheets
    # Total
    df_total_gains.index = countryls  # +['Approach A']
    df_total_losses.index = countryls

    df_total_gains.columns = list(range(start, end+1))
    df_total_losses.columns = list(range(start, end+1))

    df_domestic_gains.index = countryls
    df_domestic_gains.columns = list(range(start, end+1))

    df_domestic_losses.index = countryls
    df_domestic_losses.columns = list(range(start, end+1))

    df_export_gains.index = countryls
    df_export_gains.columns = list(range(start, end+1))

    df_export_losses.index = countryls
    df_export_losses.columns = list(range(start, end+1))

    # # Solid
    df_solid_gains.index = countryls
    df_solid_gains.columns = list(range(start,end+1))

    df_solid_losses.index = countryls
    df_solid_losses.columns = list(range(start, end+1))

    df_solid_domestic_gains.index = countryls
    df_solid_domestic_gains.columns = list(range(start,end+1))

    df_solid_domestic_losses.index = countryls
    df_solid_domestic_losses.columns = list(range(start,end+1))

    df_solid_exported_gains.index = countryls
    df_solid_exported_gains.columns = list(range(start,end+1))

    df_solid_exported_losses.index = countryls
    df_solid_exported_losses.columns = list(range(start,end+1))
    #Paper and paperboard
    df_paper_gains.index = countryls
    df_paper_gains.columns = list(range(start,end+1))

    df_paper_losses.index = countryls
    df_paper_losses.columns = list(range(start,end+1))
    #df_paper.to_excel(writer,sheet_name=sheet_name_ls[6],na_rep='NaN')
    df_paper_domestic_gains.index = countryls
    df_paper_domestic_gains.columns = list(range(start,end+1))

    df_paper_domestic_losses.index = countryls
    df_paper_domestic_losses.columns = list(range(start,end+1))
    #df_paper_domestic.to_excel(writer,sheet_name=sheet_name_ls[7],na_rep='NaN')
    df_paper_exported_gains.index = countryls
    df_paper_exported_gains.columns = list(range(start,end+1))

    df_paper_exported_losses.index = countryls
    df_paper_exported_losses.columns = list(range(start,end+1))
    #df_paper_exported.to_excel(writer,sheet_name=sheet_name_ls[8],na_rep='NaN')
    #Other
    df_other_gains.index = countryls
    df_other_gains.columns = list(range(start,end+1))

    df_other_losses.index = countryls
    df_other_losses.columns = list(range(start,end+1))
    #df_other.to_excel(writer,sheet_name=sheet_name_ls[9],na_rep='NaN')
    df_other_domestic_gains.index = countryls
    df_other_domestic_gains.columns = list(range(start,end+1))

    df_other_domestic_losses.index = countryls
    df_other_domestic_losses.columns = list(range(start,end+1))
    #df_other_domestic.to_excel(writer,sheet_name=sheet_name_ls[10],na_rep='NaN')
    df_other_exported_gains.index = countryls
    df_other_exported_gains.columns = list(range(start,end+1))

    df_other_exported_losses.index = countryls
    df_other_exported_losses.columns = list(range(start,end+1))
    #df_other_exported.to_excel(writer,sheet_name=sheet_name_ls[11],na_rep='NaN')
    # Save dataframes to excel
    for i, data in enumerate([df_total_gains, df_total_losses, df_domestic_gains, df_domestic_losses, df_export_gains, df_export_losses,
                              df_solid_gains, df_solid_losses, df_solid_domestic_gains, df_solid_domestic_losses, df_solid_exported_gains, df_solid_exported_losses,
                              df_paper_gains, df_paper_losses, df_paper_domestic_gains, df_paper_domestic_losses, df_paper_exported_gains, df_paper_exported_losses,
                              df_other_gains, df_other_losses, df_other_domestic_gains, df_other_domestic_losses, df_other_exported_gains, df_other_exported_losses]):
        if i==7 or i==6:
            print(f'{i}: data before')
            print(data)
        data = data.transpose().unstack().reset_index().rename(columns={
            'level_0': 'country', 'level_1': 'year', 0: 'HWP in use from domestic harvest (kt C)'})
        if i==7 or i==6:
            print(f'{i}: data after')
            print(data)
        data.to_excel(writer, sheet_name=sheet_name_ls[i], na_rep='NaN')

    # for i, data in enumerate([df_total_gains, df_total_losses,
    #                           df_domestic_gains, df_domestic_losses,
    #                           df_export_gains, df_export_losses]):
    #     print(data.head())
        # data = data.transpose().unstack().reset_index().rename(columns={
        #     'level_0': 'country', 'level_1': 'year', 0: 'Net emissions / removals from HWP in use (kt CO2)'})
        # data.to_excel(writer, sheet_name=sheet_name_ls[i], na_rep='NaN')


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
        file_prefix = 'all_countries'
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

    writer = pd.ExcelWriter(file_prefix+'_Table4.Gs1_HWP_gains_losses_'+str(inventory_start)+'_'+str(inventory_end)+'.xlsx',
                            engine='xlsxwriter')
    # 1. Table4G.s1
    # countryls = ['FIN', 'ITA', 'AUT']
    CreateHWPExcelSheet(writer, args.f1, countryls, sheetls[0],
                        table4Gs1_row_ls, [1, 2], table4Gs1_sheet_name_ls, inventory_start, inventory_end)

    # CreateHWPExcelSheet(writer, args.f1, ['ITA'], sheetls[0],
    #                 table4Gs1_row_ls, 5, table4Gs1_sheet_name_ls, inventory_start, inventory_end)
    writer.close()

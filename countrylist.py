euls=['FIN','AUT','BEL','BGR','CYP','CZE','DEU',
      'DNK','ESP','EST','FRA','GRC','HRV',
      'HUN','IRL','ITA','LTU','LUX','LVA',
      'MLT','NLD','POL','PRT','ROU','SVK',
      'SVN','SWE']
euplusls = euls+['GBR','ISL','NOR']
noneuls=['CAN','CHE','EUA','GBR','ISL','JPN','LIE','MCO','NOR','RUS','TUR','USA']
allcountryls=euls+noneuls

noneuls_short = ['EUA','CAN','CHE','GBR','ISL','JPN','LIE','MCO','NOR','RUS','TUR'] # USA, AUS missing
noneuls_short_no_eua = ['CAN','CHE','GBR','ISL','JPN','LIE','MCO','NOR','RUS','TUR'] # USA, AUS missing, no EUA
euls_short = ['FIN','AUT','BEL','BGR','CZE','DEU',
      'DNK','ESP','EST','FRA','GRC','HRV',
      'IRL','ITA','LTU','LUX','LVA',
      'MLT','NLD','POL','PRT','ROU','SVK',
      'SVN','SWE'] # HUN, CYP missing

allcountryls_missing = noneuls_short + euls_short
allcountryls_missing_noeua = noneuls_short_no_eua + euls_short

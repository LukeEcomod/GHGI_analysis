# UNFCCC greenhouse gas inventory analysis

This repository is a reproducibility package for results in Böttcher et al., (2026) currently in review. 

## File description

These files provide the codes for creating the summary excel files and scripts for creating the figures in the manuscript.

The python codes are forked from [https://github.com/jariperttunen/eughgsummary](https://github.com/jariperttunen/eughgsummary) and updated to account for changes in the common reporting table (CRT) for year 2025. R codes produce the figures.

### countrylist.py
This file contains lists of different countries that are used in running the other modules.

### euco2hpw_gains_losses.py
The script collects gains and losses for each reported category from harvested wood producs (HWP). The reported categories are solid wood, paper + paperboard nad other. For each category the script collects domestic gains, domestic losses, exported gains and exported losses and total gains and total losses. Note that some countries report only total gains and losses while others report both domestic and exported gains and losses.

### euco2hwp.py
The script collects net emissions Harvested wood products (HWP) data for Total HWP, Total HWP Domestic, Total HWP Exported and total, domestic and exported emissions for solid wood, paper+paperboard and other wood from the Table4.Gs1. Note a country may have reported Total HWP only. Whether Apporoach A or B is used is not explicitely mentioned. The output is a single file with three sheets for HWP net emissions.

### eulandtransitionmatrix.py
Reproduce Table4.1 Land Transition Matrix in Excel by folding it out by inventory parties 
for inventory years. Each land transition is on a separate Excel sheet.  

>[!NOTE]
>To reproduce Table4.1 in Excel may take some time, up to 8 hours.

### eurestoration.py
Collect row 10 from Table4A-Table4D.

### python_CLI_args_runs_20260109.sh
Terminal commands used to run the python files to produce the excel files in sheets folder.

### UNFCCC_data_figures.R
Produces figures 1-4 in the article.

### UNFCCC_data_LUC.R
Produces deforestation and afforestation figures in the supplementary material of the article.

## Additional data needed to produce the results
- The CRTs for each country are not included in this repository. These can be downloaded from [https://unfccc.int/ghg-inventories-annex-i-parties/2025](https://unfccc.int/ghg-inventories-annex-i-parties/2025)

- Python environment for running the python scripts.
  - The repository contains [requirements.txt](requirementes.txt) that can be used to install required python packages
  - Python environments can be created e.g., with pip and macOS / unix
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```


## Contact

Further questions should be directed to

Olli-Pekka Tikkasalo ([olli-pekka.tikkasalo@luke.fi](olli-pekka.tikkasalo@luke.fi))

Aleksi Lehtonen ([aleksi.lehtonen@luke.fi](aleksi.lehtonen@luke.fi))

Hannes Böttcher ([H.Boettcher@oeko.de](H.Boettcher@oeko.de))




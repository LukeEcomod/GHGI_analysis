

## Python virtual environment
The `requirements.txt`  contains information for `pip` to install python packages
required by *eughgsummary*. First, create [python virtual environment](https://docs.python.org/3/library/venv.html), 
activate it and install the packages:

+ pip  install -r requirements.txt
 
You may need to tell the proxy server for `pip`.

## Common command line arguments
The scripts have the following common command line arguments:
+ -h: Python command line help
+ -d: The main directory for the CRF Reporting tables. It is assumed the excel files are
      organised in this directory by countries (inventory parties) denoted with three letter acronyms.
+ -s: Start year of the inventory.
+ -e: End year of the inventory.

To select countries one of the following must be used in the command line:
+ --eu: EU countries.
+ --euplus: EU plus GBR, ISL and NOR
+ --all: All reporting countries.
+ --countries: List of country acronyms separated by spaces.
+ --list: Use the countries in source directory pointed to with the option -d

Some countries report years in 1980's. These are filtered out.

## euco2hwp.py
The script collects net emissions Harvested wood products (HWP) data for Total HWP, Total HWP Domestic
and Total HWP Exported from the Table4.Gs1. Note a country may have reported Total HWP only.
Whether Apporoach A or B is used is not explicitely mentioned. The output is a single
file with three sheets for HWP net emissions.
  
## eurestoration.py
Collect row 10 from Table4A-Table4D.

##  eulandtransitionmatrix.py
Reproduce Table4.1 Land Transition Matrix in Excel by folding it out by inventory parties 
for inventory years. Each land transition is on a separate Excel sheet.  

>[!NOTE]
>To reproduce Table4.1 in Excel may take some time, up to 8 hours. Use the Slurm  workload manager in sorvi to run the
>`eulandtransitionmatrix.slurm` script.



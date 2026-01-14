# d2d-oco3-tools
Tools for processing OCO-3 netcdf data. Part of the 2025-2026 Data to Discovery (D2D) program.

#### Convert nc4 to csv 
- open the file "nc4_plot.ipynb" in Google Colab
- There are multiple tools in there. Tool 1 is for processing nc4 files directly from the cloud (without local downloads) and into an aggregated CSV. This is probably the most useful!
- Tools 2 and 3 are in progress.
- Tool 4 is for the same process from locally downloaded files on Gdrive, and Tool 5 is for data exploration of variables within an NC4 file. 

#### Batch download nc4 files:
- Create an EarthData login profile at urs.earthdata.nasa.gov 
- Go to "https://disc.gsfc.nasa.gov/datasets/OCO3_L2_Lite_FP_11r/summary?keywords=oco3", select "Subset/ Get Data"
- Filter for what you need by location ("Refine Region" - e.g. Los Angeles's boundary is  -120, 32, -116, 36) and time ("Refine Date Range"), select "Get Data"
- Under "Web Links" option, select "Download Links List", this will generate a .txt file in your Downloads folder. (side note: If you click on the nc4 files individually you will get the file downloaded directly, but this gets cumbersome for batch downloads.)
- Generate a bearer token for your EarthData at https://urs.earthdata.nasa.gov/profile
- Set file input and output paths in nc4-dl.py for the txt file, and add in your bearer token.
- Run "python nc4-dl.py" in terminal. 
- Delete bearer token from nc4-dl.py after files are downloaded!

#### Other useful OCO-3 processing tools
- https://github.com/robrnelson/OCO3_Tools
- https://github.com/EarthDigitalTwin/FireAlarm-notebooks/blob/main/9.%20OCO3.ipynb

#### Data sources (different ways of accessing the same OCO-3 files)
- CO2: https://disc.gsfc.nasa.gov/datasets/OCO3_L2_Lite_FP_11r/summary?keywords=oco3
- SIF: https://disc.gsfc.nasa.gov/datasets/OCO3_L2_Lite_SIF_11r/summary?keywords=oco3
- https://oco2.gesdisc.eosdis.nasa.gov/data/OCO3_DATA/OCO3_L2_Lite_FP.11r/
- Tips for accessing cloud nc4 files: https://disc.gsfc.nasa.gov/information/documents?title=Data%20Access#mac_linux_wget

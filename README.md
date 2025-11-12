# d2d-oco3-tools
Tools for processing OCO-3 netcdf data. Part of the 2025-2026 Data to Discovery (D2D) program.

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
- https://github.com/EarthDigitalTwin/FireAlarm-notebooks/blob/main/9.%20OCO3.ipynb
- https://github.com/robrnelson/OCO3_Tools
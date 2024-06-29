# NSQIP-Data-visualization-tool
Biostatistics tool to visualize NSQIP database

![alt text](https://github.com/qcethe/NSQIP-Data-visualization-tool/blob/main/Example%20Image.png)



Instructions to work with tool:

Windows

1. Download latest python version here: https://www.python.org/downloads/

2. Install imports by launching Command Prompt in admin mode and using the following lines (install one at a time):
	pip install pandas
	pip install plotly
	pip install streamlit

3. Navigate to NDVT.py file location in Compand Prompt as such:
	cd  C:\Users\***FileLocation***\

4. Run the following script in Command Prompt: 
	streamlit run NDVT.py --server.maxMessageSize=2000 --server.maxUploadSize=2000

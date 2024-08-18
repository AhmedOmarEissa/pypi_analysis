import pandas as pd 
from pypi_downloads import file_loader
import os
from datetime import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)

def load_new_packages(max_date):
	file = f'../data/processed/new_packages_{max_date}.csv'

	if os.path.exists(file):
		return pd.read_csv(file,index_col=['project'])
	else:
		directory =  '../data/external/monthly_data'
		directory_files = os.listdir(directory)

		print(directory_files)

		monthly_df_list = [os.path.join(directory,file)for file in directory_files if file.endswith(".csv")]
		
		monthly_df = file_loader.FileLoader(monthly_df_list).load()

		monthly_df = monthly_df[monthly_df.run_date <= max_date]

		monthly_df_pivot = monthly_df.pivot(index='project', columns='run_date', values='installs').fillna(0)
		monthly_df_pivot.columns = [column.strftime('%Y%m%d') for column in monthly_df_pivot.columns]
		monthly_df_pivot['historical'] = monthly_df_pivot.drop(columns = max_date).sum(axis=1)
		monthly_df_pivot['total'] = monthly_df_pivot.sum(axis=1)
		monthly_df_pivot['change'] = monthly_df_pivot[max_date] - monthly_df_pivot['historical']
		monthly_df_pivot['change_percent'] = monthly_df_pivot['change']/monthly_df_pivot['historical']
		monthly_df_pivot['installs'] = monthly_df_pivot[max_date]
		monthly_df_pivot['month'] = max_date


		new_packages = monthly_df_pivot[monthly_df_pivot.historical == 0].sort_values(by='total',ascending=False)
		new_packages = new_packages[['month','installs','total','change','change_percent','historical']]
		new_packages.to_csv(file)
		return new_packages
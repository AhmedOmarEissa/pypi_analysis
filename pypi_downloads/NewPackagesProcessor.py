import os
import re
import requests
import pandas as pd
from pypi_downloads import new_packages
from datetime import datetime

class NewPackagesProcessor:
    def __init__(self, directory, file_date):
        self.directory = directory
        self.file_date = file_date
        self.df = None

    def load_new_packages(self):
        # List and filter files based on the date pattern
        files = [re.search(r'\d{8}', file).group() for file in os.listdir(self.directory) if file.endswith('.csv')]
        if self.file_date not in files:
            raise ValueError(f"No file found with date {self.file_date}")
        
        # Load the CSV file for the given date
        file_path = os.path.join(self.directory, f"bq-results-{self.file_date}.csv")
        # self.df = pd.read_csv(file_path)
        self.df = new_packages.load_new_packages(self.file_date)

        # Format the 'month' column
        self.df['month'] = pd.to_datetime(self.df['month'], format='%Y%m%d').dt.strftime('%Y-%m-%d')

        # Format the 'installs' column
        self.df['installs'] = self.df['installs'].apply(self.format_installs)
        self.df.reset_index( inplace=True,names=['project'])
        # Create the output DataFrame
        output_df = self.df[['project', 'installs']].rename(columns={'installs': 'installs_last_month'})
        return output_df

    @staticmethod
    def format_installs(value):
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value/1_000:.0f}k"
        return str(value)

    def enrich_with_pypi_data(self, df):
        # Initialize new columns for the additional information
        df['description'] = ''
        df['homepage'] = ''
        df['author'] = ''

        # Loop over the DataFrame to fetch and insert data
        for index, row in df.iterrows():
            package_name = row['project']
            try:
                # Fetch the package information from PyPI
                response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
                package_info = response.json()

                # Extract relevant information
                df.at[index, 'description'] = package_info['info']['summary']
                df.at[index, 'homepage'] = package_info['info']['home_page']
                df.at[index, 'author'] = package_info['info']['author']
                # df.at[index, 'license'] = package_info['info']['license']
                ## if homepage is empty 
                if df.at[index, 'homepage'] == '' or df.at[index, 'homepage'] == None:
                    df.at[index, 'links'] = f'[PyPI](https://pypi.org/project/{package_name})'
                else:
                    df.at[index, 'links'] = f'[PyPI](https://pypi.org/project/{package_name}), [Homepage]({df.at[index, "homepage"]})'
            except Exception as e:
                # Handle any errors (e.g., package not found)
                print(f"Error fetching data for {package_name}: {e}")
                df.at[index, 'description'] = 'Error fetching data'

        return df.drop(columns=['homepage'])

    def generate_markdown_report(self, df, template_path, output_path):
        # Convert the DataFrame to a Markdown table


        # Insert the 'rank' column as the first column
        df.insert(0, '', df.index + 1)

        markdown_table = df.to_markdown(index=False)

        # Read the markdown content from the template file
        with open(template_path, "r") as file:
            markdown_content = file.read()

        # Write the final Markdown content to a new file

        date_obj = datetime.strptime(self.file_date, '%Y%m%d')

        # Format the date to "Month Day"
        month = date_obj.strftime('%B %Y')
        formatted_date = date_obj.strftime('%Y-%m-%d')


        with open(output_path, "w") as file:
            file.write(markdown_content.format(month = month,date=formatted_date, markdown_table=markdown_table))
        
        print(f"Markdown report generated: {output_path}")

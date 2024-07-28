import pandas as pd
import warnings
warnings.filterwarnings("ignore")


class FileLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def _load(self):
        return pd.read_csv(self.file_path)
    
    def load(self):
        df = self._load()
        df['run_date'] = pd.to_datetime(df['run_date'])
        df.rename(columns={'f0_':'installs'},inplace=True)

        return df.groupby('project').agg(installs = ('installs','sum'),date = ('run_date','min'))
    

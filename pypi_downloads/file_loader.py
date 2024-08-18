import pandas as pd
import warnings

warnings.filterwarnings("ignore")


class FileLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def _load(self):
        
        ## if path is a list of files
        if isinstance(self.file_path, list):
            return pd.concat([pd.read_csv(file) for file in self.file_path])
        
        return pd.read_csv(self.file_path)
    
    def load(self):

        df = self._load()
        df['run_date'] = pd.to_datetime(df['run_date'])
        df.rename(columns={'f0_':'installs'},inplace=True)
        if isinstance(self.file_path, list):
            return df.groupby(['run_date','project']).agg(installs = ('installs','sum')).reset_index()

        return df.groupby('project').agg(installs = ('installs','sum'),date = ('run_date','min'))
    


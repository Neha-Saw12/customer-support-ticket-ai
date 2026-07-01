import pandas as pd
from typing import Optional
import os
from src.utils.config import settings

class DataLoader:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.load_data()

    def load_data(self):
        """Loads the CSV dataset into a Pandas DataFrame."""
        if not os.path.exists(settings.DATA_PATH):
            raise FileNotFoundError(f"Dataset not found at {settings.DATA_PATH}")
        
        self.df = pd.read_csv(settings.DATA_PATH)
        
        # Data preprocessing
        # Convert created_at to datetime
        if 'created_at' in self.df.columns:
            self.df['created_at'] = pd.to_datetime(self.df['created_at'], errors='coerce')
            
        # Convert categorical columns
        for col in ['category', 'priority', 'status']:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype('category')
                
        # Fill null resolution times with -1 or leave as NaN depending on usage
        
    def get_dataframe(self) -> pd.DataFrame:
        """Returns the loaded DataFrame."""
        if self.df is None:
            self.load_data()
        return self.df.copy()

data_loader = DataLoader()

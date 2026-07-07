#dataset_service.py
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
from typing import List, Dict, Iterator
import logging

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetService:
    """Service for handling dataset files (CSV/Excel) and streaming data"""
    
    def __init__(self):
        self.dataset_path = None
        self.dataset_df = None
        self.current_index = 0
        self.is_streaming = False
        
    def load_dataset(self, file_path: str) -> Dict:
        """
        Load dataset from CSV or Excel file
        Args:
            file_path: Path to the dataset file
        Returns:
            Dictionary with dataset info
        """
        try:
            file_path = os.path.abspath(file_path)
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Dataset file not found: {file_path}")
            
            # Load dataset based on file extension
            if file_path.endswith('.csv'):
                self.dataset_df = pd.read_csv(file_path, low_memory=False)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.dataset_df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            self.dataset_path = file_path
            self.current_index = 0
            
            # Clean the dataset
            self._clean_dataset()
            
            logger.info(f"Dataset loaded: {len(self.dataset_df)} records from {file_path}")
            
            return {
                'success': True,
                'file_path': file_path,
                'total_records': len(self.dataset_df),
                'columns': list(self.dataset_df.columns),
                'sample_record': self.dataset_df.iloc[0].to_dict() if len(self.dataset_df) > 0 else {}
            }
            
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _clean_dataset(self):
        """Clean and preprocess the dataset"""
        try:
            # Replace '-' with 'unknown' in service column if it exists
            if 'service' in self.dataset_df.columns:
                self.dataset_df['service'] = self.dataset_df['service'].replace('-', 'unknown')
            
            # Replace NaN values in categorical columns
            categorical_cols = ['proto', 'service', 'state']
            for col in categorical_cols:
                if col in self.dataset_df.columns:
                    self.dataset_df[col] = self.dataset_df[col].fillna('unknown')
            
            # Replace NaN values in numerical columns with 0
            numerical_cols = self.dataset_df.select_dtypes(include=[np.number]).columns
            self.dataset_df[numerical_cols] = self.dataset_df[numerical_cols].fillna(0)
            
            # Convert attack_cat to label if needed (for binary classification)
            if 'attack_cat' in self.dataset_df.columns and 'label' not in self.dataset_df.columns:
                # Create binary label: 0 for Normal, 1 for any attack
                self.dataset_df['label'] = (self.dataset_df['attack_cat'] != 'Normal').astype(int)
            
            logger.info("Dataset cleaned successfully")
            
        except Exception as e:
            logger.error(f"Error cleaning dataset: {str(e)}")
    
    def get_record(self, index: int = None) -> Dict:
        """
        Get a single record from the dataset
        Args:
            index: Index of the record (if None, returns current record)
        Returns:
            Dictionary with record data
        """
        try:
            if self.dataset_df is None:
                raise ValueError("No dataset loaded")
            
            if index is None:
                index = self.current_index
            
            if index >= len(self.dataset_df):
                return None
            
            record = self.dataset_df.iloc[index].to_dict()
            return record
            
        except Exception as e:
            logger.error(f"Error getting record: {str(e)}")
            return None
    
    def get_next_record(self) -> Dict:
        """
        Get the next record in the dataset
        Returns:
            Dictionary with record data or None if end of dataset
        """
        try:
            if self.dataset_df is None:
                return None
            
            if self.current_index >= len(self.dataset_df):
                return None
            
            record = self.get_record(self.current_index)
            self.current_index += 1
            return record
            
        except Exception as e:
            logger.error(f"Error getting next record: {str(e)}")
            return None
    
    def reset_stream(self):
        """Reset the stream to the beginning"""
        self.current_index = 0
        logger.info("Dataset stream reset")
    
    def get_batch(self, batch_size: int = 10) -> List[Dict]:
        """
        Get a batch of records
        Args:
            batch_size: Number of records to return
        Returns:
            List of record dictionaries
        """
        try:
            if self.dataset_df is None:
                return []
            
            batch = []
            for _ in range(batch_size):
                record = self.get_next_record()
                if record is None:
                    break
                batch.append(record)
            
            return batch
            
        except Exception as e:
            logger.error(f"Error getting batch: {str(e)}")
            return []
    
    def get_dataset_stats(self) -> Dict:
        """
        Get statistics about the loaded dataset
        Returns:
            Dictionary with dataset statistics
        """
        try:
            if self.dataset_df is None:
                return {'error': 'No dataset loaded'}
            
            stats = {
                'total_records': len(self.dataset_df),
                'total_columns': len(self.dataset_df.columns),
                'columns': list(self.dataset_df.columns),
                'current_index': self.current_index,
                'remaining_records': len(self.dataset_df) - self.current_index
            }
            
            # Get threat statistics if label column exists
            if 'label' in self.dataset_df.columns:
                threat_count = self.dataset_df['label'].sum()
                normal_count = len(self.dataset_df) - threat_count
                stats['threats'] = int(threat_count)
                stats['normal'] = int(normal_count)
                stats['threat_percentage'] = round((threat_count / len(self.dataset_df)) * 100, 2)
            
            # Get attack category statistics if available
            if 'attack_cat' in self.dataset_df.columns:
                attack_cats = self.dataset_df['attack_cat'].value_counts().to_dict()
                stats['attack_categories'] = attack_cats
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting dataset stats: {str(e)}")
            return {'error': str(e)}
    
    def stream_records(self, interval: float = 1.0) -> Iterator[Dict]:
        """
        Stream records from the dataset with a delay
        Args:
            interval: Delay between records in seconds
        Yields:
            Record dictionaries
        """
        import time
        
        self.is_streaming = True
        self.reset_stream()
        
        try:
            while self.is_streaming and self.current_index < len(self.dataset_df):
                record = self.get_next_record()
                if record is None:
                    break
                
                yield record
                time.sleep(interval)
                
        except Exception as e:
            logger.error(f"Error streaming records: {str(e)}")
        finally:
            self.is_streaming = False
    
    def get_sample_records(self, n: int = 5) -> List[Dict]:
        """
        Get sample records from the dataset
        Args:
            n: Number of sample records
        Returns:
            List of sample record dictionaries
        """
        try:
            if self.dataset_df is None:
                return []
            
            sample_df = self.dataset_df.sample(min(n, len(self.dataset_df)))
            return sample_df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting sample records: {str(e)}")
            return []

# Global dataset service instance
dataset_service = DatasetService()


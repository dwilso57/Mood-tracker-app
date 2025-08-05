import csv
import pandas as pd
import os
from datetime import date, datetime, timedelta
import streamlit as st

class DataManager:
    def __init__(self, filename="mood_log.csv"):
        self.filename = filename
        self.columns = ['date', 'mood', 'journal']
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.columns)
    
    def save_entry(self, entry_date, mood, journal=""):
        """Save or update a mood entry"""
        try:
            # Load existing data
            df = self.load_data()
            
            # Check if entry for this date already exists
            date_str = entry_date.isoformat() if isinstance(entry_date, date) else entry_date
            
            if not df.empty and date_str in df['date'].values:
                # Update existing entry
                df.loc[df['date'] == date_str, 'mood'] = mood
                df.loc[df['date'] == date_str, 'journal'] = journal
            else:
                # Add new entry
                new_entry = pd.DataFrame({
                    'date': [date_str],
                    'mood': [mood],
                    'journal': [journal]
                })
                df = pd.concat([df, new_entry], ignore_index=True)
            
            # Save back to CSV
            df.to_csv(self.filename, index=False)
            return True
            
        except Exception as e:
            st.error(f"Error saving entry: {str(e)}")
            return False
    
    def load_data(self):
        """Load all mood data from CSV"""
        try:
            if os.path.exists(self.filename):
                df = pd.read_csv(self.filename)
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date']).dt.date
                    df = df.sort_values('date')
                return df
            else:
                return pd.DataFrame([], columns=self.columns)
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return pd.DataFrame([], columns=self.columns)
    
    def get_entry_by_date(self, entry_date):
        """Get entry for a specific date"""
        df = self.load_data()
        if df.empty:
            return None
        
        date_filter = df['date'] == entry_date
        if date_filter.any():
            return df[date_filter].iloc[0].to_dict()
        return None
    
    def get_date_range_data(self, start_date, end_date):
        """Get entries within a date range"""
        df = self.load_data()
        if df.empty:
            return df
        
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        return df[mask]
    
    def get_current_streak(self):
        """Calculate current consecutive logging streak"""
        df = self.load_data()
        if df.empty:
            return 0
        
        # Sort by date descending
        df_sorted = df.sort_values('date', ascending=False)
        
        streak = 0
        current_date = date.today()
        
        for _, entry in df_sorted.iterrows():
            if entry['date'] == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def get_mood_statistics(self):
        """Get basic mood statistics"""
        df = self.load_data()
        if df.empty:
            return {}
        
        stats = {
            'total_entries': len(df),
            'average_mood': df['mood'].mean(),
            'median_mood': df['mood'].median(),
            'mood_distribution': df['mood'].value_counts().to_dict(),
            'best_mood_date': df.loc[df['mood'].idxmax(), 'date'],
            'worst_mood_date': df.loc[df['mood'].idxmin(), 'date'],
            'date_range': {
                'start': df['date'].min(),
                'end': df['date'].max()
            }
        }
        
        return stats
    
    def search_entries(self, query):
        """Search entries by journal content"""
        df = self.load_data()
        if df.empty or not query:
            return df
        
        # Case-insensitive search in journal entries
        mask = df['journal'].str.contains(query, case=False, na=False)
        return df[mask]
    
    def export_to_csv(self):
        """Return CSV data for export"""
        df = self.load_data()
        if not df.empty:
            return df.to_csv(index=False)
        return None

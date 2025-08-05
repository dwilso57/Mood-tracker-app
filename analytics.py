import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class MoodAnalytics:
    def __init__(self, dataframes):
        self.df = dataframes
    
    def get_mood_trends(self):
        """Calculate mood trends over time"""
        if self.df.empty:
            return {}
        
        # Sort by date
        df_sorted = self.df.sort_values('date')
        
        # Calculate moving averages
        df_sorted['mood_7day_avg'] = df_sorted['mood'].rolling(window=7, min_periods=1).mean()
        df_sorted['mood_30day_avg'] = df_sorted['mood'].rolling(window=30, min_periods=1).mean()
        
        # Calculate trend direction
        recent_avg = df_sorted['mood'].tail(7).mean()
        previous_avg = df_sorted['mood'].tail(14).head(7).mean() if len(df_sorted) >= 14 else recent_avg
        
        trend_direction = "stable"
        if recent_avg > previous_avg + 0.2:
            trend_direction = "improving"
        elif recent_avg < previous_avg - 0.2:
            trend_direction = "declining"
        
        return {
            'trend_direction': trend_direction,
            'recent_average': recent_avg,
            'previous_average': previous_avg,
            'data_with_averages': df_sorted
        }
    
    def get_weekly_patterns(self):
        """Analyze mood patterns by day of week"""
        if self.df.empty:
            return {}
        
        df_with_weekday = self.df.copy()
        df_with_weekday['weekday'] = pd.to_datetime(df_with_weekday['date']).dt.day_name()
        
        weekday_stats = df_with_weekday.groupby('weekday')['mood'].agg(['mean', 'count']).round(2)
        
        # Reorder by actual weekday order
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_stats = weekday_stats.reindex([day for day in weekday_order if day in weekday_stats.index])
        
        return {
            'weekday_averages': weekday_stats,
            'best_day': weekday_stats['mean'].idxmax() if not weekday_stats.empty else None,
            'worst_day': weekday_stats['mean'].idxmin() if not weekday_stats.empty else None
        }
    
    def get_monthly_patterns(self):
        """Analyze mood patterns by month"""
        if self.df.empty:
            return {}
        
        df_with_month = self.df.copy()
        df_with_month['month'] = pd.to_datetime(df_with_month['date']).dt.strftime('%B')
        df_with_month['month_num'] = pd.to_datetime(df_with_month['date']).dt.month
        
        monthly_stats = df_with_month.groupby(['month', 'month_num'])['mood'].agg(['mean', 'count']).round(2)
        monthly_stats = monthly_stats.sort_values('month_num')
        
        return {
            'monthly_averages': monthly_stats,
            'best_month': monthly_stats['mean'].idxmax()[0] if not monthly_stats.empty else None,
            'worst_month': monthly_stats['mean'].idxmin()[0] if not monthly_stats.empty else None
        }
    
    def get_mood_correlations(self):
        """Find correlations between mood and other factors"""
        if self.df.empty:
            return {}
        
        df_analysis = self.df.copy()
        df_analysis['date_dt'] = pd.to_datetime(df_analysis['date'])
        df_analysis['day_of_week'] = df_analysis['date_dt'].dt.dayofweek
        df_analysis['day_of_month'] = df_analysis['date_dt'].dt.day
        df_analysis['month'] = df_analysis['date_dt'].dt.month
        df_analysis['journal_length'] = df_analysis['journal'].str.len().fillna(0)
        
        correlations = {
            'day_of_week': df_analysis[['mood', 'day_of_week']].corr().iloc[0, 1],
            'day_of_month': df_analysis[['mood', 'day_of_month']].corr().iloc[0, 1],
            'month': df_analysis[['mood', 'month']].corr().iloc[0, 1],
            'journal_length': df_analysis[['mood', 'journal_length']].corr().iloc[0, 1]
        }
        
        return {k: v for k, v in correlations.items() if not pd.isna(v)}
    
    def get_streak_analysis(self):
        """Analyze logging streaks and patterns"""
        if self.df.empty:
            return {}
        
        df_sorted = self.df.sort_values('date')
        dates = df_sorted['date'].tolist()
        
        # Find all streaks
        streaks = []
        current_streak = 1
        
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current_streak += 1
            else:
                if current_streak > 1:
                    streaks.append(current_streak)
                current_streak = 1
        
        if current_streak > 1:
            streaks.append(current_streak)
        
        return {
            'longest_streak': max(streaks) if streaks else 1,
            'average_streak': np.mean(streaks) if streaks else 1,
            'total_streaks': len(streaks),
            'consistency_score': len(dates) / ((dates[-1] - dates[0]).days + 1) if len(dates) > 1 else 1
        }
    
    def get_mood_volatility(self):
        """Calculate mood volatility/stability metrics"""
        if self.df.empty or len(self.df) < 2:
            return {}
        
        mood_values = self.df.sort_values('date')['mood']
        
        # Calculate various volatility measures
        std_dev = mood_values.std()
        range_val = mood_values.max() - mood_values.min()
        
        # Calculate daily changes
        daily_changes = mood_values.diff().abs().dropna()
        avg_daily_change = daily_changes.mean()
        
        # Stability score (inverse of normalized volatility)
        normalized_volatility = std_dev / 4  # Since mood scale is 1-5
        stability_score = 1 - normalized_volatility
        
        return {
            'standard_deviation': std_dev,
            'mood_range': range_val,
            'average_daily_change': avg_daily_change,
            'stability_score': stability_score,
            'volatility_category': self._categorize_volatility(std_dev)
        }
    
    def _categorize_volatility(self, std_dev):
        """Categorize mood volatility"""
        if std_dev < 0.5:
            return "Very Stable"
        elif std_dev < 1.0:
            return "Stable"
        elif std_dev < 1.5:
            return "Moderate"
        elif std_dev < 2.0:
            return "Variable"
        else:
            return "Highly Variable"

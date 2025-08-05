import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.data_manager import DataManager
from utils.analytics import MoodAnalytics
from utils.visualizations import (
    create_mood_chart, create_mood_distribution, 
    create_weekly_pattern_chart, create_monthly_trend_chart,
    create_mood_heatmap
)

st.set_page_config(
    page_title="Analytics - Mood Tracker",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Mood Analytics")
st.markdown("Discover patterns and insights in your mood data")

# Initialize data manager
@st.cache_resource
def get_data_manager():
    return DataManager()

data_manager = get_data_manager()

# Load data
df = data_manager.load_data()

if df.empty:
    st.info("No mood data available yet. Start logging your mood to see analytics!")
    st.stop()

# Initialize analytics
analytics = MoodAnalytics(df)

# Date range selector
st.sidebar.header("📅 Date Range")
min_date = df['date'].min()
max_date = df['date'].max()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = data_manager.get_date_range_data(start_date, end_date)
else:
    filtered_df = df

# Overview metrics
st.header("📈 Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_mood = filtered_df['mood'].mean()
    st.metric("Average Mood", f"{avg_mood:.1f}/5")

with col2:
    total_entries = len(filtered_df)
    st.metric("Total Entries", total_entries)

with col3:
    best_mood = filtered_df['mood'].max()
    st.metric("Best Mood", f"{best_mood}/5")

with col4:
    mood_range = filtered_df['mood'].max() - filtered_df['mood'].min()
    st.metric("Mood Range", f"{mood_range}")

# Mood trends
st.header("📊 Mood Trends")

tab1, tab2, tab3 = st.tabs(["📈 Time Series", "📊 Distribution", "🗓️ Calendar View"])

with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if len(filtered_df) >= 2:
            # Main trend chart
            trend_chart = create_mood_chart(filtered_df, chart_type="line")
            st.plotly_chart(trend_chart, use_container_width=True)
            
            # Moving averages
            if len(filtered_df) >= 7:
                st.subheader("📊 Moving Averages")
                ma_chart = create_mood_chart(filtered_df, chart_type="line")
                
                # Add moving averages
                df_with_ma = filtered_df.copy().sort_values('date')
                df_with_ma['7_day_ma'] = df_with_ma['mood'].rolling(window=7, min_periods=1).mean()
                if len(filtered_df) >= 30:
                    df_with_ma['30_day_ma'] = df_with_ma['mood'].rolling(window=30, min_periods=1).mean()
                
                ma_chart.add_scatter(
                    x=df_with_ma['date'],
                    y=df_with_ma['7_day_ma'],
                    mode='lines',
                    name='7-day Average',
                    line=dict(color='orange', width=2)
                )
                
                if '30_day_ma' in df_with_ma.columns:
                    ma_chart.add_scatter(
                        x=df_with_ma['date'],
                        y=df_with_ma['30_day_ma'],
                        mode='lines',
                        name='30-day Average',
                        line=dict(color='red', width=2)
                    )
                
                st.plotly_chart(ma_chart, use_container_width=True)
        else:
            st.info("Need at least 2 entries to show trend analysis.")
    
    with col2:
        st.subheader("📊 Trend Analysis")
        
        if len(filtered_df) >= 7:
            trends = analytics.get_mood_trends()
            
            # Trend direction
            direction = trends['trend_direction']
            direction_emoji = {"improving": "📈", "declining": "📉", "stable": "➡️"}
            st.metric(
                "Trend Direction",
                direction.title(),
                delta=f"{direction_emoji.get(direction, '➡️')}"
            )
            
            # Recent vs previous average
            recent_avg = trends['recent_average']
            previous_avg = trends['previous_average']
            st.metric(
                "Recent Average",
                f"{recent_avg:.1f}",
                delta=f"{recent_avg - previous_avg:+.1f}"
            )
        else:
            st.info("Need at least 7 entries for trend analysis.")

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Mood distribution pie chart
        dist_chart = create_mood_distribution(filtered_df)
        st.plotly_chart(dist_chart, use_container_width=True)
    
    with col2:
        # Mood statistics
        st.subheader("📊 Mood Statistics")
        
        mood_stats = {
            "Most Common Mood": filtered_df['mood'].mode().iloc[0],
            "Median Mood": filtered_df['mood'].median(),
            "Standard Deviation": filtered_df['mood'].std(),
            "Best Day": filtered_df.loc[filtered_df['mood'].idxmax(), 'date'],
            "Worst Day": filtered_df.loc[filtered_df['mood'].idxmin(), 'date']
        }
        
        for stat, value in mood_stats.items():
            if isinstance(value, float):
                st.metric(stat, f"{value:.2f}")
            else:
                st.metric(stat, str(value))

with tab3:
    if len(filtered_df) >= 7:
        heatmap = create_mood_heatmap(filtered_df)
        st.plotly_chart(heatmap, use_container_width=True)
    else:
        st.info("Need at least 7 entries for calendar heatmap view.")

# Pattern analysis
st.header("🔍 Pattern Analysis")

tab1, tab2, tab3 = st.tabs(["📅 Weekly Patterns", "📆 Monthly Patterns", "🔗 Correlations"])

with tab1:
    if len(filtered_df) >= 7:
        weekly_patterns = analytics.get_weekly_patterns()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            weekly_chart = create_weekly_pattern_chart(filtered_df)
            st.plotly_chart(weekly_chart, use_container_width=True)
        
        with col2:
            st.subheader("📊 Weekly Insights")
            
            if weekly_patterns.get('best_day'):
                st.metric("Best Day", weekly_patterns['best_day'])
            
            if weekly_patterns.get('worst_day'):
                st.metric("Worst Day", weekly_patterns['worst_day'])
            
            # Show weekday averages
            st.subheader("Average by Day")
            for day, stats in weekly_patterns['weekday_averages'].iterrows():
                st.write(f"**{day}:** {stats['mean']:.1f} ({int(stats['count'])} entries)")
    else:
        st.info("Need at least 7 entries for weekly pattern analysis.")

with tab2:
    if len(filtered_df) >= 30:
        monthly_patterns = analytics.get_monthly_patterns()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            monthly_chart = create_monthly_trend_chart(filtered_df)
            st.plotly_chart(monthly_chart, use_container_width=True)
        
        with col2:
            st.subheader("📊 Monthly Insights")
            
            if monthly_patterns.get('best_month'):
                st.metric("Best Month", monthly_patterns['best_month'])
            
            if monthly_patterns.get('worst_month'):
                st.metric("Worst Month", monthly_patterns['worst_month'])
    else:
        st.info("Need at least 30 entries for monthly pattern analysis.")

with tab3:
    correlations = analytics.get_mood_correlations()
    
    if correlations:
        st.subheader("🔗 Correlation Analysis")
        
        correlation_labels = {
            'day_of_week': 'Day of Week',
            'day_of_month': 'Day of Month',
            'month': 'Month',
            'journal_length': 'Journal Entry Length'
        }
        
        for factor, correlation in correlations.items():
            label = correlation_labels.get(factor, factor)
            
            # Interpret correlation strength
            if abs(correlation) < 0.1:
                strength = "Very Weak"
            elif abs(correlation) < 0.3:
                strength = "Weak"
            elif abs(correlation) < 0.5:
                strength = "Moderate"
            elif abs(correlation) < 0.7:
                strength = "Strong"
            else:
                strength = "Very Strong"
            
            direction = "Positive" if correlation > 0 else "Negative"
            
            st.write(f"**{label}:** {correlation:.3f} ({strength} {direction})")
    else:
        st.info("Not enough data for correlation analysis.")

# Advanced analytics
st.header("🔬 Advanced Analytics")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Volatility Analysis")
    volatility = analytics.get_mood_volatility()
    
    if volatility:
        st.metric("Stability Score", f"{volatility['stability_score']:.2f}")
        st.metric("Volatility Category", volatility['volatility_category'])
        st.metric("Standard Deviation", f"{volatility['standard_deviation']:.2f}")
        st.metric("Average Daily Change", f"{volatility['average_daily_change']:.2f}")
    else:
        st.info("Need more entries for volatility analysis.")

with col2:
    st.subheader("🔥 Streak Analysis")
    streak_analysis = analytics.get_streak_analysis()
    
    if streak_analysis:
        st.metric("Longest Streak", f"{streak_analysis['longest_streak']} days")
        st.metric("Average Streak", f"{streak_analysis['average_streak']:.1f} days")
        st.metric("Consistency Score", f"{streak_analysis['consistency_score']:.1%}")
        st.metric("Total Streaks", streak_analysis['total_streaks'])
    else:
        st.info("Need more entries for streak analysis.")

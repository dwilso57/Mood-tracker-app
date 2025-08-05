import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_mood_chart(df, chart_type="line"):
    """Create mood trend chart"""
    if df.empty:
        return go.Figure()
    
    df_sorted = df.sort_values('date')
    fig = None
    
    if chart_type == "line":
        fig = px.line(
            df_sorted,
            x='date',
            y='mood',
            title='Mood Trend Over Time',
            labels={'mood': 'Mood Rating', 'date': 'Date'},
            markers=True,
            line_shape='spline'
        )
        
        # Add mood level annotations
        fig.add_hline(y=3, line_dash="dash", line_color="gray", 
                     annotation_text="Neutral (3)", annotation_position="right")
        
    elif chart_type == "bar":
        fig = px.bar(
            df_sorted,
            x='date',
            y='mood',
            title='Daily Mood Ratings',
            labels={'mood': 'Mood Rating', 'date': 'Date'},
            color='mood',
            color_continuous_scale='RdYlGn'
        )
    
    if fig is not None:
        # Customize layout
        fig.update_layout(
            yaxis=dict(range=[0.5, 5.5], dtick=1),
            xaxis_title="Date",
            yaxis_title="Mood Rating",
            hovermode='x unified'
        )
        
        # Add mood emojis to y-axis
        fig.update_layout(
            yaxis=dict(
                range=[0.5, 5.5], 
                dtick=1,
                tickmode='array',
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['😢 1', '😕 2', '😐 3', '😊 4', '😄 5']
            )
        )
    
    return fig if fig is not None else go.Figure()

def create_mood_distribution(df):
    """Create mood distribution chart"""
    if df.empty:
        return go.Figure()
    
    mood_counts = df['mood'].value_counts().sort_index()
    mood_emojis = {1: "😢", 2: "😕", 3: "😐", 4: "😊", 5: "😄"}
    
    labels = [f"{mood_emojis.get(mood, '')} {mood}" for mood in mood_counts.index]
    
    fig = px.pie(
        values=mood_counts.values,
        names=labels,
        title='Mood Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def create_weekly_pattern_chart(df):
    """Create weekly mood pattern chart"""
    if df.empty:
        return go.Figure()
    
    df_with_weekday = df.copy()
    df_with_weekday['weekday'] = pd.to_datetime(df_with_weekday['date']).dt.day_name()
    df_with_weekday['weekday_num'] = pd.to_datetime(df_with_weekday['date']).dt.dayofweek
    
    weekday_avg = df_with_weekday.groupby(['weekday', 'weekday_num'])['mood'].mean().reset_index()
    weekday_avg = weekday_avg.sort_values('weekday_num')
    
    fig = px.bar(
        weekday_avg,
        x='weekday',
        y='mood',
        title='Average Mood by Day of Week',
        labels={'mood': 'Average Mood', 'weekday': 'Day of Week'},
        color='mood',
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(yaxis=dict(range=[0, 5.5]))
    
    return fig

def create_monthly_trend_chart(df):
    """Create monthly mood trend chart"""
    if df.empty:
        return go.Figure()
    
    df_monthly = df.copy()
    df_monthly['year_month'] = pd.to_datetime(df_monthly['date']).dt.to_period('M')
    
    monthly_stats = df_monthly.groupby('year_month')['mood'].agg(['mean', 'count']).reset_index()
    monthly_stats['year_month_str'] = monthly_stats['year_month'].astype(str)
    
    # Create subplot with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add mood trend line
    fig.add_trace(
        go.Scatter(
            x=monthly_stats['year_month_str'],
            y=monthly_stats['mean'],
            mode='lines+markers',
            name='Average Mood',
            line=dict(color='blue', width=3)
        ),
        secondary_y=False
    )
    
    # Add entry count bars
    fig.add_trace(
        go.Bar(
            x=monthly_stats['year_month_str'],
            y=monthly_stats['count'],
            name='Entries Count',
            opacity=0.6,
            marker_color='lightgray'
        ),
        secondary_y=True
    )
    
    # Update layout
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Average Mood", secondary_y=False)
    fig.update_yaxes(title_text="Number of Entries", secondary_y=True)
    fig.update_layout(title_text="Monthly Mood Trends")
    
    return fig

def create_mood_heatmap(df):
    """Create calendar heatmap of mood data"""
    if df.empty:
        return go.Figure()
    
    # Prepare data for heatmap
    df_heatmap = df.copy()
    df_heatmap['date_dt'] = pd.to_datetime(df_heatmap['date'])
    df_heatmap['week'] = df_heatmap['date_dt'].dt.isocalendar().week
    df_heatmap['weekday'] = df_heatmap['date_dt'].dt.dayofweek
    df_heatmap['year'] = df_heatmap['date_dt'].dt.year
    
    # Create pivot table for heatmap
    heatmap_data = df_heatmap.pivot_table(
        values='mood',
        index='week',
        columns='weekday',
        aggfunc='mean'
    )
    
    # Create heatmap
    fig = px.imshow(
        heatmap_data.values,
        labels=dict(x="Day of Week", y="Week", color="Mood"),
        x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        y=heatmap_data.index,
        color_continuous_scale='RdYlGn',
        aspect='auto',
        title='Mood Calendar Heatmap'
    )
    
    return fig

def create_streak_chart(df):
    """Create streak visualization"""
    if df.empty:
        return go.Figure()
    
    df_sorted = df.sort_values('date')
    dates = df_sorted['date'].tolist()
    
    # Calculate streaks
    streaks = []
    current_streak = 1
    streak_start = dates[0]
    
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current_streak += 1
        else:
            streaks.append({
                'start': streak_start,
                'end': dates[i-1],
                'length': current_streak
            })
            current_streak = 1
            streak_start = dates[i]
    
    # Add final streak
    streaks.append({
        'start': streak_start,
        'end': dates[-1],
        'length': current_streak
    })
    
    # Create bar chart of streaks
    streak_df = pd.DataFrame(streaks)
    streak_df['streak_label'] = streak_df.apply(
        lambda x: f"{x['start']} to {x['end']}", axis=1
    )
    
    fig = px.bar(
        streak_df,
        x='streak_label',
        y='length',
        title='Logging Streaks',
        labels={'length': 'Streak Length (Days)', 'streak_label': 'Date Range'},
        color='length',
        color_continuous_scale='Viridis'
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

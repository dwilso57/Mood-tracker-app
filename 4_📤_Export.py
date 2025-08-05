import streamlit as st
import pandas as pd
import json
from datetime import datetime
import base64
from io import StringIO, BytesIO
from utils.data_manager import DataManager
from utils.analytics import MoodAnalytics

st.set_page_config(
    page_title="Export - Mood Tracker",
    page_icon="📤",
    layout="wide"
)

st.title("📤 Export Data")
st.markdown("Export your mood data in various formats")

# Initialize data manager
@st.cache_resource
def get_data_manager():
    return DataManager()

data_manager = get_data_manager()

# Load data
df = data_manager.load_data()

if df.empty:
    st.info("No mood data to export. Start logging your mood first!")
    st.stop()

# Export options
st.header("📊 Export Options")

# Date range selector
st.subheader("📅 Select Date Range")
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "Start Date",
        value=df['date'].min(),
        min_value=df['date'].min(),
        max_value=df['date'].max()
    )

with col2:
    end_date = st.date_input(
        "End Date",
        value=df['date'].max(),
        min_value=df['date'].min(),
        max_value=df['date'].max()
    )

# Filter data by date range
filtered_df = data_manager.get_date_range_data(start_date, end_date)

if filtered_df.empty:
    st.warning("No data available for the selected date range.")
    st.stop()

# Display preview
st.subheader("📋 Data Preview")
st.write(f"**Selected Period:** {start_date} to {end_date}")
st.write(f"**Total Entries:** {len(filtered_df)}")

# Show sample of data
st.dataframe(filtered_df.head(10), use_container_width=True)

if len(filtered_df) > 10:
    st.info(f"Showing first 10 entries. {len(filtered_df) - 10} more entries will be included in the export.")

# Export formats
st.header("📁 Export Formats")

tab1, tab2, tab3, tab4 = st.tabs(["📊 CSV", "📋 JSON", "📈 Analytics Report", "📄 Text Summary"])

with tab1:
    st.subheader("📊 CSV Export")
    st.write("Export your data as a CSV file for use in spreadsheet applications.")
    
    # CSV options
    include_headers = st.checkbox("Include headers", value=True)
    date_format = st.selectbox(
        "Date format",
        options=["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y"],
        format_func=lambda x: {
            "%Y-%m-%d": "2023-12-25",
            "%m/%d/%Y": "12/25/2023", 
            "%d/%m/%Y": "25/12/2023",
            "%B %d, %Y": "December 25, 2023"
        }[x]
    )
    
    # Generate CSV
    export_df = filtered_df.copy()
    export_df['date'] = export_df['date'].dt.strftime(date_format)
    
    csv_data = export_df.to_csv(index=False, header=include_headers)
    
    # Show preview
    st.write("**CSV Preview:**")
    st.code(csv_data[:500] + "..." if len(csv_data) > 500 else csv_data)
    
    # Download button
    st.download_button(
        label="💾 Download CSV",
        data=csv_data,
        file_name=f"mood_data_{start_date}_{end_date}.csv",
        mime="text/csv",
        key="csv_download"
    )

with tab2:
    st.subheader("📋 JSON Export")
    st.write("Export your data as a JSON file for programmatic use.")
    
    # JSON format options
    json_format = st.selectbox(
        "JSON structure",
        options=["Records", "Table", "Values"],
        help="Records: array of objects, Table: columns and data separate, Values: array of arrays"
    )
    
    # Convert to JSON
    export_df_json = filtered_df.copy()
    export_df_json['date'] = export_df_json['date'].astype(str)
    
    if json_format == "Records":
        json_data = export_df_json.to_json(orient='records', indent=2)
    elif json_format == "Table":
        json_data = export_df_json.to_json(orient='table', indent=2)
    else:  # Values
        json_data = export_df_json.to_json(orient='values', indent=2)
    
    # Show preview
    st.write("**JSON Preview:**")
    preview_data = json_data[:1000] + "..." if len(json_data) > 1000 else json_data
    st.code(preview_data, language="json")
    
    # Download button
    st.download_button(
        label="💾 Download JSON",
        data=json_data,
        file_name=f"mood_data_{start_date}_{end_date}.json",
        mime="application/json",
        key="json_download"
    )

with tab3:
    st.subheader("📈 Analytics Report")
    st.write("Generate a comprehensive analytics report with insights and statistics.")
    
    # Generate analytics
    analytics = MoodAnalytics(filtered_df)
    
    # Report options
    include_charts = st.checkbox("Include chart descriptions", value=True)
    include_insights = st.checkbox("Include insights and patterns", value=True)
    
    # Generate report
    report_data = {
        "report_info": {
            "generated_on": datetime.now().isoformat(),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_entries": len(filtered_df)
        },
        "basic_statistics": {
            "average_mood": float(filtered_df['mood'].mean()),
            "median_mood": float(filtered_df['mood'].median()),
            "std_deviation": float(filtered_df['mood'].std()),
            "mood_range": int(filtered_df['mood'].max() - filtered_df['mood'].min()),
            "best_mood_date": filtered_df.loc[filtered_df['mood'].idxmax(), 'date'].isoformat(),
            "worst_mood_date": filtered_df.loc[filtered_df['mood'].idxmin(), 'date'].isoformat(),
            "mood_distribution": filtered_df['mood'].value_counts().to_dict()
        }
    }
    
    if include_insights:
        # Add analytics insights
        mood_trends = analytics.get_mood_trends()
        weekly_patterns = analytics.get_weekly_patterns()
        volatility = analytics.get_mood_volatility()
        streak_analysis = analytics.get_streak_analysis()
        
        report_data["insights"] = {
            "trend_analysis": {
                "direction": mood_trends.get('trend_direction', 'unknown'),
                "recent_average": float(mood_trends.get('recent_average', 0)),
                "previous_average": float(mood_trends.get('previous_average', 0))
            },
            "volatility_analysis": {
                "stability_score": float(volatility.get('stability_score', 0)),
                "volatility_category": volatility.get('volatility_category', 'unknown'),
                "average_daily_change": float(volatility.get('average_daily_change', 0))
            },
            "streak_analysis": {
                "longest_streak": streak_analysis.get('longest_streak', 0),
                "average_streak": float(streak_analysis.get('average_streak', 0)),
                "consistency_score": float(streak_analysis.get('consistency_score', 0))
            }
        }
        
        if weekly_patterns.get('weekday_averages') is not None:
            weekday_dict = {}
            for day, stats in weekly_patterns['weekday_averages'].iterrows():
                weekday_dict[day] = {
                    "average_mood": float(stats['mean']),
                    "entry_count": int(stats['count'])
                }
            report_data["insights"]["weekly_patterns"] = weekday_dict
    
    # Add raw data
    raw_data = []
    for _, row in filtered_df.iterrows():
        raw_data.append({
            "date": row['date'].isoformat(),
            "mood": int(row['mood']),
            "journal": row['journal'],
            "journal_word_count": len(row['journal'].split()) if row['journal'] else 0
        })
    
    report_data["entries"] = raw_data
    
    # Convert to JSON
    report_json = json.dumps(report_data, indent=2, default=str)
    
    # Show preview
    st.write("**Report Preview:**")
    preview_lines = report_json.split('\n')[:20]
    st.code('\n'.join(preview_lines) + "\n..." if len(preview_lines) == 20 else report_json, 
            language="json")
    
    # Download button
    st.download_button(
        label="💾 Download Analytics Report",
        data=report_json,
        file_name=f"mood_analytics_report_{start_date}_{end_date}.json",
        mime="application/json",
        key="analytics_download"
    )

with tab4:
    st.subheader("📄 Text Summary")
    st.write("Generate a human-readable summary of your mood data.")
    
    # Summary options
    include_stats = st.checkbox("Include statistics", value=True)
    include_entries = st.checkbox("Include all entries", value=False)
    include_journal_excerpts = st.checkbox("Include journal excerpts", value=True)
    
    # Generate text summary
    summary_lines = []
    
    # Header
    summary_lines.append("MOOD TRACKING SUMMARY")
    summary_lines.append("=" * 50)
    summary_lines.append(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    summary_lines.append(f"Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}")
    summary_lines.append(f"Total entries: {len(filtered_df)}")
    summary_lines.append("")
    
    if include_stats:
        # Statistics section
        summary_lines.append("STATISTICS")
        summary_lines.append("-" * 20)
        summary_lines.append(f"Average mood: {filtered_df['mood'].mean():.1f}/5")
        summary_lines.append(f"Highest mood: {filtered_df['mood'].max()}/5")
        summary_lines.append(f"Lowest mood: {filtered_df['mood'].min()}/5")
        summary_lines.append(f"Most stable period: {filtered_df['mood'].std():.2f} standard deviation")
        summary_lines.append("")
        
        # Mood distribution
        summary_lines.append("MOOD DISTRIBUTION")
        summary_lines.append("-" * 20)
        mood_emojis = {1: "😢", 2: "😕", 3: "😐", 4: "😊", 5: "😄"}
        mood_counts = filtered_df['mood'].value_counts().sort_index()
        
        for mood, count in mood_counts.items():
            percentage = (count / len(filtered_df)) * 100
            emoji = mood_emojis.get(mood, '😐')
            summary_lines.append(f"{emoji} {mood}/5: {count} entries ({percentage:.1f}%)")
        summary_lines.append("")
    
    if include_entries:
        # All entries
        summary_lines.append("ALL ENTRIES")
        summary_lines.append("-" * 20)
        
        for _, entry in filtered_df.sort_values('date').iterrows():
            mood_emoji = {1: "😢", 2: "😕", 3: "😐", 4: "😊", 5: "😄"}.get(entry['mood'], '😐')
            entry_date = entry['date'].strftime('%B %d, %Y')
            summary_lines.append(f"{entry_date} - {mood_emoji} {entry['mood']}/5")
            
            if entry['journal'] and include_journal_excerpts:
                # Truncate long journal entries
                journal_text = entry['journal'][:200] + "..." if len(entry['journal']) > 200 else entry['journal']
                summary_lines.append(f"  Journal: {journal_text}")
            summary_lines.append("")
    else:
        # Just highlights
        best_day = filtered_df.loc[filtered_df['mood'].idxmax()]
        worst_day = filtered_df.loc[filtered_df['mood'].idxmin()]
        
        summary_lines.append("HIGHLIGHTS")
        summary_lines.append("-" * 20)
        summary_lines.append(f"Best day: {best_day['date'].strftime('%B %d, %Y')} ({best_day['mood']}/5)")
        if best_day['journal'] and include_journal_excerpts:
            journal_excerpt = best_day['journal'][:150] + "..." if len(best_day['journal']) > 150 else best_day['journal']
            summary_lines.append(f"  '{journal_excerpt}'")
        
        summary_lines.append(f"Worst day: {worst_day['date'].strftime('%B %d, %Y')} ({worst_day['mood']}/5)")
        if worst_day['journal'] and include_journal_excerpts:
            journal_excerpt = worst_day['journal'][:150] + "..." if len(worst_day['journal']) > 150 else worst_day['journal']
            summary_lines.append(f"  '{journal_excerpt}'")
        summary_lines.append("")
    
    # Join all lines
    summary_text = '\n'.join(summary_lines)
    
    # Show preview
    st.write("**Summary Preview:**")
    preview_lines = summary_text.split('\n')[:30]
    st.text('\n'.join(preview_lines) + "\n..." if len(preview_lines) == 30 else summary_text)
    
    # Download button
    st.download_button(
        label="💾 Download Text Summary",
        data=summary_text,
        file_name=f"mood_summary_{start_date}_{end_date}.txt",
        mime="text/plain",
        key="summary_download"
    )

# Backup and restore
st.header("💾 Backup & Restore")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Create Backup")
    st.write("Create a complete backup of all your mood data.")
    
    if st.button("Create Full Backup"):
        # Create complete backup
        all_data = data_manager.load_data()
        backup_data = {
            "backup_info": {
                "created_on": datetime.now().isoformat(),
                "version": "1.0",
                "total_entries": len(all_data)
            },
            "data": []
        }
        
        for _, row in all_data.iterrows():
            backup_data["data"].append({
                "date": row['date'].isoformat(),
                "mood": int(row['mood']),
                "journal": row['journal']
            })
        
        backup_json = json.dumps(backup_data, indent=2)
        
        st.download_button(
            label="💾 Download Complete Backup",
            data=backup_json,
            file_name=f"mood_tracker_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            key="backup_download"
        )

with col2:
    st.subheader("📥 Restore from Backup")
    st.write("Upload a backup file to restore your data.")
    st.warning("⚠️ This feature is not implemented for safety reasons. Manual data import should be done carefully to avoid data loss.")
    
    uploaded_file = st.file_uploader(
        "Choose backup file",
        type=['json'],
        help="Select a JSON backup file created by this application"
    )
    
    if uploaded_file is not None:
        st.info("Backup restore functionality is disabled for safety. Please contact support if you need to restore data.")

# Export statistics
st.header("📊 Export Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Selected Entries", len(filtered_df))

with col2:
    total_days = (end_date - start_date).days + 1
    coverage = (len(filtered_df) / total_days) * 100
    st.metric("Date Coverage", f"{coverage:.1f}%")

with col3:
    journal_entries = len(filtered_df[filtered_df['journal'].str.len() > 0])
    journal_rate = (journal_entries / len(filtered_df)) * 100
    st.metric("With Journal", f"{journal_rate:.1f}%")

with col4:
    total_words = filtered_df['journal'].str.split().str.len().sum()
    st.metric("Total Words", int(total_words) if pd.notna(total_words) else 0)

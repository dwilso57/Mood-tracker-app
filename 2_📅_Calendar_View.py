import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
from utils.data_manager import DataManager

st.set_page_config(
    page_title="Calendar View - Mood Tracker",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Calendar View")
st.markdown("View your mood entries in a calendar format")

# Initialize data manager
@st.cache_resource
def get_data_manager():
    return DataManager()

data_manager = get_data_manager()

# Load data
df = data_manager.load_data()

# Calendar navigation
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("← Previous Month"):
        if 'current_month' not in st.session_state:
            st.session_state.current_month = datetime.now()
        st.session_state.current_month = st.session_state.current_month.replace(day=1) - timedelta(days=1)
        st.session_state.current_month = st.session_state.current_month.replace(day=1)
        st.rerun()

with col2:
    # Initialize current month if not set
    if 'current_month' not in st.session_state:
        st.session_state.current_month = datetime.now().replace(day=1)
    
    current_month = st.session_state.current_month
    st.markdown(f"<h2 style='text-align: center;'>{current_month.strftime('%B %Y')}</h2>", 
                unsafe_allow_html=True)

with col3:
    if st.button("Next Month →"):
        if 'current_month' not in st.session_state:
            st.session_state.current_month = datetime.now()
        
        # Go to next month
        if st.session_state.current_month.month == 12:
            st.session_state.current_month = st.session_state.current_month.replace(
                year=st.session_state.current_month.year + 1, month=1
            )
        else:
            st.session_state.current_month = st.session_state.current_month.replace(
                month=st.session_state.current_month.month + 1
            )
        st.rerun()

# Quick navigation
st.sidebar.header("📅 Quick Navigation")
today_button = st.sidebar.button("Go to Today")
if today_button:
    st.session_state.current_month = datetime.now().replace(day=1)
    st.rerun()

# Month/Year selector
selected_year = st.sidebar.selectbox(
    "Year",
    range(2020, 2030),
    index=range(2020, 2030).index(current_month.year)
)

selected_month = st.sidebar.selectbox(
    "Month",
    range(1, 13),
    format_func=lambda x: calendar.month_name[x],
    index=current_month.month - 1
)

if st.sidebar.button("Go to Selected Month"):
    st.session_state.current_month = datetime(selected_year, selected_month, 1)
    st.rerun()

# Filter data for current month
month_start = current_month
if current_month.month == 12:
    month_end = current_month.replace(year=current_month.year + 1, month=1) - timedelta(days=1)
else:
    month_end = current_month.replace(month=current_month.month + 1) - timedelta(days=1)

month_data = data_manager.get_date_range_data(month_start.date(), month_end.date())

# Create mood lookup dictionary
mood_lookup = {}
if not month_data.empty:
    for _, row in month_data.iterrows():
        mood_lookup[row['date']] = {
            'mood': row['mood'],
            'journal': row['journal']
        }

# Mood emoji mapping
mood_emojis = {1: "😢", 2: "😕", 3: "😐", 4: "😊", 5: "😄"}
mood_colors = {1: "#ff4444", 2: "#ff8844", 3: "#ffdd44", 4: "#88dd44", 5: "#44dd44"}

# Generate calendar
cal = calendar.monthcalendar(current_month.year, current_month.month)

# Calendar styling
st.markdown("""
<style>
.calendar-day {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    margin: 2px;
    min-height: 80px;
    text-align: center;
    background-color: white;
    position: relative;
}

.calendar-day-header {
    font-weight: bold;
    text-align: center;
    padding: 10px;
    background-color: #f0f0f0;
    border-radius: 8px;
    margin: 2px;
}

.mood-indicator {
    font-size: 24px;
    margin: 5px 0;
}

.day-number {
    font-weight: bold;
    font-size: 14px;
}

.no-mood {
    color: #ccc;
    font-size: 12px;
}

.today {
    border: 2px solid #4CAF50;
    background-color: #f0fff0;
}
</style>
""", unsafe_allow_html=True)

# Display calendar header
header_cols = st.columns(7)
weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
for i, day in enumerate(weekdays):
    with header_cols[i]:
        st.markdown(f'<div class="calendar-day-header">{day}</div>', unsafe_allow_html=True)

# Display calendar days
for week in cal:
    week_cols = st.columns(7)
    
    for i, day in enumerate(week):
        with week_cols[i]:
            if day == 0:
                # Empty day
                st.markdown('<div class="calendar-day" style="visibility: hidden;"></div>', 
                           unsafe_allow_html=True)
            else:
                day_date = date(current_month.year, current_month.month, day)
                is_today = day_date == date.today()
                
                # Check if there's a mood entry for this day
                mood_data = mood_lookup.get(day_date)
                
                # Create day content
                today_class = "today" if is_today else ""
                
                if mood_data:
                    mood_emoji = mood_emojis.get(mood_data['mood'], '😐')
                    mood_color = mood_colors.get(mood_data['mood'], '#ddd')
                    
                    day_content = f"""
                    <div class="calendar-day {today_class}" style="border-color: {mood_color};">
                        <div class="day-number">{day}</div>
                        <div class="mood-indicator">{mood_emoji}</div>
                        <div style="font-size: 12px; color: #666;">{mood_data['mood']}/5</div>
                    </div>
                    """
                else:
                    day_content = f"""
                    <div class="calendar-day {today_class}">
                        <div class="day-number">{day}</div>
                        <div class="no-mood">No entry</div>
                    </div>
                    """
                
                # Make day clickable using button
                if st.button(f"📅 {day}", key=f"day_{day}", help=f"View details for {day_date}"):
                    st.session_state.selected_day = day_date
                
                st.markdown(day_content, unsafe_allow_html=True)

# Display selected day details
if 'selected_day' in st.session_state:
    selected_date = st.session_state.selected_day
    st.header(f"📅 Details for {selected_date.strftime('%B %d, %Y')}")
    
    mood_data = mood_lookup.get(selected_date)
    
    if mood_data:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            mood_emoji = mood_emojis.get(mood_data['mood'], '😐')
            st.markdown(f"<div style='text-align: center; font-size: 48px;'>{mood_emoji}</div>", 
                       unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center; font-size: 24px;'>{mood_data['mood']}/5</div>", 
                       unsafe_allow_html=True)
        
        with col2:
            st.subheader("Journal Entry")
            if mood_data['journal']:
                st.write(mood_data['journal'])
            else:
                st.write("*No journal entry for this day*")
        
        # Edit button
        if st.button("✏️ Edit Entry"):
            st.session_state.edit_mode = True
            st.session_state.edit_date = selected_date
            st.rerun()
    else:
        st.info(f"No mood entry recorded for {selected_date.strftime('%B %d, %Y')}")
        
        if st.button("➕ Add Entry for This Day"):
            st.session_state.add_mode = True
            st.session_state.add_date = selected_date
            st.rerun()

# Edit mode
if st.session_state.get('edit_mode', False):
    edit_date = st.session_state.edit_date
    existing_data = mood_lookup.get(edit_date)
    
    st.header(f"✏️ Edit Entry for {edit_date.strftime('%B %d, %Y')}")
    
    with st.form("edit_mood_form"):
        new_mood = st.select_slider(
            "Update mood rating",
            options=[1, 2, 3, 4, 5],
            value=existing_data['mood'] if existing_data else 3,
            format_func=lambda x: f"{x} {'😢' if x==1 else '😕' if x==2 else '😐' if x==3 else '😊' if x==4 else '😄'}"
        )
        
        new_journal = st.text_area(
            "Update journal entry",
            value=existing_data['journal'] if existing_data else "",
            height=150
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 Save Changes", type="primary"):
                success = data_manager.save_entry(edit_date, new_mood, new_journal)
                if success:
                    st.success("Entry updated successfully!")
                    del st.session_state.edit_mode
                    del st.session_state.edit_date
                    st.rerun()
                else:
                    st.error("Failed to update entry.")
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                del st.session_state.edit_mode
                del st.session_state.edit_date
                st.rerun()

# Add mode
if st.session_state.get('add_mode', False):
    add_date = st.session_state.add_date
    
    st.header(f"➕ Add Entry for {add_date.strftime('%B %d, %Y')}")
    
    with st.form("add_mood_form"):
        new_mood = st.select_slider(
            "Mood rating",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: f"{x} {'😢' if x==1 else '😕' if x==2 else '😐' if x==3 else '😊' if x==4 else '😄'}"
        )
        
        new_journal = st.text_area(
            "Journal entry",
            placeholder="How did you feel on this day?",
            height=150
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 Save Entry", type="primary"):
                success = data_manager.save_entry(add_date, new_mood, new_journal)
                if success:
                    st.success("Entry added successfully!")
                    del st.session_state.add_mode
                    del st.session_state.add_date
                    st.rerun()
                else:
                    st.error("Failed to add entry.")
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                del st.session_state.add_mode
                del st.session_state.add_date
                st.rerun()

# Month summary
if not month_data.empty:
    st.header("📊 Month Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Entries This Month", len(month_data))
    
    with col2:
        avg_mood = month_data['mood'].mean()
        st.metric("Average Mood", f"{avg_mood:.1f}/5")
    
    with col3:
        best_day = month_data.loc[month_data['mood'].idxmax(), 'date']
        st.metric("Best Day", best_day.strftime('%m/%d'))
    
    with col4:
        entries_with_journal = len(month_data[month_data['journal'].str.len() > 0])
        st.metric("Days with Journal", entries_with_journal)
    
    # Mood distribution for the month
    st.subheader("📊 Mood Distribution This Month")
    mood_counts = month_data['mood'].value_counts().sort_index()
    
    mood_cols = st.columns(5)
    for i, mood in enumerate([1, 2, 3, 4, 5]):
        with mood_cols[i]:
            count = mood_counts.get(mood, 0)
            emoji = mood_emojis.get(mood, '😐')
            st.metric(f"{emoji} {mood}", count)
else:
    st.info(f"No mood entries for {current_month.strftime('%B %Y')}. Start logging your mood to see calendar data!")

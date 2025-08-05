import streamlit as st
import pandas as pd
from datetime import date, datetime
import os
from utils.data_manager import DataManager
from utils.visualizations import create_mood_chart, create_mood_distribution

# Page configuration
st.set_page_config(
    page_title="Mood Tracker & Journal",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data manager
@st.cache_resource
def get_data_manager():
    return DataManager()

data_manager = get_data_manager()

# Custom CSS for better styling
st.markdown("""
<style>
    .mood-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        background-color: #f9f9f9;
    }
    .mood-emoji {
        font-size: 2rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("😊 Mood Tracker & Journal")
    st.markdown("Track your daily mood and reflect on your journey")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Today's Entry")
        
        # Check if entry exists for today
        today = date.today()
        existing_entry = data_manager.get_entry_by_date(today)
        
        if existing_entry is not None:
            st.info(f"You've already logged your mood for today ({today})")
            
            # Display existing entry
            mood_emojis = {1: "😢", 2: "😕", 3: "😐", 4: "😊", 5: "😄"}
            st.markdown(f"**Mood Rating:** {existing_entry['mood']}/5 {mood_emojis.get(existing_entry['mood'], '😐')}")
            st.markdown(f"**Journal Entry:**")
            st.text_area("Journal Entry", value=existing_entry['journal'], disabled=True, height=100, label_visibility="collapsed")
            
            if st.button("Update Today's Entry"):
                st.session_state.update_mode = True
                st.rerun()
        
        # Entry form
        if not existing_entry or st.session_state.get('update_mode', False):
            with st.form("mood_form"):
                st.subheader("How are you feeling today?")
                
                # Mood rating with emoji feedback
                mood_rating = st.select_slider(
                    "Rate your mood (1 = Very Bad, 5 = Excellent)",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    format_func=lambda x: f"{x} {'😢' if x==1 else '😕' if x==2 else '😐' if x==3 else '😊' if x==4 else '😄'}"
                )
                
                # Journal entry
                journal_entry = st.text_area(
                    "Write about your day (optional)",
                    placeholder="What happened today? How did you feel? What are you grateful for?",
                    height=150,
                    value=existing_entry['journal'] if existing_entry else ""
                )
                
                # Submit button
                submitted = st.form_submit_button("Save Entry", type="primary")
                
                if submitted:
                    if mood_rating:
                        success = data_manager.save_entry(today, mood_rating, journal_entry)
                        if success:
                            st.success("✅ Mood logged successfully!")
                            if 'update_mode' in st.session_state:
                                del st.session_state.update_mode
                            st.rerun()
                        else:
                            st.error("❌ Failed to save entry. Please try again.")
                    else:
                        st.error("Please select a mood rating.")
    
    with col2:
        st.header("📊 Quick Stats")
        
        # Load recent data for stats
        df = data_manager.load_data()
        
        if not df.empty:
            # Recent mood trend
            recent_entries = df.tail(7)
            avg_mood = recent_entries['mood'].mean()
            
            st.metric(
                "7-Day Average Mood",
                f"{avg_mood:.1f}/5",
                delta=f"{avg_mood - 3:.1f}" if len(recent_entries) > 1 else None
            )
            
            # Streak counter
            streak = data_manager.get_current_streak()
            st.metric("Current Streak", f"{streak} days")
            
            # Total entries
            st.metric("Total Entries", len(df))
            
            # Quick mood chart
            st.subheader("Recent Mood Trend")
            if len(recent_entries) >= 2:
                fig = create_mood_chart(recent_entries, chart_type="line")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Log more entries to see your mood trend!")
        else:
            st.info("Start logging your mood to see statistics here!")
    
    # Recent entries preview
    st.header("📖 Recent Entries")
    if not df.empty:
        recent_df = df.tail(5).sort_values('date', ascending=False)
        
        for _, entry in recent_df.iterrows():
            with st.expander(f"{entry['date']} - Mood: {entry['mood']}/5"):
                mood_emojis = {1: "😢", 2: "😕", 3: "😐", 4: "😊", 5: "😄"}
                mood_rating = int(entry['mood'])
                st.markdown(f"**Mood:** {mood_rating}/5 {mood_emojis.get(mood_rating, '😐')}")
                if entry['journal']:
                    st.markdown(f"**Journal:** {entry['journal']}")
                else:
                    st.markdown("*No journal entry for this day*")
    else:
        st.info("No entries yet. Start by logging your first mood!")

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from utils.data_manager import DataManager

st.set_page_config(
    page_title="History - Mood Tracker",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Mood History")
st.markdown("Browse and search through your mood entries")

# Initialize data manager
@st.cache_resource
def get_data_manager():
    return DataManager()

data_manager = get_data_manager()

# Load data
df = data_manager.load_data()

if df.empty:
    st.info("No mood entries found. Start logging your mood to see history!")
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Date range filter
min_date = df['date'].min()
max_date = df['date'].max()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Mood rating filter
mood_filter = st.sidebar.multiselect(
    "Mood Rating",
    options=[1, 2, 3, 4, 5],
    default=[1, 2, 3, 4, 5],
    format_func=lambda x: f"{x} {'😢' if x==1 else '😕' if x==2 else '😐' if x==3 else '😊' if x==4 else '😄'}"
)

# Search functionality
search_query = st.sidebar.text_input(
    "Search Journal Entries",
    placeholder="Enter keywords to search..."
)

# Sort options
sort_options = {
    "Newest First": ("date", False),
    "Oldest First": ("date", True),
    "Highest Mood": ("mood", False),
    "Lowest Mood": ("mood", True)
}

sort_by = st.sidebar.selectbox(
    "Sort By",
    options=list(sort_options.keys()),
    index=0
)

# Apply filters
filtered_df = df.copy()

# Date range filter
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df['date'] >= start_date) & 
        (filtered_df['date'] <= end_date)
    ]

# Mood filter
filtered_df = filtered_df[filtered_df['mood'].isin(mood_filter)]

# Search filter
if search_query:
    search_mask = filtered_df['journal'].str.contains(
        search_query, case=False, na=False
    )
    filtered_df = filtered_df[search_mask]

# Apply sorting
sort_column, ascending = sort_options[sort_by]
filtered_df = filtered_df.sort_values(sort_column, ascending=ascending)

# Display results
st.header(f"📊 Results ({len(filtered_df)} entries)")

if filtered_df.empty:
    st.warning("No entries match your current filters.")
    st.stop()

# Pagination
entries_per_page = st.sidebar.selectbox(
    "Entries per page",
    options=[10, 20, 50, 100],
    index=1
)

total_pages = (len(filtered_df) - 1) // entries_per_page + 1

if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# Page navigation
col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

with col1:
    if st.button("« First") and st.session_state.current_page > 1:
        st.session_state.current_page = 1
        st.rerun()

with col2:
    if st.button("‹ Previous") and st.session_state.current_page > 1:
        st.session_state.current_page -= 1
        st.rerun()

with col3:
    st.markdown(f"<div style='text-align: center; padding: 8px;'>Page {st.session_state.current_page} of {total_pages}</div>", 
                unsafe_allow_html=True)

with col4:
    if st.button("Next ›") and st.session_state.current_page < total_pages:
        st.session_state.current_page += 1
        st.rerun()

with col5:
    if st.button("Last »") and st.session_state.current_page < total_pages:
        st.session_state.current_page = total_pages
        st.rerun()

# Calculate page bounds
start_idx = (st.session_state.current_page - 1) * entries_per_page
end_idx = min(start_idx + entries_per_page, len(filtered_df))

page_df = filtered_df.iloc[start_idx:end_idx]

# Mood emoji mapping
mood_emojis = {1: "😢", 2: "😕", 3: "😐", 4: "😊", 5: "😄"}
mood_colors = {1: "#ff4444", 2: "#ff8844", 3: "#ffdd44", 4: "#88dd44", 5: "#44dd44"}

# Display entries
for idx, (_, entry) in enumerate(page_df.iterrows()):
    # Create expandable entry
    mood_emoji = mood_emojis.get(entry['mood'], '😐')
    mood_color = mood_colors.get(entry['mood'], '#ddd')
    
    # Entry header
    entry_date = entry['date'].strftime('%A, %B %d, %Y')
    header = f"{mood_emoji} {entry_date} - Mood: {entry['mood']}/5"
    
    with st.expander(header, expanded=False):
        col1, col2 = st.columns([1, 4])
        
        with col1:
            # Mood visualization
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; border-radius: 10px; 
                        background-color: {mood_color}20; border: 2px solid {mood_color};'>
                <div style='font-size: 48px;'>{mood_emoji}</div>
                <div style='font-size: 24px; font-weight: bold;'>{entry['mood']}/5</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Entry metadata
            st.markdown("**Date:** " + entry_date)
            st.markdown(f"**Day:** {entry['date'].strftime('%A')}")
            
            # Quick actions
            if st.button(f"✏️ Edit", key=f"edit_{idx}"):
                st.session_state.edit_entry = entry.to_dict()
                st.session_state.edit_entry['original_date'] = entry['date']
                st.rerun()
        
        with col2:
            st.subheader("📝 Journal Entry")
            if entry['journal']:
                # Highlight search terms if search is active
                journal_text = entry['journal']
                if search_query:
                    # Simple highlighting (case-insensitive)
                    import re
                    pattern = re.compile(re.escape(search_query), re.IGNORECASE)
                    journal_text = pattern.sub(
                        f"**{search_query.upper()}**", 
                        journal_text
                    )
                st.markdown(journal_text)
            else:
                st.markdown("*No journal entry for this day*")
            
            # Word count and stats
            if entry['journal']:
                word_count = len(entry['journal'].split())
                char_count = len(entry['journal'])
                st.caption(f"📊 {word_count} words, {char_count} characters")

# Edit entry modal
if 'edit_entry' in st.session_state:
    edit_data = st.session_state.edit_entry
    
    st.header(f"✏️ Edit Entry for {edit_data['date'].strftime('%B %d, %Y')}")
    
    with st.form("edit_entry_form"):
        updated_mood = st.select_slider(
            "Update mood rating",
            options=[1, 2, 3, 4, 5],
            value=edit_data['mood'],
            format_func=lambda x: f"{x} {'😢' if x==1 else '😕' if x==2 else '😐' if x==3 else '😊' if x==4 else '😄'}"
        )
        
        updated_journal = st.text_area(
            "Update journal entry",
            value=edit_data['journal'],
            height=200
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 Save Changes", type="primary"):
                success = data_manager.save_entry(
                    edit_data['original_date'], 
                    updated_mood, 
                    updated_journal
                )
                if success:
                    st.success("Entry updated successfully!")
                    del st.session_state.edit_entry
                    st.rerun()
                else:
                    st.error("Failed to update entry.")
        
        with col2:
            if st.form_submit_button("❌ Cancel"):
                del st.session_state.edit_entry
                st.rerun()

# Summary statistics for filtered data
st.header("📊 Summary Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_mood = filtered_df['mood'].mean()
    st.metric("Average Mood", f"{avg_mood:.1f}/5")

with col2:
    best_mood = filtered_df['mood'].max()
    best_date = filtered_df.loc[filtered_df['mood'].idxmax(), 'date']
    st.metric("Best Mood", f"{best_mood}/5", delta=f"on {best_date.strftime('%m/%d')}")

with col3:
    worst_mood = filtered_df['mood'].min()
    worst_date = filtered_df.loc[filtered_df['mood'].idxmin(), 'date']
    st.metric("Worst Mood", f"{worst_mood}/5", delta=f"on {worst_date.strftime('%m/%d')}")

with col4:
    entries_with_journal = len(filtered_df[filtered_df['journal'].str.len() > 0])
    journal_percentage = (entries_with_journal / len(filtered_df)) * 100
    st.metric("With Journal", f"{entries_with_journal}", delta=f"{journal_percentage:.0f}%")

# Mood distribution chart
st.subheader("📊 Mood Distribution")

mood_counts = filtered_df['mood'].value_counts().sort_index()
mood_cols = st.columns(5)

for i, mood in enumerate([1, 2, 3, 4, 5]):
    with mood_cols[i]:
        count = mood_counts.get(mood, 0)
        percentage = (count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
        emoji = mood_emojis.get(mood, '😐')
        st.metric(f"{emoji} {mood}", f"{count}", delta=f"{percentage:.1f}%")

# Word cloud or common words (if journal entries exist)
journal_entries = filtered_df[filtered_df['journal'].str.len() > 0]

if not journal_entries.empty:
    st.subheader("📝 Journal Insights")
    
    # Combine all journal entries
    all_journals = ' '.join(journal_entries['journal'].tolist())
    
    # Simple word frequency analysis
    import re
    from collections import Counter
    
    # Extract words (simple approach)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', all_journals.lower())
    
    # Filter out common stop words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'was', 'were', 'is', 'are', 'been', 'be', 'have', 'has', 'had', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'a', 'an'
    }
    
    filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
    
    if filtered_words:
        word_freq = Counter(filtered_words).most_common(10)
        
        st.write("**Most Common Words in Journal Entries:**")
        
        word_cols = st.columns(5)
        for i, (word, count) in enumerate(word_freq[:5]):
            with word_cols[i]:
                st.metric(word.capitalize(), count)
        
        if len(word_freq) > 5:
            word_cols2 = st.columns(5)
            for i, (word, count) in enumerate(word_freq[5:10]):
                with word_cols2[i]:
                    st.metric(word.capitalize(), count)

# Bulk actions
st.header("⚙️ Bulk Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("📤 Export Filtered Data"):
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="💾 Download CSV",
            data=csv_data,
            file_name=f"mood_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col2:
    if len(filtered_df) > 0:
        st.write(f"**Selected:** {len(filtered_df)} entries")
        if st.button("🗑️ Delete Filtered Entries", type="secondary"):
            st.warning("This feature is not implemented for safety reasons.")
            st.info("To delete entries, please edit them individually.")

import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
from groq import Groq
import re
from datetime import datetime
import time
import uuid

# Set page configuration
st.set_page_config(
    page_title="FloatChat AI - ARGO Data Explorer",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ChatGPT-inspired CSS styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #d1d5db;
    }

    .stApp {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        background-attachment: fixed;
        padding: 1rem;
    }

    .main .block-container {
        background: #1f2937;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0 auto;
        max-width: 900px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    /* Title styling */
    .main h1 {
        color: #f3f4f6;
        font-weight: 700;
        font-size: 2.25rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* Subheader styling */
    .main h2, .main h3 {
        color: #e5e7eb;
        font-weight: 600;
        margin: 1rem 0 0.5rem 0;
    }

    /* Text area styling */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid #4b5563 !important;
        background: #374151 !important;
        color: #f3f4f6 !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
    }

    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
    }

    /* Button styling */
    .stButton button {
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .stButton button:hover {
        background: #2563eb !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4) !important;
    }

    /* Example query buttons */
    .stButton button.example-query {
        background: #4b5563 !important;
        color: #d1d5db !important;
        border: 1px solid #6b7280 !important;
        margin-bottom: 0.5rem !important;
    }

    .stButton button.example-query:hover {
        background: #6b7280 !important;
        color: #f3f4f6 !important;
    }

    /* Code block styling */
    .stCode {
        border-radius: 12px !important;
        background: #111827 !important;
        border: 1px solid #374151 !important;
        padding: 1rem !important;
        color: #e5e7eb !important;
    }

    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        background: #1f2937 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: #374151;
        padding: 0.5rem;
        border-radius: 12px;
        display: flex;
        gap: 0.5rem;
        justify-content: center;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        color: #9ca3af;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #4b5563;
        color: #f3f4f6;
    }

    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        color: white !important;
    }

    /* Metrics styling */
    .css-1xarl3l {
        background: #1f2937;
        border: 1px solid #4b5563;
        border-radius: 12px;
        padding: 0.75rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        color: #f3f4f6;
    }

    /* Expander styling */
    .streamlit-expander {
        border-radius: 12px !important;
        border: 1px solid #4b5563 !important;
        background: #1f2937 !important;
    }

    .streamlit-expander summary {
        background: #374151 !important;
        border-radius: 12px 12px 0 0 !important;
        color: #e5e7eb !important;
        font-weight: 600 !important;
        padding: 0.75rem !important;
    }

    /* Alert styling */
    .stAlert {
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }

    .stSuccess { background: #15803d !important; color: white !important; }
    .stError { background: #b91c1c !important; color: white !important; }
    .stInfo { background: #1e40af !important; color: white !important; }
    .stWarning { background: #c2410c !important; color: white !important; }

    /* Download button */
    .stDownloadButton button {
        background: #15803d !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
    }

    .stDownloadButton button:hover {
        background: #166534 !important;
        box-shadow: 0 2px 8px rgba(22, 101, 52, 0.4) !important;
    }

    /* Map styling */
    .folium-map {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        margin: 0 auto;
        max-width: 100%;
    }

    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #3b82f6 !important;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        .stTextArea textarea {
            font-size: 0.9rem !important;
        }
    }

    /* Animation for content */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .main .block-container > * {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Initialize the Groq client
client = Groq(api_key="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")

# Database connection function
def get_db_connection():
    try:
        conn = psycopg2.connect(
            "postgresql://neondb_owner:npg_qV9a3dQRAeBm@ep-still-field-a17hi4xm-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Enhanced system prompt for the LLM
system_prompt = """
You are FloatChat, an AI for querying an ARGO ocean database.
Database Schema for table 'argo_floats':
- platform_number (TEXT): The unique ID of the float (e.g., '2902743').
- cycle_number (INTEGER): The profile number from the float.
- measurement_time (TIMESTAMP): UTC time of the observation. Use for all time filters.
- latitude (FLOAT), longitude (FLOAT): Use for all location filters.
- pressure (FLOAT): Depth in decibars (~meters). Lower values are shallower.
- temperature (FLOAT): in °C.
- salinity (FLOAT): Practical Salinity Units (PSU).
- region (TEXT): Pre-set region like 'Indian Ocean'.

CRITICAL RULES:
1. Your ONLY output must be a valid PostgreSQL SELECT query between <sql> tags.
2. You MUST include a `LIMIT 100` clause unless the user specifically asks for "all" data.
3. For spatial queries:
   - "Near [place]" -> Use approximate coordinates with 5-degree bounding box
   - "Highest/Lowest" -> Use `ORDER BY column_name DESC/ASC LIMIT 1`
4. For temporal queries:
   - "Last week" -> `WHERE measurement_time >= CURRENT_DATE - INTERVAL '7 days'`
   - "In March 2023" -> `WHERE measurement_time BETWEEN '2023-03-01' AND '2023-03-31'`
5. NEVER use DELETE, UPDATE, INSERT, or any non-SELECT operations.
6. If the query is ambiguous or cannot be translated, return `SELECT NULL WHERE FALSE;`.
7. Always include relevant columns: platform_number, measurement_time, latitude, longitude, plus requested metrics.

COMMON PLACE COORDINATES:
- Equator: latitude BETWEEN -5 AND 5
- Chennai: latitude BETWEEN 12.5 AND 13.5, longitude BETWEEN 80.0 AND 80.5
- Indian Ocean: latitude BETWEEN -60 AND 30, longitude BETWEEN 20 AND 120

Example Conversions:
User: "Show 10 floats with highest salinity"
SQL: <sql>SELECT platform_number, measurement_time, latitude, longitude, salinity FROM argo_floats ORDER BY salinity DESC LIMIT 10;</sql>

User: "Temperature near equator last month"
SQL: <sql>SELECT platform_number, measurement_time, latitude, longitude, temperature FROM argo_floats WHERE latitude BETWEEN -5 AND 5 AND measurement_time >= CURRENT_DATE - INTERVAL '1 month' LIMIT 100;</sql>

Now, generate the SQL query for the following request:
"""

# SQL Validation Function
def validate_sql_query(sql_query):
    forbidden_patterns = [
        r'\b(DELETE|DROP|UPDATE|INSERT|ALTER|TRUNCATE|CREATE|EXEC|SHUTDOWN)\b',
        r';.*;',
        r'--',
        r'/\*',
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, sql_query, re.IGNORECASE):
            return False
    if not re.match(r'^\s*SELECT', sql_query, re.IGNORECASE):
        return False
    return True

# Enhanced SQL extraction with fallbacks
def extract_sql(response):
    patterns = [
        r'<sql>(.*?)</sql>',
        r'```sql\n(.*?)\n```',
        r'```\n(.*?)\n```',
        r'SELECT.*?;(?=\s*$)'
    ]
    for pattern in patterns:
        sql_match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if sql_match:
            sql_query = sql_match.group(1).strip()
            sql_query = re.sub(r'^--.*?$', '', sql_query, flags=re.MULTILINE)
            sql_query = re.sub(r'\s+', ' ', sql_query).strip()
            return sql_query
    return None

# Enhanced SQL execution with better error handling
def execute_sql_query(sql_query):
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SET statement_timeout = 10000")
            cursor.execute(sql_query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
        conn.close()
        return df
    except psycopg2.errors.SyntaxError as e:
        st.error(f"SQL syntax error: {e}")
        return None
    except psycopg2.errors.UndefinedColumn as e:
        st.error(f"Column doesn't exist: {e}")
        return None
    except psycopg2.errors.UndefinedTable as e:
        st.error(f"Table doesn't exist: {e}")
        return None
    except Exception as e:
        st.error(f"Database error: {e}")
        return None

# Function to create a map visualization
def create_map(df):
    if df is None or df.empty or 'latitude' not in df.columns or 'longitude' not in df.columns:
        return None
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=3)
    for _, row in df.iterrows():
        popup_content = f"""
        <b>Float:</b> {row.get('platform_number', 'N/A')}<br>
        <b>Time:</b> {row.get('measurement_time', 'N/A')}<br>
        <b>Temp:</b> {row.get('temperature', 'N/A')}°C<br>
        <b>Salinity:</b> {row.get('salinity', 'N/A')} PSU<br>
        <b>Pressure:</b> {row.get('pressure', 'N/A')} dbar
        """
        color = 'blue'
        if 'temperature' in df.columns:
            temp = row.get('temperature', 20)
            if temp < 10:
                color = 'blue'
            elif temp < 20:
                color = 'green'
            elif temp < 25:
                color = 'orange'
            else:
                color = 'red'
        folium.Marker(
            [row['latitude'], row['longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"Float: {row.get('platform_number', 'N/A')}",
            icon=folium.Icon(color=color, icon='tint', prefix='fa')
        ).add_to(m)
    return m

# Function to generate profile plot
def create_profile_plot(df):
    if df is None or df.empty or 'pressure' not in df.columns:
        return None
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor('#1f2937')
    ax1.set_facecolor('#374151')
    if 'temperature' in df.columns:
        ax1.set_xlabel('Temperature (°C)', color='#3b82f6')
        ax1.plot(df['temperature'], df['pressure'], color='#3b82f6', marker='o', linestyle='-', 
                label='Temperature', linewidth=1.5, markersize=5)
        ax1.tick_params(axis='x', labelcolor='#3b82f6')
        ax1.invert_yaxis()
    if 'salinity' in df.columns:
        ax2 = ax1.twiny()
        ax2.set_xlabel('Salinity (PSU)', color='#10b981')
        ax2.plot(df['salinity'], df['pressure'], color='#10b981', marker='s', linestyle='--', 
                label='Salinity', linewidth=1.5, markersize=5)
        ax2.tick_params(axis='x', labelcolor='#10b981')
    ax1.set_ylabel('Pressure (dbar)', color='#d1d5db')
    ax1.grid(True, alpha=0.3, color='#6b7280')
    plt.title('Vertical Profile', color='#f3f4f6', fontsize=14, pad=15)
    lines1, labels1 = ax1.get_legend_handles_labels()
    if 'salinity' in df.columns:
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', facecolor='#374151', edgecolor='#6b7280')
    else:
        ax1.legend(loc='upper right', facecolor='#374151', edgecolor='#6b7280')
    plt.tight_layout()
    return fig

# Function to generate time series plot
def create_time_series(df):
    if df is None or df.empty or 'measurement_time' not in df.columns:
        return None
    if df['measurement_time'].dtype == 'object':
        df['measurement_time'] = pd.to_datetime(df['measurement_time'])
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('#1f2937')
    ax1.set_facecolor('#374151')
    if 'temperature' in df.columns:
        ax1.set_xlabel('Time', color='#d1d5db')
        ax1.set_ylabel('Temperature (°C)', color='#3b82f6')
        ax1.plot(df['measurement_time'], df['temperature'], color='#3b82f6', marker='o', 
                linestyle='-', label='Temperature', linewidth=1.5, markersize=4)
        ax1.tick_params(axis='y', labelcolor='#3b82f6')
    if 'salinity' in df.columns:
        ax2 = ax1.twinx()
        ax2.set_ylabel('Salinity (PSU)', color='#10b981')
        ax2.plot(df['measurement_time'], df['salinity'], color='#10b981', marker='s', 
                linestyle='--', label='Salinity', linewidth=1.5, markersize=4)
        ax2.tick_params(axis='y', labelcolor='#10b981')
    plt.title('Time Series', color='#f3f4f6', fontsize=14, pad=15)
    ax1.grid(True, alpha=0.3, color='#6b7280')
    plt.xticks(rotation=45, color='#d1d5db')
    ax1.tick_params(axis='x', colors='#d1d5db')
    lines1, labels1 = ax1.get_legend_handles_labels()
    if 'salinity' in df.columns:
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', facecolor='#374151', edgecolor='#6b7280')
    else:
        ax1.legend(loc='upper left', facecolor='#374151', edgecolor='#6b7280')
    plt.tight_layout()
    return fig

# Query Tips Function
def show_query_tips():
    tips = [
        "**Be specific**: 'temperature near Chennai in 2023'",
        "**Use metrics**: 'salinity', 'temperature', 'pressure'",
        "**Add timeframes**: 'last month', 'in 2023', 'between Jan and Mar'",
        "**Specify locations**: 'near equator', 'Indian Ocean', 'latitude between...'",
        "**Ask for extremes**: 'highest temperature', 'lowest salinity'"
    ]
    for tip in tips:
        st.markdown(f"• {tip}")

# Main function to process user queries
def process_user_query(user_query):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    try:
        with st.spinner("✨ Generating SQL query..."):
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                temperature=0.1,
                max_tokens=1024
            )
        llm_response = completion.choices[0].message.content
        sql_query = extract_sql(llm_response)
        if not sql_query:
            st.error("I couldn't generate a valid SQL query for your request. Please try rephrasing.")
            return None, None, None
        if not validate_sql_query(sql_query):
            st.error("Generated query contains potentially unsafe operations. Please try a different query.")
            return None, None, None
        st.code(sql_query, language="sql")
        with st.spinner("🔍 Executing query..."):
            df = execute_sql_query(sql_query)
        if df is None or df.empty:
            st.warning("No data found for your query. Please try different parameters.")
            return None, None, None
        response_match = re.search(r'<response>(.*?)</response>', llm_response, re.DOTALL)
        natural_response = response_match.group(1).strip() if response_match else "Here are the results of your query:"
        return natural_response, df, sql_query
    except Exception as e:
        st.error(f"Error processing your request: {str(e)}")
        return None, None, None

# Main app
def main():
    st.title("FloatChat AI - ARGO Data Explorer")
    
    # Initialize session state for query input
    if 'query_text' not in st.session_state:
        st.session_state.query_text = ""
    if 'should_populate' not in st.session_state:
        st.session_state.should_populate = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'sql' not in st.session_state:
        st.session_state.sql = None
    
    # Query input and button
    user_query = st.text_area(
        "Ask about ARGO data",
        height=100,
        placeholder="e.g., Show me temperature profiles for floats near the equator in the last month",
        value=st.session_state.query_text,
        key="query_input"
    )
    
    # Update session state when user types
    if user_query != st.session_state.query_text:
        st.session_state.query_text = user_query
    
    process_btn = st.button("Query Data", type="primary")
    
    # Process query if button is clicked
    if process_btn and user_query:
        if len(user_query.strip()) < 5:
            st.error("Please enter a more specific query (at least 5 characters)")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            status_text.text("🔄 Connecting to LLM...")
            progress_bar.progress(25)
            natural_response, df, sql_query = process_user_query(user_query)
            progress_bar.progress(75)
            status_text.text("📊 Preparing results...")
            if df is not None:
                st.session_state.results = natural_response
                st.session_state.df = df
                st.session_state.sql = sql_query
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
    
    # Display results if available
    if st.session_state.df is not None:
        st.markdown("### Results")
        st.success(st.session_state.results)
        st.dataframe(st.session_state.df, use_container_width=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Map", "📈 Profile", "⏰ Time Series", "📋 Raw Data"])
        
        with tab1:
            st.subheader("🌍 Float Locations")
            map_obj = create_map(st.session_state.df)
            if map_obj:
                st.markdown('<div class="folium-map">', unsafe_allow_html=True)
                folium_static(map_obj, width=700, height=450)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("📍 No location data available for mapping.")
        
        with tab2:
            st.subheader("🌊 Vertical Profile")
            profile_fig = create_profile_plot(st.session_state.df)
            if profile_fig:
                st.pyplot(profile_fig)
            else:
                st.info("📏 No pressure data available for profile plot.")
        
        with tab3:
            st.subheader("📊 Time Series")
            time_fig = create_time_series(st.session_state.df)
            if time_fig:
                st.pyplot(time_fig)
            else:
                st.info("⏰ No time data available for time series plot.")
        
        with tab4:
            st.subheader("📋 Raw Data")
            st.dataframe(st.session_state.df, use_container_width=True)
            st.download_button(
                label="📥 Download Data as CSV",
                data=st.session_state.df.to_csv(index=False),
                file_name="argo_data.csv",
                mime="text/csv",
            )
    
    # Example queries and tips in expanders
    with st.expander("Example Queries"):
        examples = [
            "Show me a map of all float measurements with salinity above 36 PSU",
            "Show me one float which is farthest from chennai",
            "show me float having highest temperature among all other floats"
        ]
        for idx, example in enumerate(examples):
            # Use a unique key for each button
            if st.button(example, key=f"example_{idx}", help="Click to populate this query", type="secondary"):
                # Update the query text in session state and clear previous results
                st.session_state.query_text = example
                st.session_state.results = None
                st.session_state.df = None
                st.session_state.sql = None
                # Force a rerun to update the text area
                st.rerun()
    
    with st.expander("Query Tips"):
        show_query_tips()
    
    # Database schema
    with st.expander("Database Schema"):
        conn = get_db_connection()
        if conn:
            try:
                table_info = pd.read_sql("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'argo_floats'
                    ORDER BY ordinal_position;
                """, conn)
                st.write("**Table Schema:**")
                st.dataframe(table_info)
                row_count = pd.read_sql("SELECT COUNT(*) as count FROM argo_floats;", conn)
                min_date = pd.read_sql("SELECT MIN(measurement_time) as min_date FROM argo_floats;", conn)
                max_date = pd.read_sql("SELECT MAX(measurement_time) as max_date FROM argo_floats;", conn)
                st.write("**Database Statistics:**")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Records", f"{row_count['count'].iloc[0]:,}")
                col2.metric("Earliest Measurement", min_date['min_date'].iloc[0].strftime('%Y-%m-%d'))
                col3.metric("Latest Measurement", max_date['max_date'].iloc[0].strftime('%Y-%m-%d'))
                conn.close()
            except Exception as e:
                st.error(f"Error retrieving database info: {e}")

if __name__ == "__main__":
    main()

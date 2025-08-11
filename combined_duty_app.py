import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# Title Row with Clear All Button
col1, col2 = st.columns([4, 1])
with col1:
    st.title("Duty & Rest Calculator")
with col2:
    if st.button("Clear All", type="primary"):
        st.session_state.clear()

st.divider()

# Helper Functions
def format_hours(hours_float):
    hrs = int(hours_float)
    mins = int(round((hours_float - hrs) * 60))
    return f"{hrs:02d}:{mins:02d}"

def calculate_end_time(start_time, duty_length):
    return (datetime.combine(datetime.today(), start_time) + timedelta(hours=duty_length)).time()

# ------------------
# CALCULATOR 1: Single Duty Day
# ------------------
st.header("Single Duty Day Calculator")
dep_time = st.time_input("First Flight Departure Time", key="single_dep")
arr_time = st.time_input("Last Flight Arrival Time", key="single_arr")

if dep_time and arr_time:
    duty_start = (datetime.combine(datetime.today(), dep_time) - timedelta(minutes=60)).time()
    duty_end = (datetime.combine(datetime.today(), arr_time) + timedelta(minutes=15)).time()
    st.write(f"**Duty Start:** {duty_start}")
    st.write(f"**Duty End:** {duty_end}")

# ------------------
# CALCULATOR 2: Split Duty Day
# ------------------
st.header("Split Duty Day Calculator")
first_dep = st.time_input("First Flight Departure Time", key="split_dep")
last_arr = st.time_input("Last Flight Arrival Time", key="split_arr")

if first_dep and last_arr:
    split_start = (datetime.combine(datetime.today(), first_dep) - timedelta(minutes=60)).time()
    split_end = (datetime.combine(datetime.today(), last_arr) + timedelta(minutes=15)).time()
    st.write(f"**Split Duty Start:** {split_start}")
    st.write(f"**Split Duty End:** {split_end}")

# ------------------
# CALCULATOR 3: Rest Period Calculator
# ------------------
st.header("Rest Period & Callout Calculator")

flight_arrival = st.time_input("Last Flight Arrival Time", key="rest_arr")
manual_end_time = st.time_input("Override Duty End Time (optional)", key="manual_end")

if flight_arrival:
    if manual_end_time:
        duty_end = manual_end_time
    else:
        duty_end = (datetime.combine(datetime.today(), flight_arrival) + timedelta(minutes=15)).time()

    # Determine assumed vs deemed rest
    if 20 <= duty_end.hour or duty_end.hour < 2:
        rest_end = (datetime.combine(datetime.today(), duty_end) + timedelta(hours=10)).time()
    else:
        rest_end = datetime.strptime("06:00", "%H:%M").time()

    callout_time = rest_end
    departure_time = (datetime.combine(datetime.today(), callout_time) + timedelta(hours=2, minutes=30)).time()

    st.write(f"**Duty End:** {duty_end}")
    st.write(f"**Rest Ends:** {rest_end}")
    st.write(f"**Earliest Callout:** {callout_time}")
    st.write(f"**Earliest Departure:** {departure_time}")

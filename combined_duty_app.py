import streamlit as st
from datetime import datetime, timedelta, time

st.set_page_config(layout="wide")

# Helper functions
def parse_time(t_str):
    """Parse HHMM or HH:MM strings to datetime.time, or return None if invalid."""
    t_str = t_str.strip()
    try:
        if ':' in t_str:
            dt = datetime.strptime(t_str, "%H:%M")
        else:
            dt = datetime.strptime(t_str.zfill(4), "%H%M")
        return dt.time()
    except:
        return None

def time_to_datetime(t):
    """Convert datetime.time to datetime.datetime for today."""
    return datetime.combine(datetime.today(), t)

def format_timedelta(td):
    """Format timedelta as HH:MM string."""
    total_minutes = int(td.total_seconds() // 60)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h:02d}:{m:02d}"

# Initialize session state for inputs if not present
def init_session_state():
    defaults = {
        # Tab 1: Duty Calculator
        "duty_dep": "",
        "duty_arr": "",
        # Tab 2: Split Duty Calculator
        "split_first_dep": "",
        "split_first_arrival": "",
        "split_second_dep": "",
        "split_last_arrival": "",
        # Tab 3: Rest Calculator
        "rest_landing": "",
        "rest_duty_end": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# Clear all relevant inputs except other settings
def clear_all_inputs():
    keys_to_clear = [
        "duty_dep", "duty_arr",
        "split_first_dep", "split_first_arrival", "split_second_dep", "split_last_arrival",
        "rest_landing", "rest_duty_end",
    ]
    for key in keys_to_clear:
        st.session_state[key] = ""

# Title and Clear All button at top-right
col1, col2 = st.columns([5,1])
with col1:
    st.title("Duty & Rest Calculators")
with col2:
    if st.button("Clear All"):
        clear_all_inputs()

# Tabs for the three calculators
tab1, tab2, tab3 = st.tabs(["Duty Calculator", "Split Duty Calculator", "Rest Calculator"])

with tab1:
    st.header("Duty Calculator")
    duty_dep_input = st.text_input("First Flight Departure Time (HHMM or HH:MM)", value=st.session_state.duty_dep, key="duty_dep")
    duty_arr_input = st.text_input("Last Flight Arrival Time (HHMM or HH:MM)", value=st.session_state.duty_arr, key="duty_arr")

    dep_time = parse_time(duty_dep_input)
    arr_time = parse_time(duty_arr_input)

    if dep_time and arr_time:
        duty_start_dt = time_to_datetime(dep_time) - timedelta(minutes=60)
        duty_end_dt = time_to_datetime(arr_time) + timedelta(minutes=15)
        duty_length = duty_end_dt - duty_start_dt

        st.write(f"Duty Start (60 min before first departure): {duty_start_dt.time().strftime('%H:%M')}")
        st.write(f"Duty End (15 min after last arrival): {duty_end_dt.time().strftime('%H:%M')}")
        st.write(f"Total Duty Length: {format_timedelta(duty_length)}")

with tab2:
    st.header("Split Duty Calculator")
    split_first_dep_input = st.text_input("First Flight Departure Time (HHMM or HH:MM)", value=st.session_state.split_first_dep, key="split_first_dep")
    split_first_arrival_input = st.text_input("Landing Time Before Split (HHMM or HH:MM)", value=st.session_state.split_first_arrival, key="split_first_arrival")
    split_second_dep_input = st.text_input("Departure Time After Split (HHMM or HH:MM)", value=st.session_state.split_second_dep, key="split_second_dep")
    split_last_arrival_input = st.text_input("Last Flight Arrival Time (HHMM or HH:MM)", value=st.session_state.split_last_arrival, key="split_last_arrival")

    first_dep = parse_time(split_first_dep_input)
    first_arrival = parse_time(split_first_arrival_input)
    second_dep = parse_time(split_second_dep_input)
    last_arrival = parse_time(split_last_arrival_input)

    if None not in (first_dep, first_arrival, second_dep, last_arrival):
        dt_start = time_to_datetime(first_dep) - timedelta(minutes=60)
        dt_land = time_to_datetime(first_arrival)
        dt_dep = time_to_datetime(second_dep)
        dt_end = time_to_datetime(last_arrival) + timedelta(minutes=15)

        # Handle cross-midnight
        if dt_land < dt_start:
            dt_land += timedelta(days=1)
        if dt_dep < dt_land:
            dt_dep += timedelta(days=1)
        if dt_end < dt_dep:
            dt_end += timedelta(days=1)

        ground_rest = (dt_dep - dt_land).total_seconds() / 3600
        allowable_duty = 14
        if ground_rest >= 6:
            allowable_duty += min((ground_rest - 2)/2, 3)
        duty_length = (dt_end - dt_start).total_seconds() / 3600

        st.write(f"Duty Start (60 min before first departure): {dt_start.time().strftime('%H:%M')}")
        st.write(f"Duty End (15 min after last arrival): {dt_end.time().strftime('%H:%M')}")
        st.write(f"Ground Rest Duration: {ground_rest:.2f} hours")
        st.write(f"Allowable Duty Length: {format_timedelta(timedelta(hours=allowable_duty))}")
        st.write(f"Actual Duty Length: {format_timedelta(timedelta(hours=duty_length))}")

        if duty_length > allowable_duty:
            st.markdown(f"<span style='color:red;'>Over allowable duty by {format_timedelta(timedelta(hours=duty_length - allowable_duty))}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:green;'>Within allowable duty</span>", unsafe_allow_html=True)

with tab3:
    st.header("Assumed vs Deemed Rest Calculator")
    landing_input = st.text_input("Crew Landing Time (HHMM or HH:MM)", value=st.session_state.rest_landing, key="rest_landing")
    duty_end_input = st.text_input("Override Duty End Time (optional)", value=st.session_state.rest_duty_end, key="rest_duty_end")

    landing_time = parse_time(landing_input)

    duty_end_time = parse_time(duty_end_input) if duty_end_input.strip() else None

    if landing_time:
        default_duty_end_dt = time_to_datetime(landing_time) + timedelta(minutes=15)
        if duty_end_time:
            duty_end_dt = time_to_datetime(duty_end_time)
        else:
            duty_end_dt = default_duty_end_dt

        # Check deemed rest window (20:00 to 02:00 inclusive)
        duty_end_hour = duty_end_dt.time().hour
        duty_end_min = duty_end_dt.time().minute
        # Condition: duty_end between 20:00 and 23:59 or 00:00 to 02:00 inclusive
        if (duty_end_hour >= 20) or (duty_end_hour < 2) or (duty_end_hour == 2 and duty_end_min == 0):
            rest_end_dt = duty_end_dt + timedelta(hours=10)
            rest_type = "Deemed Rest"
            rest_color = "orange"
        else:
            # Assumed rest ends at 06:00 next day if duty ends before 6:00 else same day 06:00
            assumed_rest_end_dt = datetime.combine(duty_end_dt.date(), time(6,0))
            if duty_end_dt.time() >= time(6,0):
                assumed_rest_end_dt += timedelta(days=1)
            rest_end_dt = assumed_rest_end_dt
            rest_type = "Assumed Rest"
            rest_color = "green"

        callout_dt = rest_end_dt
        departure_dt = callout_dt + timedelta(hours=2, minutes=30)

        st.markdown(f"**Duty End Time:** {duty_end_dt.strftime('%H:%M')}")
        st.markdown(f"<span style='color:{rest_color}; font-weight:bold;'>Rest Type: {rest_type}</span>", unsafe_allow_html=True)
        st.markdown(f"**Rest Ends At:** {rest_end_dt.strftime('%H:%M')}")
        st.markdown(f"**Earliest Callout Time:** {callout_dt.strftime('%H:%M')}")
        st.markdown(f"**Earliest Departure Time:** {departure_dt.strftime('%H:%M')}")


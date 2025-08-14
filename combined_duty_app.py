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

# Initialize session state for inputs & outputs if not present
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
        # Shared outputs
        "duty_start_str": "",
        "duty_end_str": "",
        "ground_rest_str": "",
        "allowable_duty_str": "",
        "actual_duty_str": "",
        "status_message": ""
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# Clear all relevant inputs & outputs
def clear_all_inputs():
    keys_to_clear = [
        # Inputs
        "duty_dep", "duty_arr",
        "split_first_dep", "split_first_arrival", "split_second_dep", "split_last_arrival",
        "rest_landing", "rest_duty_end",
        # Outputs
        "duty_start_str", "duty_end_str", "ground_rest_str",
        "allowable_duty_str", "actual_duty_str", "status_message"
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
    st.markdown("**<span style='color:red;'>MAX DUTY: 14 HOURS</span>**", unsafe_allow_html=True)

    dep_str = st.text_input("First Flight Departure Time (UTC - HHMM or HH:MM)", value="08:00")
    arr_str = st.text_input("Last Flight Arrival Time (UTC - HHMM or HH:MM)", value="17:00")

    dep_time = parse_time(dep_str)
    arr_time = parse_time(arr_str)

    if dep_time and arr_time:
        duty_start = datetime.combine(datetime.today(), dep_time) - timedelta(minutes=60)
        duty_end = datetime.combine(datetime.today(), arr_time) + timedelta(minutes=15)

        duty_length_td = duty_end - duty_start
        duty_length_hours = duty_length_td.total_seconds() / 3600

        # Determine colour coding
        if duty_length_hours < 13:
            color = "green"
        elif 13 <= duty_length_hours < 14:
            color = "yellow"
        else:
            color = "red"

        duty_length_str = f"{int(duty_length_td.seconds // 3600)}:{int((duty_length_td.seconds % 3600) // 60):02d}"

        st.markdown(f"**Duty Start:** {duty_start.strftime('%H:%M')}")
        st.markdown(f"**Duty End:** {duty_end.strftime('%H:%M')}")
        st.markdown(f"<span style='color:{color}; font-weight:bold;'>Duty Length: {duty_length_str}</span>", unsafe_allow_html=True)

        # Earliest Next Departure
        if duty_length_hours < 14:
            earliest_next_dep = duty_end + timedelta(hours=11)
            st.markdown(f"**Earliest Next Departure:** {earliest_next_dep.strftime('%H:%M')}")
        else:
            st.markdown("**Earliest Next Departure:** —")

with tab2:
    st.header("Split Duty Calculator")
    split_first_dep_input = st.text_input("First Flight Departure Time (UTC - HHMM or HH:MM)", value=st.session_state.split_first_dep, key="split_first_dep")
    split_first_arrival_input = st.text_input("Landing Time Before Split (UTC - HHMM or HH:MM)", value=st.session_state.split_first_arrival, key="split_first_arrival")
    split_second_dep_input = st.text_input("Departure Time After Split (UTC - HHMM or HH:MM)", value=st.session_state.split_second_dep, key="split_second_dep")
    split_last_arrival_input = st.text_input("Last Flight Arrival Time (UTC - HHMM or HH:MM)", value=st.session_state.split_last_arrival, key="split_last_arrival")

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

        # Ground rest in timedelta
        ground_rest_td = dt_dep - dt_land
        ground_rest_hours = ground_rest_td.total_seconds() / 3600

        allowable_duty = 14
        if ground_rest_hours >= 6:
            allowable_duty += min((ground_rest_hours - 2) / 2, 3)

        duty_length_td = dt_end - dt_start
        duty_length_hours = duty_length_td.total_seconds() / 3600

        st.write(f"Duty Start (60 min before first departure): {dt_start.time().strftime('%H:%M')}")
        st.write(f"Duty End (15 min after last arrival): {dt_end.time().strftime('%H:%M')}")

        # Show ground rest in HH:MM format
        st.write(f"Ground Rest Duration: {format_timedelta(ground_rest_td)}")

        # Warning if ground rest < 6 hours
        if ground_rest_hours < 6:
            st.markdown("<span style='color:red; font-weight:bold;'>Split Duty Day not applicable as ground rest is less than 6:00 hours!</span>", unsafe_allow_html=True)

        st.write(f"Allowable Duty Length: {format_timedelta(timedelta(hours=allowable_duty))}")

# Colour-coded Actual Duty Length
time_diff_hours = allowable_duty - duty_length_hours

if duty_length_hours > allowable_duty:
    # Over allowable duty
    st.markdown(
        f"<span style='color:red; font-weight:bold;'>Actual Duty Length: {format_timedelta(duty_length_td)} "
        f"(Over allowable duty by {format_timedelta(timedelta(hours=duty_length_hours - allowable_duty))})</span>",
        unsafe_allow_html=True
    )
elif time_diff_hours < 1:
    # Within 1 hour under allowable duty (Yellow)
    st.markdown(
        f"<span style='color:orange; font-weight:bold;'>Actual Duty Length: {format_timedelta(duty_length_td)}</span>",
        unsafe_allow_html=True
    )
else:
    # 1 hour or more under allowable duty (Green)
    st.markdown(
        f"<span style='color:green; font-weight:bold;'>Actual Duty Length: {format_timedelta(duty_length_td)}</span>",
        unsafe_allow_html=True
    )


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















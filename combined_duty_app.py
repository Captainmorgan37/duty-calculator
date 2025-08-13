import streamlit as st
from datetime import datetime, timedelta

# Helper to parse freeform time
def parse_time(time_str):
    try:
        return datetime.strptime(time_str.strip(), "%H:%M").time()
    except:
        return None

# ---------- TAB 1: Single Duty Calculator ----------
def single_duty_calculator():
    st.markdown("**<span style='color:red;'>MAX DUTY: 14 HOURS</span>**", unsafe_allow_html=True)

    dep_str = st.text_input("First Flight Departure Time (Local)", value="08:00")
    arr_str = st.text_input("Last Flight Arrival Time (Local)", value="17:00")

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

# ---------- TAB 2: Split Duty Calculator ----------
def split_duty_calculator():
    dep_str = st.text_input("First Flight Departure Time (Local)", value="08:00", key="split_first_flight_dep_unique")
    arr_str = st.text_input("Last Flight Arrival Time (Local)", value="17:00", key="split_last_flight_arr_unique")
    rest_start_str = st.text_input("Split Rest Start Time (Local)", value="12:00", key="split_rest_start_unique")
    rest_end_str = st.text_input("Split Rest End Time (Local)", value="13:00", key="split_rest_end_unique")

    dep_time = parse_time(dep_str)
    arr_time = parse_time(arr_str)
    rest_start_time = parse_time(rest_start_str)
    rest_end_time = parse_time(rest_end_str)

    if dep_time and arr_time and rest_start_time and rest_end_time:
        first_duty_start = datetime.combine(datetime.today(), dep_time) - timedelta(minutes=60)
        split_rest_start_dt = datetime.combine(datetime.today(), rest_start_time)
        first_duty = split_rest_start_dt - first_duty_start

        split_rest_end_dt = datetime.combine(datetime.today(), rest_end_time)
        last_duty_end = datetime.combine(datetime.today(), arr_time) + timedelta(minutes=15)
        second_duty = last_duty_end - split_rest_end_dt

        total_duty = first_duty + second_duty

        def format_td(td):
            hours = td.seconds // 3600
            minutes = (td.seconds % 3600) // 60
            return f"{hours}:{minutes:02d}"

        st.markdown(f"**First Duty Period:** {format_td(first_duty)}")
        st.markdown(f"**Second Duty Period:** {format_td(second_duty)}")
        st.markdown(f"**Total Duty Time:** {format_td(total_duty)}")

# ---------- TAB 3: Assumed vs Deemed Rest Calculator ----------
def rest_calculator():
    landing_str = st.text_input("Landing Time (Local)", value="18:00")
    custom_end_str = st.text_input("Custom Duty End Time (Optional)", value="")

    landing_time = parse_time(landing_str)
    custom_end_time = parse_time(custom_end_str) if custom_end_str else None

    if landing_time:
        default_duty_end = datetime.combine(datetime.today(), landing_time) + timedelta(minutes=15)
        duty_end_time = datetime.combine(datetime.today(), custom_end_time) if custom_end_time else default_duty_end

        if 20 <= duty_end_time.hour or duty_end_time.hour < 2:
            rest_type = "Deemed Rest"
            rest_end_time = duty_end_time + timedelta(hours=10)
        else:
            rest_type = "Assumed Rest"
            rest_end_time = datetime.combine(datetime.today(), datetime.strptime("06:00", "%H:%M").time())

        callout_time = rest_end_time
        earliest_departure = callout_time + timedelta(hours=2, minutes=30)

        st.markdown(f"**Rest Type:** {rest_type}")
        st.markdown(f"**Rest End Time:** {rest_end_time.strftime('%H:%M')}")
        st.markdown(f"**Earliest Callout:** {callout_time.strftime('%H:%M')}")
        st.markdown(f"**Earliest Departure After Callout:** {earliest_departure.strftime('%H:%M')}")

# ---------- MAIN APP ----------
st.set_page_config(layout="wide")
st.title("Crew Duty & Rest Tools")

tab1, tab2, tab3 = st.tabs(["Single Duty", "Split Duty", "Rest Calculator"])

with tab1:
    single_duty_calculator()

with tab2:
    split_duty_calculator()

with tab3:
    rest_calculator()

import streamlit as st
from datetime import datetime, timedelta

def parse_time(t_str):
    try:
        if ":" in t_str:
            return datetime.strptime(t_str, "%H:%M").time()
        else:
            return datetime.strptime(t_str.zfill(4), "%H%M").time()
    except:
        return None

def time_to_datetime(t):
    return datetime.combine(datetime.today(), t)

def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}:{minutes:02d}"

def calc_duty_length(start, end):
    dt_start = time_to_datetime(start)
    dt_end = time_to_datetime(end)
    if dt_end < dt_start:
        dt_end += timedelta(days=1)
    return dt_end - dt_start

def calc_allowable_end(start, max_hours):
    dt_start = time_to_datetime(start)
    dt_allowable = dt_start + timedelta(hours=max_hours)
    return dt_allowable.time()

def regular_duty_calculator():
    st.header("Regular Duty Calculator")
    max_duty = st.number_input("Max Duty Length (hours)", min_value=1, max_value=24, value=14, key="reg_max_duty")
    start_input = st.text_input("Duty Start Time (HHMM or HH:MM)", value="0800", key="reg_start")
    end_input = st.text_input("Duty End Time (HHMM or HH:MM)", value="2200", key="reg_end")

    start_time = parse_time(start_input)
    end_time = parse_time(end_input)

    if start_time and end_time:
        duty_length = calc_duty_length(start_time, end_time)
        allowable_end = calc_allowable_end(start_time, max_duty)
        overage = duty_length - timedelta(hours=max_duty)

        st.write(f"**Duty Length:** {format_timedelta(duty_length)}")
        st.write(f"**Allowable Duty End Time:** {allowable_end.strftime('%H:%M')}")

        if overage > timedelta(seconds=0):
            st.markdown(f"<span style='color:red;'>Over duty by {format_timedelta(overage)}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:green;'>Within allowable duty</span>", unsafe_allow_html=True)
    else:
        st.warning("Please enter valid start and end times in HHMM or HH:MM format.")

def split_duty_calculator():
    st.header("Split Duty Calculator")
    # Inputs
    start_input = st.text_input("Duty Start Time (HHMM or HH:MM)", value="0700", key="split_start")
    first_land_input = st.text_input("Landing Time Before Split (HHMM or HH:MM)", value="1100", key="split_land")
    second_dep_input = st.text_input("Departure Time After Split (HHMM or HH:MM)", value="1800", key="split_dep")
    final_end_input = st.text_input("Final Duty End Time (HHMM or HH:MM)", value="2300", key="split_end")

    start_time = parse_time(start_input)
    first_land = parse_time(first_land_input)
    second_dep = parse_time(second_dep_input)
    final_end = parse_time(final_end_input)

    if None in [start_time, first_land, second_dep, final_end]:
        st.warning("Please enter valid times in all fields.")
        return

    dt_start = time_to_datetime(start_time)
    dt_land = time_to_datetime(first_land)
    dt_dep = time_to_datetime(second_dep)
    dt_end = time_to_datetime(final_end)

    # Adjust cross-midnight times
    if dt_land < dt_start:
        dt_land += timedelta(days=1)
    if dt_dep < dt_land:
        dt_dep += timedelta(days=1)
    if dt_end < dt_dep:
        dt_end += timedelta(days=1)

    # Calculate ground rest in hours
    ground_rest = (dt_dep - dt_land).total_seconds() / 3600

    # Calculate allowable duty
    base_allowable = 14
    if ground_rest >= 6:
        extension = min((ground_rest - 2) / 2, 3)
        allowable_duty = base_allowable + extension
    else:
        allowable_duty = base_allowable

    # Calculate actual duty
    actual_duty = (dt_end - dt_start).total_seconds() / 3600

    # Display results
    st.write(f"**Ground Rest Duration:** {ground_rest:.2f} hours")
    st.write(f"**Allowable Duty Length:** {allowable_duty:.2f} hours")
    st.write(f"**Actual Duty Length:** {actual_duty:.2f} hours")

    if actual_duty > allowable_duty:
        st.markdown(f"<span style='color:red;'>Over allowable duty by {actual_duty - allowable_duty:.2f} hours</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='color:green;'>Within allowable duty</span>", unsafe_allow_html=True)

tabs = st.tabs(["Regular Duty", "Split Duty"])

with tabs[0]:
    regular_duty_calculator()

with tabs[1]:
    split_duty_calculator()

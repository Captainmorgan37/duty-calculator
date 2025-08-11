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
    
    first_flight_dep_input = st.text_input("First Flight Departure Time (HHMM or HH:MM)", value="0800", key="reg_first_flight_dep")
    last_flight_arr_input = st.text_input("Last Flight Arrival Time (HHMM or HH:MM)", value="2200", key="reg_last_flight_arr")

    first_dep_time = parse_time(first_flight_dep_input)
    last_arr_time = parse_time(last_flight_arr_input)

    if first_dep_time and last_arr_time:
        duty_start_dt = time_to_datetime(first_dep_time) - timedelta(minutes=60)
        duty_start = duty_start_dt.time()
        
        duty_end_dt = time_to_datetime(last_arr_time) + timedelta(minutes=15)
        duty_end = duty_end_dt.time()
        
        duty_length = calc_duty_length(duty_start, duty_end)
        allowable_end = calc_allowable_end(duty_start, max_duty)
        overage = duty_length - timedelta(hours=max_duty)

        st.write(f"**Duty Start Time (calculated):** {duty_start.strftime('%H:%M')}")
        st.write(f"**Duty End Time (calculated):** {duty_end.strftime('%H:%M')}")
        st.write(f"**Duty Length:** {format_timedelta(duty_length)}")
        st.write(f"**Allowable Duty End Time:** {allowable_end.strftime('%H:%M')}")

        if overage > timedelta(seconds=0):
            st.markdown(f"<span style='color:red;'>Over duty by {format_timedelta(overage)}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:green;'>Within allowable duty</span>", unsafe_allow_html=True)
    else:
        st.warning("Please enter valid first departure and last arrival times in HHMM or HH:MM format.")

def split_duty_calculator():
    st.header("Split Duty Calculator")
    
    first_flight_dep_input = st.text_input("First Flight Departure Time (HHMM or HH:MM)", value="0700", key="split_first_flight_dep")
    first_flight_arrival_input = st.text_input("Landing Time Before Split (HHMM or HH:MM)", value="1100", key="split_first_flight_arrival")
    second_flight_dep_input = st.text_input("Departure Time After Split (HHMM or HH:MM)", value="1800", key="split_second_flight_dep")
    last_flight_arr_input = st.text_input("Last Flight Arrival Time (HHMM or HH:MM)", value="2300", key="split_last_flight_arr")

    first_dep_time = parse_time(first_flight_dep_input)
    first_land = parse_time(first_flight_arrival_input)
    second_dep = parse_time(second_flight_dep_input)
    last_arr_time = parse_time(last_flight_arr_input)

    if None in [first_dep_time, first_land, second_dep, last_arr_time]:
        st.warning("Please enter valid times in all fields.")
        return

    duty_start_dt = time_to_datetime(first_dep_time) - timedelta(minutes=60)
    duty_start = duty_start_dt.time()
    
    duty_end_dt = time_to_datetime(last_arr_time) + timedelta(minutes=15)
    duty_end = duty_end_dt.time()

    dt_start = time_to_datetime(duty_start)
    dt_land = time_to_datetime(first_land)
    dt_dep = time_to_datetime(second_dep)
    dt_end = time_to_datetime(duty_end)

    if dt_land < dt_start:
        dt_land += timedelta(days=1)
    if dt_dep < dt_land:
        dt_dep += timedelta(days=1)
    if dt_end < dt_dep:
        dt_end += timedelta(days=1)

    ground_rest = (dt_dep - dt_land).total_seconds() / 3600
    base_allowable = 14
    if ground_rest >= 6:
        extension = min((ground_rest - 2) / 2, 3)
        allowable_duty_hours = base_allowable + extension
    else:
        allowable_duty_hours = base_allowable

    actual_duty_hours = (dt_end - dt_start).total_seconds() / 3600

    # Convert decimal hours to timedelta for formatting
    allowable_duty_td = timedelta(hours=allowable_duty_hours)
    actual_duty_td = timedelta(hours=actual_duty_hours)

    st.write(f"**Duty Start Time (calculated):** {duty_start.strftime('%H:%M')}")
    st.write(f"**Duty End Time (calculated):** {duty_end.strftime('%H:%M')}")
    st.write(f"**Ground Rest Duration:** {ground_rest:.2f} hours")
    st.write(f"**Allowable Duty Length:** {format_timedelta(allowable_duty_td)}")
    st.write(f"**Actual Duty Length:** {format_timedelta(actual_duty_td)}")

    if actual_duty_hours > allowable_duty_hours:
        over_hours = actual_duty_hours - allowable_duty_hours
        over_td = timedelta(hours=over_hours)
        st.markdown(f"<span style='color:red;'>Over allowable duty by {format_timedelta(over_td)}</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='color:green;'>Within allowable duty</span>", unsafe_allow_html=True)


tabs = st.tabs(["Regular Duty", "Split Duty"])

with tabs[0]:
    regular_duty_calculator()

with tabs[1]:
    split_duty_calculator()

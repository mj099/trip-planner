import streamlit as st
from streamlit_calendar import calendar
import pandas as pd
from datetime import datetime
from datetime import timedelta

colordict = {'p':'#b5ffc2','t':'#ffd3d3', 'o':'#b3b1ae'}
countrycolor = ["#e6194B","#3cb44b","#ffe119","#4363d8","#f58231","#911eb4","#42d4f4","#f032e6","#bfef45","#fabed4"]


st.set_page_config(page_title="Calendar", page_icon="📆")
st.markdown(
    "## Travel calendar "
)

st.write("Departure time format: 24hour clock, e.g. 15:30, 23:20")
st.write("Transport duration in hours. e.g. 1.5 = 90 minutes")
st.write("Mode of transport options:")
st.write("- p: plane")
st.write("- t: train")
st.write("- o: other")

trip_start_date = st.date_input("Pick a start date")
todays_date = datetime.today().strftime('%Y-%m-%d')



if 'cal' not in st.session_state:
    st.session_state.cal = 0


f = st.file_uploader("Test", accept_multiple_files=False)
if f != None:
    df_ = pd.read_csv(f)
    df = pd.DataFrame(
        {"City": df_["City"], "Duration (days)": df_["Duration (days)"], "Mode of Transport": df_["Mode of Transport"], "Departure time": df_["Departure time"], "Transport duration": df_["Transport duration"]}
    )

else:
        
    try:
        cities = st.session_state.ordered
    except:
        cities = None

    if cities:
        df = pd.DataFrame(
            {"City": cities, "Duration (days)": [None] * len(cities), "Mode of Transport": [None] * len(cities), "Departure time": ["12:00"] * len(cities), "Transport duration": [None] * len(cities)}
        )

if df != None:
    edited_df = st.data_editor(df)
    current_start_date = trip_start_date

    for i in range(len(edited_df)):
        duration = int(edited_df.at[i, 'Duration (days)'])

        if duration is not None and duration > 0:
            edited_df.at[i, 'From'] = current_start_date
            edited_df.at[i, 'Until'] = current_start_date + timedelta(days=duration)
            current_start_date = edited_df.at[i, 'Until'] #+ timedelta(days=1)
        
        else:
            edited_df.at[i, 'From'] = None
            edited_df.at[i, 'Until'] = None

    st.write(edited_df)

    st.download_button(
        label="Download data",
        data= edited_df.to_csv(index=False),
        file_name="calendar-data.csv",
        mime="application/json"
    )
    #============= CALENDAR EVENTS:
    # Initialize events only once
    if 'events' not in st.session_state:
        st.session_state.events = []

    # Reference to events in session state
    events = st.session_state.events

    # Only append events if they haven't already been added (to prevent duplicates on rerun)
    if len(events) == 0:
        count = 0
        for i in range(1, len(edited_df)):
            pre_end_date = edited_df.at[i-1, 'Until']
            pre_dep_time = edited_df.at[i-1, 'Departure time']
            pre_tran_dur = float(edited_df.at[i-1, 'Transport duration'])/24  # Convert to proportion of a day
            prev_departure_ar = pd.to_datetime(pre_end_date.strftime('%Y-%m-%d') + ' ' + str(pre_dep_time)) + timedelta(days=pre_tran_dur)

            city = edited_df.at[i, 'City']
            start_date = edited_df.at[i, 'From']
            end_date = edited_df.at[i, 'Until']
            transport_mode = edited_df.at[i, 'Mode of Transport']
            departure_time = edited_df.at[i, 'Departure time']
            transport_duration = edited_df.at[i, 'Transport duration']

            departure_datetime = pd.to_datetime(end_date.strftime('%Y-%m-%d') + ' ' + str(departure_time))
            transport_duration = float(transport_duration)/24 

            # City stay event
            if start_date is not None and end_date is not None:
                event = {
                    "id": count,
                    "title": city,                               
                    "color": countrycolor[i % len(countrycolor)],                    
                    "start": prev_departure_ar.strftime('%Y-%m-%d %H:%M'),       
                    "end": departure_datetime.strftime('%Y-%m-%d %H:%M'),
                    "travelBy": transport_mode,
                    "display": "block",
                    "overlap": "true",
                    "User": []  # Store user info here
                }
                events.append(event)
                count += 1

            # Travel event
            if departure_time is not None and transport_duration is not None:
                travel_event = {
                    "id": count,
                    "title": f"Travel ({transport_mode})",
                    "color": colordict.get(transport_mode),                      
                    "start": departure_datetime.strftime('%Y-%m-%d %H:%M'),  
                    "end": (departure_datetime + timedelta(days=transport_duration)).strftime('%Y-%m-%d %H:%M'),
                    "travelBy": transport_mode,
                    "display": "block",
                    "overlap": "true",
                    "User": []
                }
                events.append(travel_event)
                count += 1

    #========== CALENDAR
    mode = st.selectbox(
        "Calendar Mode:",
        (
            "daygrid",
            "timegrid",
            "multimonth",
        ),
    )

    calendar_options = {
        "editable": "true",
        "navLinks": "true",
        "selectable": "true",
    }

    if mode == "daygrid":
        calendar_options = {
            **calendar_options,
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridDay,dayGridWeek,dayGridMonth",
            },
            "initialDate": str(trip_start_date),
            "initialView": "dayGridMonth",
        }
    elif mode == "multimonth":
        calendar_options = {
            **calendar_options,
            "initialView": "multiMonthYear",
        }

    # Use calendar with session events
    state = calendar(
        events=events,
        options=calendar_options,
        custom_css="""
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
        """,
    )

    # Handle calendar state updates
    if state.get("eventsSet") is not None:
        st.session_state["events"] = state["eventsSet"]

    #st.write(state)

    # ========= UPDATE SELECTED EVENT =========
    try:
        current_event_title = state["eventClick"]["event"]["title"]
        current_event_id = int(state["eventClick"]["event"]["id"])  # Ensure integer
        current_event = st.session_state.events["events"][current_event_id]["extendedProps"]

        new_info = st.text_input(f"Enter additional information for {current_event_title}")
        if st.button("Submit new information:"):
            
            if "User" not in current_event or not isinstance(current_event["User"], list):
                current_event["User"] = []
            
            current_event["User"].append(new_info)


            st.session_state.events["events"][current_event_id]

        st.write(state["eventClick"]["event"])

    except:
        st.write("Press a calendar event to add additional information.")
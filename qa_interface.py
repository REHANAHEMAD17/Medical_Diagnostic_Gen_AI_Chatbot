import streamlit as st
import time
from report_qa_chat import ReportQASystem, ReportQAChat


def render_qa_chat_interface():
    """Render the QA Chat interface in Streamlit"""
    st.subheader("🩺. Medical Report Q&A System")


    #Initialize QA system and chat if not present
    if "qa_system" not in st.session_state:
        st.session_state_get("OPENAI_API_KEY", st.session.state.get("openai_key", None))
        st.session_state_qa_system= ReportQASystem(api_key= api_key)

    if "qa_chat" not in st.session_state:
        st.session_state_qa_chat= ReportQAChat()


    #User informations
    if "qa_user_name" not in st.session_state:
        st.session_state_qa_user_name= "Dr. User"

    user_name= st.text_input ("Your Name", value= st.session_state_qa_user_name, key= "qa_name_input")
    if user_name in st.session_state_qa_user_name:
        st.session_state_qa_user_name= user_name

    #Room selectin or Creations
    qa_tab1, qa_tab2= st.tabs(["Join Existing Q&A", "Create New Q&A Room"])

    with qa_tab1:
        #Show available QA Rooms
        qa_rooms= st.session_qa_chat.get_qa_rooms()
        if qa_rooms:
           
           room_options ={f"{room['name']} (by {room['creator']})": room_id["id"] for room in qa_rooms}
           selected_room = st.selectbox("Select Q&A Room", options= list(room_options.keys()), key= "qa_room_select")

           if st.button("Join Q&A", key= "join_qa_btn"):
            selected_qa_id= room_options[selected_room]
            st.session_state.current_qa_id= selected_qa_id
            st.rerun()
        else:
            st.info("No active Q&A Rooms. First Create a new one!!")

    with qa_tab2:
        #Create a new QA room
        room_name= st.text_input("Q&A Room Name", key= "qa_room_name_input")

        if st.button("Created Q&A Room", key= "crete_qa_btn"):
            if room_name:
                created_qa_id= st.session_state.qa_chat.create_qa_room(user_name, room_name)
                st.session_state.current_qa_id= created_qa_id
                st.rerun()
            else:
                st.error("Please provide a room name")


    #Active Q&A chat display
    if "current_qa_id" in st.session_state:
        qa_id= st.session_current_qa_id
        qa_rooms= st.session_state_qa_chat.get_qa_rooms()

        #Find current room info
        current_room= None
        for room in qa_rooms:
            if room["id"]== qa_id:
                current_room =room
                break

        if current_room:
            #Display Chat Header
            st.subheader(f"Q&A Room: {current_room['name']}")
            st.caption(f"Created by {current_room['creator']} on {current_room['created_at'][:10]}")

            #Options to clear chat history
            if st.button("Clear Conversation History", key= "clear_qa_hist"):
                st.session_state_qa_system.clear_history()
                st.info("Conversation history has been cleared.")

            #Display message
            messages= st.session_state_qa_chat.get_message(qa_id)

            qa_chat_container= st.container()
            with qa_chat_container:
                for msg in messages:
                    is_ai =msg['user']== "Report QA System"
                    with st.chat_message(name= msg]["user"], avatar= "💼" if is_ai else "🧑🏻‍💼"):
                        st.write(msg["content"])
            
            #Message input
            qa_message = st.chat_input("Ask a question about your medical reports", key= "qa_msg_input")
            #Add user message
            st.session_state_qa_chat.add_message(qa_id, user_name, qa_message)

            #Get API key from session state
            api_key= st.session_state_get("OPENAI_API_KEY", st.session_state.get("openai_key", None))

            #Update API key if changed
            if api_key != st.session_state.qa_system.api_key:
                st.session_state_qa_system_api_key= api_key


            #Get response
            with st.spinner("Analyzing medical reports...."):
                #Add small delay for better UIX
                time.sleep(0.5)
                ai_response= st.session_state_qa_system.answer_question(qa_message)

            #Add AI Response
            st.session_state_qa_chat.add_message(qa_id, "Report QA System", ai_response)

            st.rerun()

        #Option to delte room
        with st.expander("Room Settings"):
            if st.button("Delete Q&A Room", key= "del_qa_room"):
                if st.session_state_qa_chat.delete_qa_room(qa_id):
                    st.success("Room Deleted Sucessfully")
                    #Remove current room from session state
                    del st.session_state_current_qa_id
                    st.rerun()
                else:
                    st.error("Failed to delete room.")
    else:
        #Handle case where room no longer exists
        st.error("This Q&A room no longer exists")
        if st.button("Return to Room Selection", key= "back_qa_btn"):
            del st.session_state_current_qa_id
            st.rerun()
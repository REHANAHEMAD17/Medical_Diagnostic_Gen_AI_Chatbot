import streamlit as st
import os
import io
import json
import base64
from PIL import Image
from datetime import datetime
from utils_simple import(process_file, analyze_image, generate_heatmap, save_analysis, get_latest_analyses, generate_report, search_pubmed, generate_statistics_report)
from chat_system import render_chat_interface, create_manual_chat_room
from report_qa_chat import ReportQASystem, ReportQAChat
from qa_interface import render_qa_chat_interface

st.set_page_config(page_title= "Medical Image Analysis Platform", page_icon= "🏣",layout= "wide")

if "open_ai_key" not in st.session_state:
    st.session_state_openai_key=""
if "file_data" not in st.session_state:
    st.session_state.file_data= None
if "analysis_results" not in st.session_state:
    st.session_state.analysis_result= None
if "file_name" not in st.session_state:
    st.session_state.file_name= None
if "file_type" not in st.session_state:
    st.session_state.file_type= None
if "OPENAI_API_KEY" not in st.session_state:
    st.session_state.OPENAI_API_KEY=None


st.title("🏣 Advanced Medical Image Analysis")
st.markdown("Upload medical images for AI-Powered analysis and collaborate.")

with st.sidebar:
    st.header("Configuration")

    #API Key Input
    api_key= st.text_input(
        "OpenAI API Key",
        value= st.session_state.openai_key,
        type= "password",
        help= "Enter your OpenAI API key to enable image analysis"
    )

    if api_key:
        st.session_state.openai_key= api_key
        st.session_state.OPENAI_API_KEY= api_key

    #Explainable AI captions
    st.subheader("Analysis Options")
    enable_xai= st.checkbox("Enable Explainable AI", value= True)
    include_references= st.checkbox("Include Medical References", value= True)

    #Recent Analysis
    st.subheader("Recent Analyses")
    recent_analyses= get_latest_analyses(limit=5)
    for analysis in recent_analyses:
        st.caption(f"{analysis.get('filename','Unknown')} - {analysis.get('data', '')[:10]}")

        #Statistics Report
    if st.button("Generate Statistics Report"):
        stats_report= generate_statistics_report
        if stats_report:
            b64_pdf= base64.b64encode(stats_report.read()).decode()
            href= f'<a href="data:application/pdf;base64,{b64_pdf}" download= "statistics_report.pdf">Download Statistics Report</a>'
            st.markdown(href, unsafe_allow_html= True)



tab1,tab2,tab3,tab4= st.tabs(["Image Upload & Analysis", "Collaboration", "Report Q&A", "Reports"])

with tab1:
    #File Uploader
    uploaded_file= st.file_uploder(
        "Upload a medical image(JPEG, PNG, DICOM, NIfTI)",
        type=["jpg","jpeg","png","dcm","nii","nii.gz"]
    )

    if uploaded_file:
        #Process the file
        try:
            file_data= process_file(uploaded_file)

            if file_data:
                st.session_state.file_data= file_data
                st.session_state.file_name= uploaded_file.name
                st.session_state.file_type= file_data["type"]

                #Display the image
                st.image(file_data["data"], caption=f"Uploaded{file_data['type']} image", use_column_width= True)

                #Analysis button
                if st.button("Analyze Image") and st.session_state.openai_key:
                    with st.spinner("Analyzing image..."):
                        #Run image analysis
                        analysis_results= analyze_image(
                            file_data["data"],
                            st.session_state.openai_key,
                            enable_xai= enable_xai
                        )
                        # Store the analysis
                        analysis_results= save_analysis(analysis_results, filename= uploaded_file.name)

                        #Update session state
                        st.session_state.analysis_results= analysis_results
                        st.session_state.findings= analysis_results.get("findings", [])

                        #Display results
                        st.subheader("Analysis Results")
                        st.markdown(analysis_results["analysis"])

                        #Show findings if available
                        if analysis_results.get("findings"):
                            st.subheader("Key Findings")
                            for idx, finding in enumerate(analysis_results["findings"],1):
                                st.markdown(f"{idx}. {finding}")

                        #Show keywords if availble
                        if analysis_results.get("keywords"):
                            st.subheader("keywords")
                            st.markdown(f"*{', '.join(analysis_results['keywords'])}*")

                        #Generate Heatmap if XAI is enable
                        if enable_xai:
                            st.subheader("Explainable AI Visualization")
                            overlay, heatmap= generate_heatmap(file_data['array'])
                            col1, col2= st.columns(2)
                            with col1:
                                st.image(overlay, caption= "Headtmap Overlay", use_column_width= True)
                            with col2:
                                st.image(heatmap, caption= "Raw Heatmap", use_column_width= True)

                        #Show medical reference if enabled
                        if include_references and analysis_results.get("keywords"):
                            st.subheader("Relevant Medical Literature")
                            refernces= search_pubmed(analysis_results["keywords"], max_results=3)
                            for ref in refernces:
                                st.markdown(f"- **{ref['title']}**  \n{ref['journal']}, {ref['year']} (PMID: {ref['id']})")

                        #Generate PDF reports
                        st.subheader("Report Generation")
                        pdf_buffer= generate_report(analysis_results, include_references= include_references)

                        #Create download link for the PDF
                        b64_pdf= base64.b64encode(pdf_buffer.read()).decode()
                        href= f'<a href="data:application/pdf;base64, {b64_pdf}" download="medical_report_{datetime.now().strftime("%Y%m%d")}.pdf">Download PDF Report</a>'
                        st.markdown(href, unsafe_allow_html= True)

                        #Options to start a disuccion
                        with col2:
                            if st.button("Start Q&A Session"):
                                #Create a QA room for this analysis
                                if "qa_chat" not in st.session_state:
                                    st.session_state_qa_chat= ReportQAChat()

                                room_name= f"Q&A for {uploaded_file.name}"
                                created_qa_id = st.session_state.qa_chat.create_qa_room("Dr. Anonymous", room_name)
                                st.session_state_current_qa_id= created_qa_id
                                st.rerun()

                elif not st.session_state.openai_key:
                    st.warning("Please enter your OPENAI API key in the sidebar to enable analysis")

            else:
                st.error("Unable to process the uploaded file")

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

    elif "analysis_results" in st.session_state and st.session_state.analysis_results:
        st.subheader("Previous Analysis Results")
        st.markdown(st.session_state.analysis_results["analysis"])

        if "findings" in st.session_state.analysis_results:
            st.subheader("Key Findings")
            for idx, finding in enumerate(st.session_state.analysis_results["findings"],1):
                st.markdown(f"{idx}. {finding}")


        #Generate PDF report for previous analysis
        st.subheader("Report")
        if st.button("Generate PDF Report"):
            pdf_buffer= generate_report(st.session_state.analysis_results, include_references= include_references)

        #Create download link for the PDf
        b64_pdf= base64.b64encode(pdf_buffer.read()).decode()
        href= f'<a href="data:application/pdf;base64,{b64_pdf}" download="medical_report_{datetime.now().strftime("%Y%m%d")}.pdf">Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html= True)
        
with tab2:

    #Render the chat interface for collaboration
    try:
        render_chat_interface()
    except Exception as e:
        st.error(f"Error in chat interface: {str(e)}")
        st.info("If you are trying to create a new discusion, please upload and analyze an image first.")

        #Offer a direct way to create a discussion without an image
        st.subheader("Create Discussion Without Image")
        manual_creator= st.text_input("Your Name", value= "Dr. Anonymous")
        manual_description= st.text_input("Case Description")

        if st.button("Create Manual Discussion") and manual_description:
            case_id= create_manual_chat_room(manual_creator, manual_description)
            st.session_state.current_case_id= case_id
            st.rerun()

with tab3:
    #Render the QA Chat Interface
    render_qa_chat_interface()


with tab4:
    #Reports and Analytics section
    st.subheader("Medical Reports & Analytics")

    #Analysis History
    st.markdown('### Analysis History')
    recent_analyses= get_latest_analyses(limit= 10)

    if recent_analyses:
         for idx, analysis in enumerate(recent_analyses, 1):
             with st.expander(f"{idx}. {analysis.get('filename','Unknown')} - {analysis.get('date','')[:10]}"):
                    st.markdown(analysis.get("analysis", "No analysis available"))
                    
                    if analysis.get("findings"):
                        st.markdown("** Key Findings:**")                       
                        for finding_idx, finding in enumerate(analysis["findings"],1):
                            st.markdown(f"{finding_idx}. {finding}")
            
                    col1,col2= st.columns(2)

                    #Generate individual report 
                    with col1:
                        if st.button(f"Generate Report #{idx}"):
                            pdf_buffer =generate_report(analysis, include_reference= include_references)

                            #Create Download Link
                            b64_pdf= base64.b64encode(pdf_buffer.read()).decode()
                            report_name =f"report_{analysis.get('id', 'unknown')[:8]}.pdf"
                            href= f'<a href="data:application/pdf;base64,{b64_pdf}" download="{report_name}">Download Report<\a>'
                            st.markdown(href, unsafe_allow_html= True)

                    #Ask questions about this report
                    with col2:
                        if st.button(f"Q&A on Report #{idx}"):
                            # Create a QA room specially for this report
                            if "qa_chat" not in st.session_state:
                                st.session_state.qa_chat= ReportQAChat()

                            report_name= f"Q&A for {analysis.get('filename', 'Unknown')}"
                            created_qa_id= st.session_state.qa_chat.create_qa_room("Dr. Anonymous", report_name)
                            st.session_state.current_qa_id=created_qa_id

                            # Switch to QA Tab
                            st.rerun()

    else:
        st.info("No previous analyses found. Upload and analyze an image to get started.")

    #Statistics session
    st.markdown("### Statistics")

    #Generate statistics report
    if st.button("Generate Comprehensive Statistics"):
        stats_report= generate_statistics_report()
        if stats_report:
            #Created download link
            b64_pdf= base64.b64encode(stats_report.read()).decode()
            href= f'<a href="data:application/pdf;base64,{b64_pdf}"download="statistics_report.pdf">Download Statistics Report</a>'
            st.markdown(href, unsafe_allow_html= True)


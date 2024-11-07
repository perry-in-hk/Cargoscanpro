import streamlit as st
from langchain_community.document_loaders import AmazonTextractPDFLoader
import openai
import os
import json

# Set up OpenAI API credentials
openai.api_type = "azure"
openai.api_base = "https://hkust.azure-api.net"
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set the title of the app
st.title("Air Way Bill Form")

# File uploader for the image
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

# Create rescan button outside the form
rescan_button = st.button("RESCAN")

def rescan_and_autofill():
    # Perform OCR using Amazon Textract
    loader = AmazonTextractPDFLoader("temp_image.png")
    documents = loader.load()

    # Extract text from the document
    page_content = documents[0].page_content

    # Send the extracted text to OpenAI for formatting
    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo-16k",
        messages=[
            {"role": "user", "content": f"""read {page_content}, Read the following information and format it into a JSON object:\
            Air Way Bill No. (dont give the p letter11 digits it must apeear in the awb and it will be the first 11 letter of the Air Way Bill Barcode , in the format xxx-xxxxxxxx or xxxxxxxxxxx 160-51752201)\:
            Air Way Bill Barcode (if can detect the 16 digits, use the 16 digit first, 16 digits number only(no any english letter), if available, otherwise construct it using the Awb number (11 digits) and usually the number pieces of goods (e.g., for 3 pieces: 00003), e.g.1605175220100001, \):\
            Destination (3 upper case letters, country code):\
            No. of Pieces (e.g., 3): (extract the number followed by No. of Pieces, if not no no. of piece show , output=1)\
            Origin (3 upper case letters, country code):\
            Output should be in a clean JSON format containing only these 5 fields."""}
        ],
    )

    try:
        ocr_data = json.loads(response['choices'][0]['message']['content'])

        # Update the session state with autofilled data
        st.session_state.air_way_bill_no = ocr_data.get("Air Way Bill No.", "")
        st.session_state.air_way_bill_barcode = ocr_data.get("Air Way Bill Barcode", "")
        st.session_state.destination = ocr_data.get("Destination", "")
        st.session_state.num_of_pieces = ocr_data.get("No. of Pieces", "")
        st.session_state.origin = ocr_data.get("Origin", "")

        # Display success message
        st.success("Fields have been autofilled!")
    except json.JSONDecodeError:
        st.error("Failed to parse the OCR output. Please try again.")

if rescan_button:
    rescan_and_autofill()

if uploaded_file:
    # Save uploaded file temporarily
    with open("temp_image.png", "wb") as f:
        f.write(uploaded_file.getbuffer())

    rescan_and_autofill()
if rescan_button:
    rescan_and_autofill()

# Create a form to collect the necessary information
with st.form(key='air_way_bill_form'):
    air_way_bill_no = st.text_input("Air Way Bill No.", value=st.session_state.get("air_way_bill_no", ""))
    air_way_bill_barcode = st.text_input("Air Way Bill Barcode", value=st.session_state.get("air_way_bill_barcode", ""))
    destination = st.text_input("Destination", value=st.session_state.get("destination", ""))
    num_of_pieces = st.text_input("No. of Pieces", value=st.session_state.get("No. of Pieces", ""))
    origin = st.text_input("Origin", value=st.session_state.get("origin", ""))

    # Create button for checkout
    checkout_button = st.form_submit_button("CHECKOUT")



# Logic for button actions
if checkout_button:
    st.success(f"Checkout successful for Air Way Bill No. {air_way_bill_no}")



# Display current values in the session state for verification
st.write("Current Values:")
st.write("Air Way Bill No.:", st.session_state.get("air_way_bill_no", ""))
st.write("Air Way Bill Barcode:", st.session_state.get("air_way_bill_barcode", ""))
st.write("Destination:", st.session_state.get("destination", ""))
st.write("No. of Pieces:", st.session_state.get("num_of_pieces",""))
st.write("Origin:", st.session_state.get("origin", ""))

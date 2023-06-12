import streamlit as st
import pandas as pd
from google.cloud import storage
import os

# Create a client
client = storage.Client()

# Your data bucket name
bucket_name = 'raw-data-tobipets'

# Your frontend bucket name
frontend_bucket_name = 'pipeline-tobipets-streamlit'

def upload_to_bucket(blob_name, file):
    """Upload data to a bucket"""
    print(f"Uploading {blob_name}...")
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_file(file)
    print(f"Uploaded {blob_name} successfully.")

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    print(f"Downloading {source_blob_name}...")
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)
    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

def main():
    # Download the logo from the frontend bucket
    download_blob(frontend_bucket_name, 'tobipets-logo.png', '/tmp/tobipets-logo.png')

    # Add the logo to your application
    st.image('/tmp/tobipets-logo.png')

    # Add a title to your application
    st.title('Tobipets Employee Data Upload')

    # Upload files
    uploaded_file_1 = st.file_uploader("Upload Transactions Excel", type="xlsx")
    uploaded_file_2 = st.file_uploader("Upload Autoship Excel", type="xlsx")
    uploaded_file_3 = st.file_uploader("Upload Inventory Control", type="xlsx")

    # Preview files
    if uploaded_file_1 is not None:
        st.write('Preview of Transactions Excel file:')
        df1 = pd.read_excel(uploaded_file_1)
        st.dataframe(df1.head())

    if uploaded_file_2 is not None:
        st.write('Preview of Autoship Excel file:')
        df2 = pd.read_excel(uploaded_file_2)
        st.dataframe(df2.head())

    if uploaded_file_3 is not None:
        st.write('Preview of Inventory Control Excel file:')
        df3 = pd.read_excel(uploaded_file_3)
        st.dataframe(df3.head())

    # Submit button
    if st.button('Submit'):
        if uploaded_file_1 is not None and uploaded_file_2 is not None and uploaded_file_3 is not None:
            # Reset the file pointers to the beginning
            uploaded_file_1.seek(0)
            uploaded_file_2.seek(0)
            uploaded_file_3.seek(0)
            
            # Upload files
            upload_to_bucket('transactions.xlsx', uploaded_file_1)
            upload_to_bucket('autoships.xlsx', uploaded_file_2)
            upload_to_bucket('inventory_control.xlsx', uploaded_file_3)
            st.write('Files uploaded successfully!')

if __name__ == "__main__":
    main()

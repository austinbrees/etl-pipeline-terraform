from google.cloud import storage, bigquery
import pandas as pd
import os

def inventory_control_cleaning(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    file_name = event['name']
    if file_name != 'inventory_control.xlsx':
        print(f"Ignoring file {file_name} as it is not 'inventory_control.xlsx'.")
        return

    bucket_name = event['bucket']
    download_path = '/tmp/{}'.format(file_name)

    # download the file
    print(f"Downloading file {file_name} from bucket {bucket_name}...")
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.download_to_filename(download_path)
    print(f"File {file_name} downloaded to {download_path}.")

    # Read the Excel file into a DataFrame
    print(f"Reading Excel file into DataFrame...")
    df = pd.read_excel(download_path)
    print("DataFrame created.")
    
    df = df.rename(columns={'STOCK (En almacen)': 'Stock'})

    # perform data cleaning
    col_change = ['Proveedor', 'Pets', 'Marca']
    for i in col_change:
        df[i] = df[i].astype(str)

    # Pets to lowercase
    df['Pets'] = df['Pets'].astype(str).str.lower()

    # Marca values with same brand written indifferent ways
    df['Marca'] = df['Marca'].replace(['Pet Appétit', 'Diamond', 'Bagheera', 'Zee.Dog', 'IPET', 'tpbi', 'unimedical', 'Natural pets'],
                                      ['PetAppetit', 'Diamond Naturals', 'Baghera', 'ZeeDog', 'IPet', 'tobi', 'Unimedical', 'Natural Pets'])

    df = df.copy().replace({'NA': None})

    # upload to BigQuery
    print("Uploading DataFrame to BigQuery...")
    client = bigquery.Client()
    table_id = "impact-project-387115.pipeline.inventory_control"
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",  # append to existing table
    )
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # Wait for the job to complete.
    print("Upload completed.")
import os
from google.cloud import storage, bigquery
import pandas as pd

def autoships_cleaning(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    file_name = event['name']
    if file_name != 'autoships.xlsx':
        print(f"Ignoring file {file_name} as it is not 'autoships.xlsx'.")
        return

    bucket_name = event['bucket']
    download_path = '/tmp/{}'.format(file_name)

    # download the file
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.download_to_filename(download_path)

    # parse and clean the data
    df = pd.read_excel(download_path)
    df = clean_data(df)

    # export the cleaned data to BigQuery
    export_to_bigquery(df)

def clean_data(autoship_df):
    # Generate columns list and new_names dict
    columns = autoship_df.columns.tolist()

    # Rename columns
    new_names = {'Código': 'code', 'Marcas': 'brands', 'SKU': 'SKU', 
            'Precio': 'price', 'Cantidad': 'quantity', 'Estatus': 'status', 
            'Id Cliente': 'user_ID', 'Cliente': 'client', 'Frecuencia': 'frequency_in_weeks', 
            'Lugar': 'place', 'Inicia': 'starts', 'Siguiente Entrega': 'next_delivery', 
            'Última Edición': 'last_edit', 'Creado': 'creation_date'}

    autoship_df.rename(columns=new_names, inplace=True)

    # Move SKU to first column
    column_to_move = autoship_df.pop('SKU')
    autoship_df.insert(0, 'SKU', column_to_move)

    # Translate order status
    status_dict = {'En pausa': 'paused', 'Activo': 'active'}
    autoship_df['status'] = autoship_df['status'].map(status_dict)

    # Fill missing SKU values
    autoship_df['SKU'] = autoship_df['SKU'].replace('Sin SKU', 'no_SKU').fillna('no_SKU')

    # Drop unnecessary columns
    autoship_df = autoship_df.drop(['client', 'place', 'price'], axis=1)

    return autoship_df

def export_to_bigquery(df, dataset_id='pipeline', table_id='autoships'):
    client = bigquery.Client()
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)

    job_config = bigquery.LoadJobConfig()
    job_config.autodetect = True
    job_config.write_disposition = 'WRITE_APPEND'

    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)

    # wait for the load job to complete
    job.result()


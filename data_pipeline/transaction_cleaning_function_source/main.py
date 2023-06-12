import os
from google.cloud import storage, bigquery
import pandas as pd
import numpy as np

def transactions_cleaning(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    file_name = event['name']
    if file_name != 'transactions.xlsx':
        print(f"Ignoring file {file_name} as it is not 'transactions.xlsx'.")
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


def clean_data(df):
    new_names = {'Número de pedido': 'order_number',
 'Estado del pedido': 'order_status',
 'Fecha del pedido': 'order_date',
 'Fecha de pago': 'payment_date',
 'Fecha en la que se completó': 'order_completed_date',
 'Teléfono (facturación)': 'phone_number',
 'ID de usuario': 'user_ID',
 'Nombre de usuario': 'username',
 'Nombre (facturación)': 'name',
 'Apellidos (facturación)': 'last_name',
 'Nombre completo (facturación)': 'full_name',
 'Web del usuario': 'web_user',
 'Nota del cliente': 'client_notes',
 'Correo electrónico del cliente': 'user_email',
 'Fecha del primer pedido del cliente': 'first_order_date',
 'Fecha del último pedido del cliente': 'last_order_date',
 'Pedidos totales del cliente': 'total_orders_from_client',
 'Gasto total del cliente': 'total_amount_spent',
 'Provincia (envío)': 'shipping_province',
 'Ciudad (envío)': 'shipping_city',
 'CANTON AR': 'canton_ar',
 'Dirección línea 2 (envío)': 'address_line_2_shippment',
 'Título del método de pago': 'payment_method',
 'Importe de descuento del carrito': 'cart_discount_amount',
 'Importe de subtotal del pedido': 'order_subtotal_amount',
 'Importe total de impuestos del pedido': 'total_tax_amount_of_order',
 'Importe total del pedido': 'total_amount_order',
 'Título del método de envío': 'shipping_method',
 'Importe de envío del pedido': 'order_shipping_amount',
 'SKU': 'SKU',
 'Artículo #': 'number_of_article',
 'Nombre del artículo': 'article_name',
 'Cantidad': 'quantity',
 'Variación del producto': 'product_variation',
 'Categoría': 'category',
 'Cantidad de existencias': 'stock_quantity',
 'Coste de artículo': 'article_cost',
 'Código de cupón': 'cupon_code',
 'Otro Cupones': 'other_cupons',
 'Importe de descuento': 'amount_discount',
 'Importe de impuestos del descuento': 'discount_tax_amount',
 'Autoship': 'autoship',
 'Ref de partnership': 'partnership_ref'}  # Your new names dictionary here

    df.rename(columns=new_names, inplace=True)

    column_to_move = df.pop('SKU')
    df.insert(0, 'SKU', column_to_move)

    order_status_dict = {
    'En espera': 'on_hold',
    'Pendiente de pago': 'waiting_for_payment',
    'Completado': 'completed',
    'Procesando': 'processing',
    }  # Your order_status_dict here
    df['order_status'] = df['order_status'].map(order_status_dict)

    payment_method_dict = {
    'Tarjetas de crédito/débito': 'credit_or_debit',
    'Pago contra entrega (Datáfono)': 'at_delivery',
    'Pago por medio de  SINPE': 'sinpe',
    'Pago por medio de SINPE': 'sinpe',
    'Otro': 'other',
    np.nan: 'not_specified'

    }  # Your payment_method_dict here
    df['payment_method'] = df['payment_method'].map(payment_method_dict)

    df = df[~df['shipping_method'].isin(['Envío pedido 48693', 'Envío pedido 48879', 'Envío pedido 49284', 'Envío pedido 49934', 'Envío'])]

    shipping_method_dict = {
    'Envío gratuito': 'free',
    'Envío Gratuito': 'free',
    'Envío Regular': 'regular',
    'Envío por encomienda': 'mail',
    'Envío Gratuita': 'free',
    'Envío regular': 'regular',
    'Envío Express': 'express',
    'Envío express': 'express',
    'Envío por Encomienda': 'mail',
    'Envío Encomienda': 'mail',
    'Envío Gratis': 'free',
    'Envío encomienda': 'mail',
    'Envío gratis': 'free',
    'Envío gartuito': 'free',
    'Envío gratuito, Envío': 'free',
    'Envío Regular, Envío Express': 'express',
    'Envío gratutito': 'free',
    'Envío Express, Envío': 'express',
    np.nan: 'not_specified'
    }  # Your shipping_method_dict here
    df['shipping_method'] = df['shipping_method'].map(shipping_method_dict)

    df = df.drop(['phone_number', 'username', 'name', 'last_name', 
                  'full_name', 'user_email', 'web_user', 'client_notes', 
                  'total_amount_spent', 'shipping_province', 'shipping_city', 
                  'canton_ar', 'address_line_2_shippment', 'cart_discount_amount', 
                  'order_subtotal_amount', 'total_tax_amount_of_order', 'total_amount_order', 
                  'article_cost', 'amount_discount', 'discount_tax_amount'], axis=1)  # Columns to drop here

    df['can_be_AS'] = df['category'].apply(lambda x: 'Autoship' in str(x))

    autoship_dict = {
        1 : True,
        np.nan: False
    }

    df['autoship'] = df['autoship'].map(autoship_dict)

    df['has_AS'] = ((~df['cupon_code'].isnull()) | (df['autoship'] == True)) & (df['can_be_AS'] == True)

    return df


def export_to_bigquery(df, dataset_id='pipeline', table_id='transactions'):
    client = bigquery.Client()
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)

    job_config = bigquery.LoadJobConfig()
    job_config.autodetect = True
    job_config.write_disposition = 'WRITE_APPEND'

    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)

    # wait for the load job to complete
    job.result()


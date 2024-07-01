import json
import yfinance as yf
import pandas as pd
import boto3
from io import StringIO

def lambda_handler(event, context):
    # Lista de tickers de las acciones
    tickers = ["AAPL", "GOOGL", "AMZN", "MSFT"]

    # Lista para almacenar los datos de cada ticker
    all_data = []

    # Iterar sobre cada ticker y obtener los datos históricos diarios
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5y", interval="1d")  # Aqui puedes cambiar los intervalos y periodos
        hist.reset_index(inplace=True)  # Resetear el índice para incluir la columna de fecha
        hist['Ticker'] = ticker  # Añadir una columna para identificar el ticker
        all_data.append(hist)

    # Concatenar todos los datos en un único DataFrame
    all_data_df = pd.concat(all_data)

    # Convertir el DataFrame a CSV
    csv_buffer = StringIO()
    all_data_df.to_csv(csv_buffer, index=False)

    # Conectar con S3
    s3 = boto3.client('s3')
    bucket_name = 'nombre-de-tu-bucket'

    # Guardar el CSV en S3
    s3.put_object(
        Bucket=bucket_name,
        Key='stocks_data_diarios.csv',
        Body=csv_buffer.getvalue()
    )

    return {{
        'statusCode': 200,
        'body': json.dumps('Datos guardados en S3')
    }}

        'body': json.dumps('Datos guardados en S3')
    }

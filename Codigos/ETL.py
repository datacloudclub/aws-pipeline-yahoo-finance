import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import pandas as pd

# Inicializar el contexto de Glue
glueContext = GlueContext(SparkContext.getOrCreate())
spark = glueContext.spark_session
job = Job(glueContext)
job.init(sys.argv[0], getResolvedOptions(sys.argv, ['JOB_NAME']))

# Cargar los datos del catálogo de Glue
datasource0 = glueContext.create_dynamic_frame.from_catalog(database = "DatosYahooFinance", table_name = "nombre-de-tu-tabla")

# Convertir a DataFrame de Spark
df = datasource0.toDF()

# Convertir a DataFrame de Pandas
pandas_df = df.toPandas()

# Operaciones ETL
# Convertir la columna de fecha a datetime, ignorando la zona horaria
date_column = 'Date'
pandas_df[date_column] = pd.to_datetime(pandas_df[date_column].str[:10], errors='coerce')
# Eliminar filas con valores nulos después de la conversión a datetime
pandas_df.dropna(subset=[date_column], inplace=True)
# Asegurar que los datos estén ordenados por fecha y símbolo
pandas_df.sort_values(by=[date_column, 'Ticker'], inplace=True)
# Crear columnas adicionales para el análisis
pandas_df['Year'] = pandas_df[date_column].dt.year
pandas_df['Month'] = pandas_df[date_column].dt.month
# Calcular la media móvil de 20 días
pandas_df['20D_MA'] = pandas_df.groupby('Ticker')['Close'].transform(lambda x: x.rolling(window=20).mean())
# Calcular los retornos diarios
pandas_df['Daily_Return'] = pandas_df.groupby('Ticker')['Close'].transform(lambda x: x.pct_change())
# Calcular la volatilidad (desviación estándar de los retornos diarios)
pandas_df['Volatility'] = pandas_df.groupby('Ticker')['Daily_Return'].transform(lambda x: x.rolling(window=20).std())
# Eliminar la columna 'Stock Splits'
pandas_df.drop(columns=['Stock Splits'], inplace=True)

# Diccionario de traducción de nombres de columnas
column_translation = {
    'Date': 'Fecha',
    'Open': 'Apertura',
    'High': 'Alta',
    'Low': 'Baja',
    'Close': 'Cierre',
    'Volume': 'Volumen',
    'Dividends': 'Dividendos',
    'Ticker': 'Símbolo',
    'Year': 'Año',
    'Month': 'Mes',
    '20D_MA': 'Media Móvil 20D',
    'Daily_Return': 'Retorno Diario',
    'Volatility': 'Volatilidad'
}
# Renombrar las columnas
pandas_df.rename(columns=column_translation, inplace=True)

# Convertir de nuevo a DataFrame de Spark
spark_df = spark.createDataFrame(pandas_df)

# Guardar los datos transformados de vuelta en S3
spark_df.write.csv('s3://nombre-de-tu-bucket/datos_acciones_transformados.csv', header=True)

# Finalizar el trabajo
job.commit()

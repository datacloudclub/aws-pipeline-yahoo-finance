# Instructivo: Paso a Paso

## Introducción

Este instructivo proporciona una guía detallada paso a paso para seguir el proyecto de Ingeniería de Datos con AWS y Yahoo Finance. Aquí encontrarás todas las instrucciones necesarias para configurar y ejecutar cada componente del proyecto. 

### Requisitos
- Cuenta activa de AWS
- Conocimientos básicos de los servicios de AWS (Lambda, S3, Glue, RDS, QuickSight y EventBridge)
- Acceso a la API de Yahoo Finance (opcional). En este caso, estaremos usando la biblioteca `yfinance` ya que no tiene límite de llamados.
- Configuración y permisos de IAM adecuados para los servicios de AWS utilizados en el proyecto
- Permisos de administrador en la cuenta de AWS para crear y configurar los servicios necesarios
- Conocimiento básico de Python y Pandas


## Tabla de Contenidos
- [Paso 1: Crear un Bucket en Amazon S3](#paso-1-crear-un-bucket-en-amazon-s3)
- [Paso 2: Obtener Datos de Yahoo Finance usando AWS Lambda](#paso-2-obtener-datos-de-yahoo-finance-usando-aws-lambda)
- [Paso 3: Configurar un Trigger de Ejecución Periódica con Amazon EventBridge](#paso-3-configurar-un-trigger-de-ejecución-periódica-con-amazon-eventbridge)
- [Paso 4: Almacenar los Datos en Amazon RDS](#paso-4-almacenar-los-datos-en-amazon-rds)
- [Paso 5: Procesar y Transformar los Datos con AWS Glue](#paso-5-procesar-y-transformar-los-datos-con-aws-glue)
- [Paso 6: Visualizar los Datos con Amazon QuickSight](#paso-6-visualizar-los-datos-con-amazon-quicksight)

## Paso 1: Crear un Bucket en Amazon S3
<details>
<summary>Haga clic para expandir</summary>
  
1. **Acceder a la Consola de Amazon S3:**
   - Ve a la consola de administración de AWS.
   - Selecciona "S3" en la lista de servicios.

2. **Crear un Bucket:**
   - Haz clic en "Crear bucket".
   - Proporciona un nombre único para el bucket.
   - Selecciona la región apropiada.
   - Configura las opciones de almacenamiento según tus necesidades.
   - Haz clic en "Crear bucket" para finalizar.
</details>

## Paso 2: Obtener Datos de Yahoo Finance usando AWS Lambda
<details>
<summary>Haga clic para expandir</summary>

### Crear una Función Lambda

1. **Acceder a la Consola de AWS Lambda:**
   - Ve a la consola de administración de AWS (https://aws.amazon.com/console/).
   - En la barra de búsqueda, escribe "Lambda" y selecciona el servicio "Lambda".

2. **Crear una Nueva Función Lambda:**
   - Haz clic en "Crear función".
   - Selecciona "Crear desde cero".
   - Proporciona un nombre para la función, por ejemplo, `ObtenerDatosYahooFinance`.
   - En "Rol de ejecución", selecciona "Crear un rol nuevo con permisos básicos de Lambda".
   - Haz clic en "Crear función" al final de la página.

3. **Pegar el Código en la Función Lambda:**
   - Después de crear la función, serás redirigido al panel de configuración de la función.
   - Desplázate hacia abajo hasta la sección "Código fuente" y selecciona el entorno de ejecución "Python 3.x".
   - Elimina cualquier código que ya esté en el editor y pega el siguiente código:
     - Asegúrate de reemplazar `nombre-de-tu-bucket` con el nombre real de tu bucket de S3.  
<br>

   ```python
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
</details>
```
4. **Guardar los Cambios:**
   - Haz clic en el botón "Deploy" (Desplegar) en la parte superior derecha para guardar los cambios.
</details>


## Paso 3: Configurar un Trigger de Ejecución Periódica con Amazon EventBridge
<details>
<summary>Haga clic para expandir</summary>

1. **Acceder a la Consola de Amazon EventBridge:**
   - En la consola de administración de AWS, busca "EventBridge" y selecciona el servicio "Amazon EventBridge".

2. **Crear una Nueva Regla:**
   - Haz clic en "Crear regla".
   - Proporciona un nombre para la regla, por ejemplo, `EjecutarLambdaDiariamente`.
   - En "Tipo de regla", selecciona "Patrón de eventos".
   - Selecciona "Programar expresión" y define una expresión cron para ejecutar la función Lambda diariamente (por ejemplo, `cron(0 0 * * ? *)` para ejecutarla a medianoche UTC).

3. **Seleccionar el Objetivo:**
   - En la sección "Objetivo", selecciona "Función Lambda".
   - En "Seleccionar un objetivo", elige la función Lambda que creaste anteriormente (`ObtenerDatosYahooFinance`).

4. **Crear la Regla:**
   - Haz clic en "Crear" al final de la página para guardar la regla.

### Verificar la Ejecución

1. **Verificar que la Regla esté Habilitada:**
   - Asegúrate de que la regla esté habilitada en el panel de Amazon EventBridge.

2. **Verificar la Ejecución de la Función Lambda:**
   - Comprueba los registros en la consola de AWS Lambda para asegurarte de que la función se ejecute según el cronograma establecido y que los datos se guarden correctamente en S3.
</details>

## Paso 4: Almacenar los Datos en Amazon RDS
<details>
<summary>Haga clic para expandir</summary>

### Crear una Instancia de Amazon Aurora Serverless

1. **Acceder a la Consola de Amazon RDS:**
   - Ve a la consola de administración de AWS (https://aws.amazon.com/console/).
   - En la barra de búsqueda, escribe "RDS" y selecciona el servicio "RDS".

2. **Crear una Nueva Instancia de Base de Datos:**
   - Haz clic en "Crear base de datos".
   - Selecciona el método de creación "Standard Create".
   - En "Motor de base de datos", selecciona "Amazon Aurora".
   - En "Tipo de despliegue", selecciona "Aurora Serverless".
   - Configura los detalles de la instancia:
     - **Versión del motor:** Elige la versión más reciente disponible.
     - **Identificador de la base de datos:** Proporciona un nombre único para tu base de datos, por ejemplo, `mi-aurora-serverless-db`.
     - **Credenciales de administrador:** Proporciona un nombre de usuario y una contraseña para el administrador de la base de datos.
     - **Clase de la instancia:** Selecciona `db.t3.small` (puedes ajustar según tus necesidades y presupuesto).
     - **Configuración de almacenamiento:** Selecciona el almacenamiento predeterminado.
   - Configura las opciones de red:
     - **VPC:** Selecciona la VPC predeterminada o la VPC que estás utilizando.
     - **Subredes:** Asegúrate de seleccionar al menos dos subredes en diferentes zonas de disponibilidad.
     - **Grupo de seguridad:** Selecciona un grupo de seguridad que permita el acceso desde el entorno de AWS Glue.
   - Opciones adicionales:
     - **Copias de seguridad:** Configura según tus necesidades.
     - **Monitorización:** Habilita CloudWatch para supervisar la base de datos.
     - **Mantenimiento:** Programa las ventanas de mantenimiento según tus preferencias.
   - Haz clic en "Crear base de datos" para finalizar.

### Configurar RDS Proxy para Conectar con Aurora Serverless

1. **Crear un RDS Proxy:**
   - Accede a la consola de administración de AWS y busca "RDS" y selecciona "Proxies".
   - Haz clic en "Create proxy".
   - Proporciona un nombre para el proxy, por ejemplo, `AuroraServerlessProxy`.
   - Selecciona el clúster de Amazon Aurora Serverless creado anteriormente.
   - Configura las opciones de conexión:
     - **VPC:** Selecciona la misma VPC utilizada para la base de datos.
     - **Subredes:** Selecciona las subredes correspondientes.
     - **Grupos de seguridad:** Selecciona el mismo grupo de seguridad que permite el acceso desde AWS Glue.
   - Proporciona un nombre de rol IAM que tenga permisos para acceder a RDS.
   - Haz clic en "Create proxy" para finalizar.

### Configurar AWS Glue para Conectar con RDS Proxy

1. **Crear una Conexión en AWS Glue:**
   - Accede a la consola de AWS Glue.
   - Selecciona "Connections" en el panel de navegación.
   - Haz clic en "Add connection".
   - Proporciona un nombre para la conexión, por ejemplo, `ConexionRDSProxy`.
   - Selecciona el tipo de conexión "JDBC".
   - Proporciona la cadena de conexión JDBC para el RDS Proxy, el nombre de usuario y la contraseña.
   - Haz clic en "Crear" para finalizar.

### Configurar los Permisos de IAM

1. **Acceder a la Consola de IAM:**
   - Ve a la consola de administración de AWS (https://aws.amazon.com/console/).
   - En la barra de búsqueda, escribe "IAM" y selecciona el servicio "IAM".

2. **Asignar Políticas Gestionadas por AWS al Rol de IAM:**
   - En el panel de navegación, selecciona "Roles" y luego encuentra el rol utilizado por AWS Glue.
   - Haz clic en el nombre del rol para abrir su configuración.
   - Selecciona la pestaña "Permissions" y luego haz clic en "Add permissions" y "Attach policies".
   - Busca y selecciona las siguientes políticas gestionadas por AWS:
     - `AmazonRDSFullAccess`
     - `AWSGlueServiceRole`
     - `AmazonRDSDataFullAccess`
   - Haz clic en "Attach policy" para asignar las políticas al rol.

</details>

## Paso 5: Procesar y Transformar los Datos con AWS Glue
<details>
<summary>Haga clic para expandir</summary>

### Crear un Job de AWS Glue para Transformar los Datos

1. **Acceder a la Consola de AWS Glue:**
   - Ve a la consola de administración de AWS (https://aws.amazon.com/console/).
   - En la barra de búsqueda, escribe "Glue" y selecciona el servicio "AWS Glue".

2. **Crear un Job en AWS Glue:**
   - Selecciona "Jobs" en el panel de navegación.
   - Haz clic en "Agregar job".
   - Proporciona un nombre para el job, por ejemplo, `TransformarDatosYahooFinance`.
   - Configura el job para que lea los datos de la base de datos `DatosYahooFinance` y los transforme.
   - En "IAM Role", selecciona el rol de IAM con los permisos necesarios.
   - En "Type", selecciona "Spark".
   - En "Glue version", selecciona la versión más reciente disponible.
   - Configura el "Maximum capacity" según tus necesidades, generalmente, con `2` es suficiente para este tipo de tareas.

3. **Pegar el Código de Transformación en el Job de Glue:**
   - Selecciona el tipo de código "Python".
   - Pega el siguiente código en el editor de Glue:
     - Asegúrate de reemplazar 'DatosYahooFinance', `nombre-de-tu-tabla`, `ConexionRDS`, `nombre_de_tu_base_de_datos`, y `rds-proxy-endpoint` con los nombres y rutas reales correspondientes. 
  <br>

  ```python
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

   # Guardar los datos transformados en RDS a través de RDS Proxy
   glueContext.write_dynamic_frame.from_options(
       frame=DynamicFrame.fromDF(spark_df, glueContext, "RDSConnection"),
       connection_type="mysql",
       connection_options={
           "url": "jdbc:mysql://<rds-proxy-endpoint>:3306/nombre_de_tu_base_de_datos",
           "user": "<tu-usuario>",
           "password": "<tu-contraseña>",
           "dbtable": "nombre_de_tu_tabla"
       },
       transformation_ctx="RDSConnection"
   )

   # Finalizar el trabajo
   job.commit()
</details>
```

4. **Guardar y Ejecutar el Job:**
   - Haz clic en "Save" (Guardar) y luego en "Run job" (Ejecutar job) para iniciar el proceso de transformación de los datos.

### Explicación de las Transformaciones

- **Conversión de Fechas:** La columna de fecha se convierte a tipo datetime, ignorando la zona horaria para asegurar una representación consistente de las fechas.
- **Limpieza de Datos:** Se eliminan las filas con valores nulos en la columna de fecha después de la conversión a datetime.
- **Ordenación de Datos:** Los datos se ordenan por fecha y símbolo para facilitar el análisis cronológico.
- **Creación de Columnas Adicionales:** Se crean nuevas columnas para el análisis, incluyendo el año (`Year`) y el mes (`Month`).
- **Media Móvil:** Se calcula la media móvil de 20 días (`20D_MA`) para cada acción, lo cual es útil para identificar tendencias de precios.
- **Retornos Diarios:** Se calculan los retornos diarios (`Daily_Return`) de las acciones para medir el rendimiento diario.
- **Volatilidad:** Se calcula la volatilidad (`Volatility`) como la desviación estándar de los retornos diarios durante un período de 20 días, lo cual ayuda a medir el riesgo.
- **Traducción de Nombres de Columnas:** Se renombran las columnas al español para facilitar la interpretación.

</details>

## Paso 6: Visualizar los Datos con Amazon QuickSight
<details>
<summary>Haga clic para expandir</summary>

### Crear un Dataset en Amazon QuickSight

1. **Acceder a la Consola de Amazon QuickSight:**
   - Ve a la consola de administración de AWS (https://aws.amazon.com/console/).
   - En la barra de búsqueda, escribe "QuickSight" y selecciona el servicio "Amazon QuickSight".

2. **Configuración Inicial de QuickSight:**
   - Si es la primera vez que usas QuickSight, tendrás que configurar la cuenta.
   - Selecciona "Standard" para la edición.
   - Proporciona los detalles de la cuenta, incluyendo el acceso a S3 y la selección de un rol de IAM con los permisos necesarios.
   - Completa el proceso de configuración inicial.

3. **Crear un Nuevo Dataset:**
   - En la consola de QuickSight, haz clic en "Manage data" y luego en "New dataset".
   - Selecciona "RDS" como la fuente de datos.
   - Proporciona un nombre para la fuente de datos, por ejemplo, `YahooFinanceRDS`.
   - Selecciona la instancia de RDS que creaste anteriormente y proporciona las credenciales de acceso.

4. **Seleccionar y Preparar los Datos:**
   - Selecciona la base de datos y la tabla que contiene los datos transformados.
   - Haz clic en "Edit/Preview data" para preparar los datos.
   - Verifica que todos los datos estén correctos y haz clic en "Save & visualize" para continuar.

### Crear un Análisis en Amazon QuickSight

1. **Crear un Nuevo Análisis:**
   - En la consola de QuickSight, haz clic en "New analysis".
   - Selecciona el dataset `YahooFinanceRDS` que creaste anteriormente.

2. **Agregar Visualizaciones:**
   - Usa las herramientas de QuickSight para crear visualizaciones a partir de tus datos.
   - Puedes crear gráficos de líneas para mostrar las tendencias de precios, gráficos de barras para los volúmenes de transacciones, y tablas para mostrar datos detallados.
   - Personaliza las visualizaciones según tus necesidades y preferencias.

3. **Crear Dashboards:**
   - Una vez que hayas creado varias visualizaciones, puedes agruparlas en un dashboard.
   - Haz clic en "Share" y luego en "Publish dashboard".
   - Proporciona un nombre para el dashboard, por ejemplo, `AnálisisYahooFinance`.
   - Configura los permisos para compartir el dashboard con otros usuarios si es necesario.

### Guardar y Compartir

1. **Guardar el Análisis y el Dashboard:**
   - Asegúrate de guardar todos los cambios en el análisis y el dashboard.
   - Puedes acceder a estos en cualquier momento desde la consola de QuickSight.

2. **Compartir el Dashboard:**
   - Si deseas compartir el dashboard con otros usuarios, puedes hacerlo mediante la opción "Share".
   - Proporciona acceso a otros usuarios de QuickSight en tu organización para que puedan ver y colaborar en el análisis.

</details>



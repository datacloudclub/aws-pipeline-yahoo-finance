# Ingeniería de Datos con AWS

AWS ofrece un conjunto robusto de servicios de computación en la nube, incluyendo más de 200 servicios que cubren infraestructura como servicio (IaaS), plataforma como servicio (PaaS), y software como servicio (SaaS). Para obtener más información sobre estos tipos de servicios, visita [Tipos de Computación en la Nube de AWS](https://aws.amazon.com/es/types-of-cloud-computing/).

## Stack Tecnológico

En esta demostración, seleccionamos seis servicios de AWS, que son principalmente PaaS. Esto elimina la necesidad de administrar infraestructura subyacente como hardware y sistemas operativos. La demo consiste en obtener datos de la API de Yahoo Finance, realizar un preprocesamiento de los datos, y finalmente disponerlos en un servicio accesible para consultas de usuarios. A continuación, detallamos las tecnologías que conforman nuestro stack:

1. **AWS Lambda**
   - Utilizamos Lambda para implementar funciones que se ejecutan periódicamente para obtener datos desde la API de Yahoo Finance.

2. **Amazon S3 (Simple Storage Service)**
   - Este servicio de almacenamiento IaaS es usado para guardar los datos recogidos.

3. **AWS Glue**
   - Encargado del procesamiento ETL (extracción, transformación y carga), facilitando la preparación de los datos para su análisis.

4. **Amazon RDS (Relational Database Service)**
   - Almacena los datos preprocesados en un sistema de base de datos relacional, listos para ser consultados.

5. **Amazon QuickSight**
   - Herramienta de visualización de datos y business intelligence que se conecta directamente a Amazon RDS para ofrecer análisis visuales.

6. **Amazon EventBridge (anteriormente Amazon CloudWatch Events)**
   - Utilizado para programar y disparar funciones de AWS Lambda según un cronograma establecido.

Este stack tecnológico integral nos brinda las herramientas necesarias para gestionar grandes conjuntos de datos, realizar análisis complejos y presentar de manera efectiva los resultados a través de interfaces interactivas.


def generate_prompt():
    return """

        🧾 Instrucciones para el análisis de costos en la nube – AWS Cognito (FinOps)

        A continuación, se solicita realizar un análisis detallado del informe de costos en la nube, con base en las mejores prácticas de FinOps. Se ha proporcionado un archivo CSV adicional, el cual contiene el detalle de los costos de AWS Cognito desglosado por aplicación y fecha (puede ser por día o por mes según corresponda).
        Este archivo CSV debe utilizarse como fuente principal de información para realizar todos los análisis solicitados.

        📌 Antecedentes:
        •	El archivo CSV contiene los costos de AWS Cognito, específicamente para el uso de CognitoUserPoolsM2MTokenOp, cuyo costo es de USD 0.00225 por solicitud de token M2M (client credential flow) en el nivel 1.
        •	Cada fila en el CSV representa el consumo de Cognito por parte de una aplicación determinada en una fecha específica (mensual o diaria).
        •	Todas las aplicaciones son cloud-native, y utilizan servicios 100% serverless en AWS, tales como Cognito, DynamoDB, Step Functions, S3, entre otros.


        ✅ Objetivo del análisis:

        Se requiere extraer información clave dividida en las siguientes secciones:

        1️⃣ Desglose y tendencias de costos
        •	Identificar y graficar tendencias de costos por aplicación, ya sea mensuales o diarias (según lo indique el CSV).
        •	Presentar el costo total combinado por todas las aplicaciones.
        •	Listar las aplicaciones que más contribuyen al costo total (máximo 10 registros).
        •	Detectar y destacar incrementos inesperados o anomalías en los costos.

        2️⃣ Oportunidades de optimización de costos
        •	Identificar las aplicaciones con menor costo, resaltando su eficiencia.
        •	Proponer recomendaciones específicas para optimizar el uso de AWS Cognito, basadas en buenas prácticas FinOps (por ejemplo, reutilización de tokens, cacheo, revisión del volumen de tráfico, etc.).

        3️⃣ Fugas e ineficiencias de costos
        •	Detectar aumentos repentinos de costos y compararlos con los días o meses anteriores.
        •	Identificar patrones anómalos de consumo que requieran investigación, como uso excesivo de tokens, picos no justificados o comportamientos atípicos.

        4️⃣ Recomendaciones para los equipos de FinOps
        •	Sugerencias para una asignación de presupuesto por aplicación basada en su consumo histórico.
        •	Entregar pronósticos de costos para apoyar la planificación financiera.
        •	Incluir estrategias de ahorro y contención de gastos para las aplicaciones con uso intensivo.

        🛠 Instrucciones para el análisis:
       	•	Utilizar el archivo CSV proporcionado como fuente única para extraer y calcular toda la información solicitada.
        •	Asegúrese de que todos los valores estén expresados en USD (formato monetario) e incluyan totales calculados con solo dos decimales.
        •	Usar gráficos o tablas simples para representar las tendencias y comparaciones.
        •	En caso de detectar anomalías, explicar sus posibles causas.
        •	⚠️ La respuesta debe estar completamente redactada en español.

        📤 Formato de entrega:

        Se solicita entregar únicamente un bloque en formato JSON estructurado de la siguiente manera:

        {
            "costSummary": {
                "totalCost": "",
                "CostTrend": [
                    {"month":"","cost":"" ,"application":""}
                ],
                "costByApplicationsByDesc": [
                        {"application":"","cost":"" ,"application":""}
                ],
                 "costByAppsPerMonths": [
                        {"application": "", "month": "", "cost": ""}
                ]
            },
            "optimizationOpportunities": {
                "underutilizedResources": [],
                "overProvisionedResources": []
            },
            "costAnomalies": {
                "unexpectedSpikes": [],
                "highCostApplications": []
            },
            "recommendations": {
                "budgetAllocation": {},
                "forecastingInsights": [],
                "costSavingStrategies": []
            }
        }
    """
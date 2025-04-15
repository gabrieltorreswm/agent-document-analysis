def get_body_message_daily(data_response_model,url_signed):

    try:
         # Custom email subject & message body
        print(f'data_response_model : {data_response_model}')

        total_cost = data_response_model["costSummary"]["totalCost"]
        top_apps = data_response_model["costSummary"]["costByApplicationsByDays"]
        costbymonth = data_response_model["costSummary"]["totalCostByDays"]
        underutilized_resources = data_response_model["optimizationOpportunities"]["underutilizedResources"]
        over_provisioned_resources = data_response_model["optimizationOpportunities"]["overProvisionedResources"]
        cost_anomalies = data_response_model["costAnomalies"]["unexpectedSpikes"]
        recommendations = data_response_model["recommendations"]["costSavingStrategies"]
        forecastingInsights = data_response_model["recommendations"]["forecastingInsights"]
        conclusion = data_response_model["forecasting"]["conclusion"]

        # Format top-cost applications
        top_apps_str = "\n".join(
            [f"- {app['application']}: {app['cost']}" for app in top_apps]
        )

        # Format daily cost trend
        costbymonth_str = "\n".join(
            [f"* {app['day']}: {app['cost']}" for app in costbymonth]
        )

        # Format underutilized resources
        underutilized_str = "\n".join([f"   - {item}" for item in underutilized_resources])

        # Format over-provisioned resources
        over_provisioned_str = "\n".join([f"   - {item}" for item in over_provisioned_resources])

        # Format cost anomalies
        anomalies_str = "\n".join(
            [f"* {anomaly}" for anomaly in cost_anomalies]
        )

        # Format recommendations
        recommendations_str = "\n".join([f"   - {rec}" for rec in recommendations])

        # Format forecastingInsights
        forecastingInsights_str = "\n".join([f"   - {rec}" for rec in forecastingInsights])

        email_body = f"""
            <html>
            <head>
                <style>
                body {{ font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #333; }}
                h2 {{ color: #2F855A; }}
                h3 {{ margin-bottom: 0; }}
                p {{ margin-top: 0; }}
                ul {{ margin-top: 0; }}
                .section-title {{ font-weight: bold; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <p>¡Hola! Espero todo este yendo muy bien. Aca les comparto el reporte de Cognito, generado y analizado por un agente IA cloud</p>
                <p>Queremos llevar nuestros análisis financieros en la nube al siguiente nivel. Buscamos refinar nuestro agente inteligente actual para que profundice aún más en el análisis de las fluctuaciones de costos de nuestras aplicaciones en AWS.</p>
                
                <h3>📊Costos Diarios </h3>
                <pre>{costbymonth_str if costbymonth_str else "No recommendations at this time."}</pre>

                <img src="{url_signed}" alt="Chart" style="height: 400px; width: 700px" /img>

                <h3>📣 Pronostico y tendencias</h3>
                <pre>{forecastingInsights_str if forecastingInsights else "No recommendations at this time."}</pre>

                <h3>🚨 Anomalías de costos</h3>
                <pre>{anomalies_str if cost_anomalies else "No anomalies detected."}</pre>

                <h3>🧠 Recomendaciones para ahorrar costos</h3>
                <pre>{recommendations_str if recommendations else "No recommendations at this time."}</pre>


                <h3>💡 Analisis/Conclusion</h3>
                <pre>{conclusion}</pre>

                <p style="margin-top: 30px;">
                Saludos,<br/>
                <strong>Servicios Cloud</strong>
                </p>
            </body>
            </html>
            """
        return email_body
    except Exception as ex:
        print(f"Error get_body_message {ex}")

        return None
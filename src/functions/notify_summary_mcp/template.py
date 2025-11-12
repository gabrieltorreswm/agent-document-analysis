def get_body_message(data_analisis):

    try:
         # Custom email subject & message body
        print(f'data_analisis : {data_analisis}')


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


                <h3>📝 Nota: </h3>
                <div style="background-color: #f9f9f9; border-left: 4px solid #ccc; padding: 10px; font-style: italic; font-size: 14px; color: #555;">
                    {{data_analisis}}
                    para generar estimaciones precisas a nivel diario.
                </div>

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
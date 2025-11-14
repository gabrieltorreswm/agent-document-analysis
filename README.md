
# Welcome to your CDK Python project! Uopda

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!



Event anomaly detection event reciever


Event received: {'Records': 
[{'EventSource': 'aws:sns', 
'EventVersion': '1.0', 
'EventSubscriptionArn': 
'arn:aws:sns:us-east-1:471112847654:grafana-topic-notify:2ddfe8f6-d7d2-4ff3-9983-e4ca910b20ee', 
'Sns': {'Type': 
'Notification', 'MessageId': 'c7e448a3-6781-54dd-a14a-29321e5b444c',
'TopicArn': 'arn:aws:sns:us-east-1:471112847654:grafana-topic-notify',
'Message': '{"AlarmName":"# Error Api  |  Verificarseg  |  Inicio de Sesión",
"AlarmDescription":"Se ha generado una alarma en el endpoint de inicio de sesión del API de Banca Móvil, debido a la detección de un patrón de comportamiento anómalo que podría indicar un incidente o actividad no habitual.",
"AWSAccountId":"471112847654",
"AlarmConfigurationUpdatedTimestamp":"2025-11-14T17:27:42.228+0000",
"NewStateValue":"ALARM",
"NewStateReason":"Thresholds Crossed: 1 out of the last 4 datapoints [537.0 (14/11/25 18:39:00)] was less than the lower thresholds [193.33593366980995] or greater than the upper thresholds [531.4406901351432] (minimum 1 datapoint for OK -> ALARM transition).","StateChangeTime":"2025-11-14T18:40:26.838+0000","Region":"US East (N. Virginia)","AlarmArn":"arn:aws:cloudwatch:us-east-1:471112847654:alarm:# Error Api  |  Verificarseg  |  Inicio de Sesión","OldStateValue":"OK","OKActions":[],"AlarmActions":["arn:aws:sns:us-east-1:471112847654:grafana-topic-notify"],"InsufficientDataActions":[],"Trigger":{"Period":60,"EvaluationPeriods":4,"DatapointsToAlarm":1,"ComparisonOperator":"LessThanLowerOrGreaterThanUpperThreshold","ThresholdMetricId":"ad1","TreatMissingData":"missing","EvaluateLowSampleCountPercentile":"","Metrics":[{"Id":"m1","MetricStat":{"Metric":{"Dimensions":[{"value":"bmp-msp-verificarseg-pro","name":"ApiName"},{"value":"/iniciarsesion","name":"Resource"},{"value":"pro","name":"Stage"},{"value":"POST","name":"Method"}],"MetricName":"Count","Namespace":"AWS/ApiGateway"},"Period":60,"Stat":"Sum"},"ReturnData":true,"AccountId":"775096123702"},{"Expression":"ANOMALY_DETECTION_BAND(m1, 1.5)","Id":"ad1","Label":"Count (expected)","ReturnData":true}]}}', 'Timestamp': '2025-11-14T18:40:26.892Z', 'SignatureVersion': '1', 'Signature': 'jwsJmO5tHpVzzgqzuvkonrsKSLxwg79HutxDBNS5famzsbzS8gMiq1kb1SZHM1aV1IUPDkW5nuh2HASp+09i4Wes6xGuoP9TNUdGUFWrl83rQuCfg3kEpnx8urPiVxAqVn0FSxZD+8RKBhPN6UlDXDd5TXTr5xmXiR0L85Fpe6HjW0TfpGz4ziDido206x5a3yXTzmb6HwvskTLwfFYoR/dCSGkmiU9RdVIDGucwsbo6jeGj38waWHUWVzJsYBLDL8O1270nz5Ot6+yKQzvraihm+1SbRyXuyuL+2GFKxt/dPobuD5H187G3TWKCToxu5Z8Fd5MeqguF4gpx+k9+1g==', 'SigningCertUrl': 'https://sns.us-east-1.amazonaws.com/SimpleNotificationService-6209c161c6221fdf56ec1eb5c821d112.pem', 'Subject': 'ALARM: "# Error Api  |  Verificarseg  |  Inicio de Sesi_n" in US East (N. Virginia)', 'UnsubscribeUrl': 'https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:471112847654:grafana-topic-notify:2ddfe8f6-d7d2-4ff3-9983-e4ca910b20ee', 'MessageAttributes': {}}}]}


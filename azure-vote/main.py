from flask import Flask, request, render_template
import os
import random
import redis
import socket
import sys
import logging
from datetime import datetime

# App Insights
# App Insights
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.ext.azure.trace_exporter import AzureExporter


connection_string = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING') or "InstrumentationKey=11630375-f7e5-41fd-a228-6fc1498d04ca;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/;LiveEndpoint=https://westus.livediagnostics.monitor.azure.com/;ApplicationId=0ea2b8b4-e5ca-42a7-b6cd-1791831c09e8"
# Logging
# Logging
logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(
        connection_string=connection_string
    )
)
logger.setLevel(logging.INFO)

# Metrics
# Metrics


# Tracing
tracer = Tracer(
    exporter=AzureExporter(
        connection_string=connection_string
    ),
    sampler=ProbabilitySampler(1.0)
)

app = Flask(__name__)

# Requests
middleware = FlaskMiddleware(
    app,
    exporter=AzureExporter(
        connection_string=connection_string
    )
)

# Load configurations from environment or config file
app.config.from_pyfile('config_file.cfg')

if ("VOTE1VALUE" in os.environ and os.environ['VOTE1VALUE']):
    button1 = os.environ['VOTE1VALUE']
else:
    button1 = app.config['VOTE1VALUE']

if ("VOTE2VALUE" in os.environ and os.environ['VOTE2VALUE']):
    button2 = os.environ['VOTE2VALUE']
else:
    button2 = app.config['VOTE2VALUE']

if ("TITLE" in os.environ and os.environ['TITLE']):
    title = os.environ['TITLE']
else:
    title = app.config['TITLE']

# Redis Connection
# Redis configurations for AKS
redis_server = os.environ["REDIS"]

try:
    if "REDIS_PWD" in os.environ:
        r = redis.StrictRedis(
            host=redis_server,
            port=6379,
            password=os.environ["REDIS_PWD"]
        )
    else:
        r = redis.Redis(host=redis_server, port=6379)

    r.ping()

except redis.ConnectionError:
    exit("Failed to connect to Redis, terminating.")

# Change title to host name to demo NLB
if app.config['SHOWHOST'] == "true":
    title = socket.gethostname()

# Init Redis
if not r.get(button1): r.set(button1,0)
if not r.get(button2): r.set(button2,0)

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'GET':

        # Get current values
        with tracer.span(name="Get Cats Vote"):
         vote1 = r.get(button1).decode("utf-8")

        with tracer.span(name="Get Dogs Vote"):
         vote2 = r.get(button2).decode("utf-8")

        # Return index with values
        return render_template("index.html", value1=int(vote1), value2=int(vote2), button1=button1, button2=button2, title=title)

    elif request.method == 'POST':

        if request.form['vote'] == 'reset':

            # Empty table and return results
            r.set(button1,0)
            r.set(button2,0)
            vote1 = r.get(button1).decode('utf-8')
            properties = {'custom_dimensions': {'Cats Vote': vote1}}
            logger.info(
                "Cats vote reset",
                extra=properties
            )

            vote2 = r.get(button2).decode('utf-8')
            properties = {'custom_dimensions': {'Dogs Vote': vote2}}
            logger.info(
                "Dogs vote reset",
                extra=properties
            )

            return render_template("index.html", value1=int(vote1), value2=int(vote2), button1=button1, button2=button2, title=title)

        else:

            # Insert vote result into DB
            vote = request.form['vote']
            r.incr(vote,1)

            # Get current values
            vote1 = r.get(button1).decode('utf-8')
            vote2 = r.get(button2).decode('utf-8')

            # Return results
            return render_template("index.html", value1=int(vote1), value2=int(vote2), button1=button1, button2=button2, title=title)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True,
        debug=False
    )
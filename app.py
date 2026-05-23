from flask import Flask, request, jsonify
import requests
import urllib3
import logging

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from formatter import format_alerts

app = Flask(__name__)

# Disable SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("logs/webhook.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)

session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)


#
# ZULIP ROUTE
#
@app.route('/zulip', methods=['POST'])
def send_message():

    try:

        logger.info("Received Zulip webhook request")

        webhook_url = request.args.get("webhook_url")
        email = request.args.get("email")
        token = request.args.get("token")
        to = request.args.get("to")
        topic = request.args.get("topic", "alerts")

        ignore_ssl = request.args.get(
            "ignore_ssl",
            "false"
        ).lower() == "true"

        if not all([webhook_url, email, token, to]):

            return jsonify({
                "status": "error",
                "message": "Missing required query parameters"
            }), 400

        body = request.json

        content = format_alerts(body)

        url = f"{webhook_url}/api/v1/messages"

        payload = {
            "type": "stream",
            "to": to,
            "topic": topic,
            "content": content
        }

        response = session.post(
            url,
            auth=(email, token),
            data=payload,
            verify=not ignore_ssl,
            timeout=30
        )

        return jsonify({
            "status": "success",
            "zulip_status_code": response.status_code,
            "zulip_response": response.json()
        })

    except Exception as e:

        logger.exception("Unhandled exception")

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


#
# MATTERMOST ROUTE
#
@app.route('/mattermost', methods=['POST'])
def send_mattermost():

    try:

        logger.info("Received Mattermost webhook request")

        webhook_url = request.args.get("webhook_url")

        ignore_ssl = request.args.get(
            "ignore_ssl",
            "false"
        ).lower() == "true"

        if not webhook_url:

            return jsonify({
                "status": "error",
                "message": "Missing webhook_url parameter"
            }), 400

        body = request.json

        content = format_alerts(body)

        payload = {
            "text": content
        }

        response = session.post(
            webhook_url,
            json=payload,
            verify=not ignore_ssl,
            timeout=30
        )

        return jsonify({
            "status": "success",
            "mattermost_status_code": response.status_code,
            "mattermost_response": response.text
        })

    except Exception as e:

        logger.exception("Unhandled exception")

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':

    logger.info("Starting webhook relay service on port 8686")

    app.run(host='0.0.0.0', port=8686)

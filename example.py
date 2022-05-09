import logging

from flask import Flask

from github_proxy import blueprint

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG, force=True)

app = Flask(__name__)

app.register_blueprint(blueprint)
app.register_blueprint(
    blueprint, name="github_enterprise_proxy", url_prefix="/api/v3"
)  # enterprise server

if __name__ == "__main__":
    app.run()

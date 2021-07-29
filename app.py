from flask import Flask


app = Flask(__name__)



@app.route("/")
def root():
    return "Now running the flask app!"


if __name__ == "__main__":
    app.run()

from app.conf import app

app


if __name__ == "main":
    app.run(host="127.0.0.1", debug=True)

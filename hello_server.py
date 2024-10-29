#! /usr/bin/python3

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello():
    return '<html><body><h1>Hello, this was rendered directly from Python</h1</body></html>'

@app.route('/premade')
def premade():
    output = render_template('hello.html')
    return output

@app.route('/dynamic')
def dynamic():
    output = render_template('dynamic.html', myText="<h1>From Python</h1>")
    return output
if __name__ == '__main__':
    app.run(port=8000, debug=True, host="0.0.0.0")
from flask import Flask, redirect, render_template, request
# from flask_sqlalchemy import SQLAlchemy
import numpy as np
import random
import json
import os

app = Flask(__name__)

viewership = {
	'data': [123456,234567,345678,456789,567890,678901]
}
	

@app.route("/", methods=['GET', 'POST'])
def home():
	return render_template('home.html', data=viewership)

if __name__ == "__main__":
	app.run(port=1234, debug=True)
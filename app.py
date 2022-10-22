from flask import Flask, redirect, render_template, request
# from flask_sqlalchemy import SQLAlchemy
import numpy as np
import random
import json

app = Flask(__name__)
CONFIG = json.load(open('./config/config.json')) # for future configs

# dummy data: actual data can store in temporarily store in JSON moving forward
viewership = {
	'data': [123456,234567,345678,456789,567890,678901],
	'label': 'Viewership'
}

@app.route("/", methods=['GET', 'POST'])
def home():
	if request.method == 'POST':
		# read user's dropdown input
		if request.form.get("submit-button") == "Submit":
			print(request.form["period"], request.form["genre"])

	return render_template('home.html', data=viewership)

if __name__ == "__main__":
	app.run(port=1234, debug=True)
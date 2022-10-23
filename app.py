from flask import Flask, redirect, render_template, request
# from flask_sqlalchemy import SQLAlchemy
import numpy as np
import random
import json

app = Flask(__name__)
CONFIG = json.load(open('./config/config.json')) # for future configs

selection = {
	'period': 'yearly',
	'genre': 'action'
}

# dummy data: actual data can store in temporarily store in JSON moving forward
viewership = {
	'labels': ["1/1/2019", '2/1/2019', '3/1/2019', '4/1/2019', '5/1/2019', '6/1/2019'],
	'data': [123456, 234567, 345678, 456789, 567890, 678901],
	'label': 'Viewership',
	'title': 'Vierwership Trend'
}

@app.route("/", methods=['GET', 'POST'])
def home():
	global selection
	if request.method == 'POST':
		# read user's dropdown input
		if request.form.get("submit-button") == "Submit":
			print(request.form["period"], request.form["genre"])
			selection['period'] = request.form['period']; selection['genre'] = request.form['genre']
	print(selection)
	return render_template('home.html', data=viewership, selection=selection)

if __name__ == "__main__":
	app.run(port=1234, debug=True)
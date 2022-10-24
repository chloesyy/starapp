from flask import Flask, redirect, render_template, request
# from flask_sqlalchemy import SQLAlchemy
import numpy as np
import random
import json
import psycopg2
import datetime

app = Flask(__name__)
CONFIG = json.load(open('./config/config.json')) # for future configs

class POSTGRES:
    def __init__(self):
        self.conn = self.get_db_connection()
        self.cur = self.conn.cursor()
        
    def get_db_connection(self):
        # Connect to postgres
        conn = psycopg2.connect(
            host = CONFIG["postgres"]["host"],
            database = CONFIG["postgres"]["database"],
            user = CONFIG["postgres"]["user"],
            password = CONFIG["postgres"]["password"]
        )
        return conn

    def query_db(self, query):
        self.cur.execute(query)
        result = self.cur.fetchall()
        
        return result
    
    def close(self):
        self.cur.close()
        self.conn.close()

selection = {
	'period': 'yearly',
	'genre': 'action'
}

# dummy data: actual data can store in temporarily store in JSON moving forward
# viewership = {
# 	'labels': ["1/1/2019", '2/1/2019', '3/1/2019', '4/1/2019', '5/1/2019', '6/1/2019'],
# 	'data': [123456, 234567, 345678, 456789, 567890, 678901],
# 	'label': 'Viewership',
# 	'title': 'Vierwership Trend'
# }
viewership = {
	'labels': None,
	'data': None,
	'label': 'Viewership',
	'title': 'Vierwership Trend'
}

@app.route("/", methods=['GET', 'POST'])
def home():
    global selection

    pg = POSTGRES()                                         # Start connection to db
    views = pg.query_db('SELECT * FROM viewership;')        # Queries db
    
    # Format to pass data in render_template (change accordingly)
    views = list(zip(*views))
    labels = views[0]
    data = views[1]
    viewership["labels"] = [datetime.datetime.strftime(i, "%d/%m/%Y") for i in labels]
    viewership["data"] = data
    
    pg.close()                                              # Close connection to db


    if request.method == 'POST':
        # read user's dropdown input
        if request.form.get("submit-button") == "Submit":
            print(request.form["period"], request.form["genre"])
            selection['period'] = request.form['period']; selection['genre'] = request.form['genre']
    print(selection)
    return render_template('home.html', data=viewership, selection=selection)

if __name__ == "__main__":
	app.run(port=1234, debug=True)
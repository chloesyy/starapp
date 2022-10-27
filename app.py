import os
from flask import Flask, redirect, render_template, request
# from flask_sqlalchemy import SQLAlchemy
import numpy as np
import random
import json
import psycopg2
import datetime

app = Flask(__name__)

# TODO: read distnct dropdown values, aggregate by time (week + month) 

IS_PROD = os.environ.get('IS_HEROKU', None)
if not IS_PROD:
    CONFIG = json.load(open('./config/config.json'))

class POSTGRES:
    def __init__(self):
        self.conn = self.get_db_connection()
        self.cur = self.conn.cursor()
        
    def get_db_connection(self):
        if IS_PROD:
            print("IN PRODUCTION")
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            pass
        else:
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

def replace_nth(string, old, new, n):
    index_of_occurrence = string.find(old)
    occurrence = int(index_of_occurrence != -1)
    while index_of_occurrence != -1 and occurrence != n:
        index_of_occurrence = string.find(old, index_of_occurrence + 1)
        occurrence += 1
    if occurrence == n:
        return (
            string[:index_of_occurrence] + new +
            string[index_of_occurrence+len(old):]
        )
    return string

selection = {
	'period': 'Daily',
	'genre': 'ALL',
    'country': 'ALL',
    'plan': 'ALL'
}

options = {
    "period_options" : ["Daily", "Weekly", "Monthly", "Quarterly"],
    "country_options" : ["ALL", "Indonesia", "Italy", "Uruguay", "Sweden"],
    "plan_options" : ["ALL", "Basic", "Standard", "Premium"],
    "genre_options" : ["ALL", "Movies"]
}

viewership_fact = {
	'labels': None,
	'data': None,
	'label': 'Viewership',
	'title': 'Vierwership Trend'
}

@app.route("/", methods=['GET', 'POST'])
def home():
    global selection
    if request.method == 'POST':
        # read user's dropdown input
        if request.form.get("submit-button") == "Submit":
            pg = POSTGRES()
            selection['period'] = request.form['period']; selection['genre'] = request.form['genre']; selection['country'] = request.form['country']; selection['plan'] = request.form['plan']
            query = 'SELECT d1.date, SUM(f.view_duration) FROM viewership_fact f, date_dim d1, loc_dim d2, mem_dim d3, show_dim d4 WHERE f.date_key = d1.date_key AND f.loc_key = d2.loc_key AND f.mem_key = d3.mem_key AND f.show_key = d4.show_key GROUP BY d1.date ORDER BY d1.date DESC;'
            if selection['genre'] != 'all':
                query_one, query_three = query.split('GROUP BY')[0], ' GROUP BY' + query.split('GROUP BY')[1]
                query_two = f"AND d4.genre = \'{selection['genre'].title()}\'"
                query = query_one + query_two + query_three
            elif selection['country'] != 'all': 
                query_one, query_three = query.split('GROUP BY')[0], ' GROUP BY' + query.split('GROUP BY')[1]
                query_two = f"AND d2.country_name = \'{selection['country'].title()}\'"
                query = query_one + query_two + query_three       
            elif selection['plan'] != 'all':
                query_one, query_three = query.split('GROUP BY')[0], ' GROUP BY' + query.split('GROUP BY')[1]
                query_two = f"AND d3.plan_type = \'{selection['plan'].title()}\'"
                query = query_one + query_two + query_three         
            # elif selection['period'] == 'monthly':
            #     query = replace_nth(query, 'd1.date', '(d1.month, d1.year)', 4)
            #     query = replace_nth(query, 'd1.date', '(d1.month, d1.year)', 3)
            #     query = replace_nth(query, 'd1.date', 'd1.month, d1.year', 1)
            #     print(query)
                

            views = list(map(list, zip(*pg.query_db(query))))
            if len(views[0]) >= 30: # if series is more than 30, Chart.js will truncate the dates
                viewership_fact["labels"] = [datetime.datetime.strftime(i, "%d/%m/%Y") for i in views[0]][:30][::-1]
                viewership_fact["data"] = views[1][:30][::-1]
            else:
                viewership_fact["labels"] = [datetime.datetime.strftime(i, "%d/%m/%Y") for i in views[0]][::-1]
                viewership_fact["data"] = views[1][::-1]                
            pg.close()
    else:
        pg = POSTGRES()
        query = 'SELECT d1.date, SUM(f.view_duration) FROM viewership_fact f, date_dim d1  WHERE f.date_key = d1.date_key GROUP BY d1.date ORDER BY d1.date DESC;'
        views = list(map(list, zip(*pg.query_db(query))))
        viewership_fact["labels"] = [datetime.datetime.strftime(i, "%d/%m/%Y") for i in views[0]][:30][::-1]
        viewership_fact["data"] = views[1][:30][::-1]
        pg.close()

    print(selection)
    return render_template('home.html', data=viewership_fact, selection=selection, options=options)

if __name__ == "__main__":
	app.run(debug=True)
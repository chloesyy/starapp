import os
from flask import Flask, flash, make_response, redirect, render_template, request, url_for
# from flask_sqlalchemy import SQLAlchemy
import io
import csv
import numpy as np
import random
import json
import psycopg2
import datetime

app = Flask(__name__)
# random key set for flask flash to work
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

IS_PROD = os.environ.get('IS_HEROKU', None)
if not IS_PROD:
	CONFIG = json.load(open('./config/config.json'))

class POSTGRES:
    def __init__(self):
        self.conn = self.get_db_connection()
        self.cur = self.conn.cursor()
        
    def get_db_connection(self):
        if IS_PROD:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        else:
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
	'period': 'Daily',
	'genre': 'ALL',
	'country': 'ALL',
	'plan': 'ALL'
}

pg = POSTGRES()
pairs = (('genre_1', 'show_dim'), ('plan_type', 'mem_dim'), ('country_name', 'loc_dim'))
options = {"date_dim": ["Daily", "Weekly", "Monthly"]}
for pair in pairs:
	output = sorted(list(sum(pg.query_db(f'SELECT DISTINCT {pair[0]} FROM {pair[1]};'), ())))
	output.insert(0, 'ALL')
	options[pair[1]] = output

viewership_fact = {
	'labels': None,
	'data': None,
	'label': 'Viewership',
	'title': 'Viewership Trend'
}

viewership_period_dict = { 
    "daily":"date", 
    "weekly": "week", 
    "monthly":"month",
    "quarterly" : "quarter"
}

######################## CATEGORICAL DATA ########################
categorical_selection = {
    'period': '7 Days',
    'y_axis': 'Views',
    'x_axis': 'Genre',
    'start_date': '2022-10-22'
}

categorical_options = {
    'period': ['7 Days', '1 Month', '1 Quarter', '6 Months', '1 Year'],
    'y_axis': ['Views', 'Viewing Duration'],
    'x_axis': ['Genre', 'Movie', 'Country', 'Director', 'Plan']
}

categorical_query = {
    'period': ['7 days', '30 days', '3 months', '6 months', '1 year'],
    'y_axis': ['COUNT(*)', 'SUM(f.view_duration)'],
    'x_axis': [
        {
            'key': 'show_key',
            'column': 'genre_1',
            'name': 'genre',
            'table': 'show_dim'
        },
        {
            'key': 'show_key',
            'column': 'title',
            'name': 'movie',
            'table': 'show_dim'
        },
        {
            'key': 'loc_key',
            'column': 'country_name',
            'name': 'country',
            'table': 'loc_dim'
        },
        {
            'key': 'show_key',
            'column': 'director',
            'name': 'director',
            'table': 'show_dim'
        },
        {
            'key': 'mem_key',
            'column': 'plan_type',
            'name': 'plan',
            'table': 'mem_dim'
        },
    ]
}

categorical_data = {
    'labels': None,
    'data': None,
    'label': 'Categorical',
    'title': 'Categorical Chart'
}

######################## INSIGHTS DATA ########################

insights_data = {
	'id': None,
	'id_duration': None,
	'title': None,
	'title_duration': None,
	'genre': None,
	'genre_duration': None,
	'age_rating': None,
	'age_rating_duration': None,
	'country': None,
	'country_duration': None
}

insights_query = {
	'selection': ['d3.mem_id', 'd2.title', 'd2.genre_1', 'd2.age_rating', 'd4.country_name'],
	'update_data': [('id', 'id_duration'), ('title', 'title_duration'), ('genre', 'genre_duration'), ('age_rating', 'age_rating_duration'), ('country', 'country_duration')]
}

######################## QUERY DATA ########################
custom_query_options = {'date_dim' : ['7 days', '30 days', '3 months', '6 months', '1 year']}
for pair in pairs:
	output = sorted(list(sum(pg.query_db(f'SELECT DISTINCT {pair[0]} FROM {pair[1]};'), ())))
	output.insert(0, 'ALL')
	custom_query_options[pair[1]] = output

custom_query_default = {
    'period':['1 year'], 
    'genre':['ALL'], 
    'country':['ALL'], 
    'plan':['ALL'],
    'sort_by':['period'],
    'sort':['asc']}

## table, selection, join_conditions are all fixed
custom_query_query = {
    'table': ['show_dim d1', 'loc_dim d2', 'mem_dim d3', 'date_dim d4', 'viewership_fact f'],
    'selection': ['d4.date','d1.genre_1', 'd2.country_name', 'd3.plan_type', 'f.view_duration'],
    'join_conditions': ['f.show_key = d1.show_key', 'f.loc_key = d2.loc_key', 'f.mem_key = d3.mem_key', 'f.date_key = d4.date_key'],
    'filter': {'genre':'d1.genre_1', 'country':'d2.country_name', 'plan':'d3.plan_type', 'period':'d4.date'},
    'csv_header': ['date', 'genre', 'country', 'plan_type', 'view_duration_mins']
}

@app.route("/", methods=['GET', 'POST'])
def insights():
	for selection_index in range(len(insights_query['selection'])):
		query = f"SELECT {insights_query['selection'][selection_index]}, SUM(f.view_duration) AS total FROM viewership_fact f, date_dim d1, show_dim d2, mem_dim d3, loc_dim d4 WHERE f.date_key = d1.date_key AND f.show_key = d2.show_key AND f.mem_key = d3.mem_key AND f.loc_key = d4.loc_key AND d1.date >= DATE '2022-10-22' - INTERVAL '1 month' GROUP BY {insights_query['selection'][selection_index]} ORDER BY total DESC LIMIT 1;"
		views = list(map(list, zip(*pg.query_db(query))))
		insights_data[insights_query['update_data'][selection_index][0]] = views[0][0]; insights_data[insights_query['update_data'][selection_index][1]] = views[1][0]
	return render_template('insights.html', data=insights_data)

@app.route("/viewership", methods=['GET', 'POST'])
def viewership():
    global selection
    query = None
    if request.method == 'POST':
        if request.form.get("submit-button") == "Submit":
            selection['period'] = request.form['period']
            selection['genre'] = request.form['genre']
            selection['country'] = request.form['country']
            selection['plan'] = request.form['plan']
            query = 'SELECT d1.date, SUM(f.view_duration) FROM viewership_fact f, date_dim d1, loc_dim d2, mem_dim d3, show_dim d4 WHERE f.date_key = d1.date_key AND f.loc_key = d2.loc_key AND f.mem_key = d3.mem_key AND f.show_key = d4.show_key GROUP BY d1.date ORDER BY d1.date DESC;'
            query_one, query_three = query.split('GROUP BY')[0], ' GROUP BY' + query.split('GROUP BY')[1]
            query_two = ""
            idx_0, idx_1 = 0, 1
            if selection['genre'] != 'all':
                query_two = query_two + f"AND d4.genre_1 = \'{selection['genre'].title()}\'"
            if selection['country'] != 'all': 
                query_two = query_two + f"AND d2.country_name = \'{selection['country'].title()}\'"
            if selection['plan'] != 'all':
                query_two = query_two + f"AND d3.plan_type = \'{selection['plan'].title()}\'"
            if selection['period'] != 'all':
                q1_1, q1_2 = query_one.split("d1.date",1)
                sql_col = "d1.year, d1."+viewership_period_dict[selection['period']]
                q1_1 += sql_col
                query_one = q1_1 + q1_2
                query_three = "GROUP BY " + sql_col
                query_three += " ORDER BY "+ sql_col 
                idx_0, idx_1 = 1, 2
                  
            query = query_one + query_two + query_three
            views = list(map(list, zip(*pg.query_db(query))))
            if not views:
                viewership_fact["labels"] = []
                viewership_fact["data"] = []
                return render_template('viewership.html', data=viewership_fact, selection=selection, options=options)
            
            allowable_chart_size = 40
            if len(views[idx_0]) >= allowable_chart_size:
                if type(views[idx_0][idx_0]) == int:
                    step  = len(views[idx_0])//allowable_chart_size
                    viewership_fact["labels"] = [i for i in views[idx_0]][::step]
                    viewership_fact["data"] = views[idx_1][::step]
                else:
                    step  = len(views[idx_0])//allowable_chart_size
                    viewership_fact["labels"] = [datetime.datetime.strftime(i, "%d/%m/%Y") for i in views[idx_0]][::step]
                    viewership_fact["data"] = views[idx_1][::step]

            else:
                if type(views[idx_0][0]) == int:
                    viewership_fact["labels"] = [i for i in views[idx_0]][::1]  
                    viewership_fact["data"] = views[idx_1][::1]                  
                else:
                    viewership_fact["labels"] = [datetime.datetime.strftime(i, "%d/%m/%Y") for i in views[idx_0]][::1]
                    viewership_fact["data"] = views[idx_1][::1]
            
            print(viewership_fact["labels"])
            return render_template('viewership.html', data=viewership_fact, selection=selection, options=options)

    else:
        query = 'SELECT d1.date, SUM(f.view_duration) FROM viewership_fact f, date_dim d1  WHERE f.date_key = d1.date_key GROUP BY d1.date ORDER BY d1.date DESC;'
        views = list(map(list, zip(*pg.query_db(query))))
        viewership_fact["labels"] = [datetime.datetime.strftime(i, "%d/%m/%Y") for i in views[0]][:30][::-1]
        viewership_fact["data"] = views[1][:30][::-1]

    return render_template('viewership.html', data=viewership_fact, selection=selection, options=options)

@app.route("/categorical", methods=['GET', 'POST'])
def categorical():
    global categorical_selection, categorical_query
    if request.method == 'POST':
        if request.form.get('submit-button') == 'Submit':
            categorical_selection['period'] = request.form['period']
            categorical_selection['y_axis'] = request.form['y_axis']
            categorical_selection['x_axis'] = request.form['x_axis']
            categorical_selection['start_date'] = request.form['start_date']
            
    period_index = categorical_options['period'].index(categorical_selection['period'])
    y_axis_index = categorical_options['y_axis'].index(categorical_selection['y_axis'])
    x_axis_index = categorical_options['x_axis'].index(categorical_selection['x_axis'])
    
    period = categorical_query['period'][period_index]
    y_axis = categorical_query['y_axis'][y_axis_index]
    x_axis = categorical_query['x_axis'][x_axis_index]
    start_date = categorical_selection['start_date'] 
    
    query = f"SELECT d2.{x_axis['column']} AS {x_axis['name']}, {y_axis} AS total FROM viewership_fact f, date_dim d1, {x_axis['table']} d2 WHERE f.date_key = d1.date_key AND f.{x_axis['key']} = d2.{x_axis['key']} AND d1.date >= DATE \'{start_date}\' AND d1.date <= DATE \'{start_date}\' + INTERVAL \'{period}\' GROUP BY {x_axis['column']} ORDER BY total DESC;"
    views = list(map(list, zip(*pg.query_db(query))))
    categorical_data["labels"] = views[0]
    categorical_data["data"] = views[1]
    categorical_data['label'] = categorical_selection['y_axis']
    categorical_data['title'] = f"{categorical_selection['y_axis'].title()} per {categorical_selection['x_axis'].title()}"
    
    print(query)
    return render_template('categorical.html', data=categorical_data, selection=categorical_selection, options=categorical_options)

@app.route("/customquery", methods=['GET', 'POST'])
def customquery():
    if request.method == 'POST':
        if request.form.get("submit-button") == "Query":
            filter_list = []
            sort_string = ''
            sort_by_string = ''
            for col_key, default_val in custom_query_default.items():
                filters_val = []
                formatted_filter = ''
                if not request.form.getlist(col_key):
                    filters_val= default_val
                else:
                    filters_val = request.form.getlist(col_key)

                if not col_key in custom_query_query['filter']:
                    ## These are sortby and sort
                    if col_key == 'sort_by':
                        sort_by_string = custom_query_query['filter'][filters_val[0]]
                    elif col_key == 'sort':
                        sort_string = filters_val[0]
                    continue

                ## Selection
                table_col = custom_query_query['filter'][col_key]

                ## Accounting for period
                if col_key == 'period':
                    formatted_filter = f"{table_col} >= DATE '2022-10-22' - INTERVAL \'{filters_val[0]}\'"                  
                    filter_list.append(formatted_filter)
                    continue

                if type(filters_val) == list:
                    if 'ALL' in filters_val:
                        continue
                    else:
                        if len(filters_val) == 1:
                            ## to deal with kids' tv >:( apostrophe throws error
                            if filters_val[0].find('\'') != -1:
                                filters_val[0] = filters_val[0].replace('\'','\'\'')
                            formatted_filter = f"{table_col} = \'{filters_val[0]}\'"
                        else:
                            for i in range(len(filters_val)):
                                if filters_val[i].find('\'') != -1:
                                    filters_val[i] = filters_val[i].replace('\'','\'\'')
                            filters_val = str(tuple(filters_val)).replace("\"","\'")
                            formatted_filter = f"{table_col} IN {filters_val}"
                        filter_list.append(formatted_filter)
                else:
                    print("Error with type received from drop down")

            ## Querying DB
            table_string = ', '.join(str(val) for val in custom_query_query['table'])
            selection_string = ', '.join(str(val) for val in custom_query_query['selection'])
            join_string = " and ".join(str(val) for val in custom_query_query['join_conditions'])
            filter_string = " and ".join(str(val) for val in filter_list)

            query = f"SELECT {selection_string} FROM {table_string} WHERE {join_string} AND {filter_string} ORDER BY {sort_by_string} {sort_string};"
            output = pg.query_db(query)

            if len(output) == 0:
                print("this is output:" , output)
                flash('No data found for query!')
                return render_template('customquery.html', options=custom_query_options)
                #return redirect(url_for('customquery'))

            ## Writing Files
            file_name = "result.csv"
            csv_file = [custom_query_query['csv_header']]
            for row in output:
                tmp = [str(row_string) for row_string in row] 
                csv_file.append(tmp)

            dest = io.StringIO()
            writer = csv.writer(dest)
            for row in csv_file:
                writer.writerow(row)
            
            response = make_response(dest.getvalue())
            cd = "attachment; filename="+file_name
            response.headers['Content-Disposition'] = cd
            response.mimetype="test/csv"
            return response
    else:
        return render_template('customquery.html', options=custom_query_options)


if __name__ == "__main__":
    app.run(debug=True)
    print("Closing db...")
    pg.close()
    print("DB closed.")
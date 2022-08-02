import random
from hashlib import md5
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import datetime

app = Flask(__name__,
            static_folder="css")

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='project',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def hello():
    return render_template('index.html')



@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register_auth', methods=['GET', 'POST'])
def register_auth():
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    building_number = request.form['building_number']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    phone_number = request.form['phone_number']
    passport_number = request.form['passport_number']
    passport_expiration = request.form['passport_expiration']
    passport_country = request.form['passport_country']
    date_of_birth = request.form['date_of_birth']

    print(password)

    # print((email, name, password, building_number, street, city, state,
    #        phone_number, passport_number, passport_expiration, passport_country,
    #        date_of_birth))

    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, email)

    data = cursor.fetchone()
    # #use fetchall() if you are expecting more than 1 data row
    error = None
    if data:
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = 'INSERT INTO customer VALUES(%s, %s, MD5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, name, password, building_number, street, city, state
                             , phone_number, passport_number, passport_expiration, passport_country
                             , date_of_birth))
        conn.commit()
        cursor.close()
        return render_template('index.html')

@app.route('/public_result', methods = ['GET', 'POST'])
def public_result(): 
    # 1search flight public
    cursor = conn.cursor()
    dep = request.form["dep"]
    arr = request.form["arr"]
    sdate = request.form["sdate"]
    edate = request.form["edate"]
    query = "SELECT airline_name, flight_number,dep_date_time, arr_date_time, dept_airport, arr_airport, DEP.NAME as 'Departure Airport', ARR.NAME as 'Arrival Airport'" \
            "FROM flight JOIN airport as dep on flight.dept_airport=dep.code JOIN airport as ARR on flight.arr_airport=arr.code " \
            "WHERE (flight.dept_airport= %s OR DEP.city = %s) AND (flight.arr_airport= %s OR arr.city = %s) AND dep_date_time > %s AND dep_date_time < %s"
    cursor.execute(query, (dep, dep, arr, arr, sdate, edate))
    pub_search = cursor.fetchall()
    cursor.close()
    return render_template('pub_result.html', pub_search=pub_search)

@app.route('/register_staff')
def register_staff():
    return render_template('register_staff.html')


@app.route('/register_auth_staff', methods=['GET', 'POST'])
def register_auth_staff():
    username = request.form['username']
    password = request.form['password']
    f_name = request.form['f_name']
    l_name = request.form['l_name']
    birth_date = request.form['birth_date']
    airline_name = request.form['airline_name']
    phone = request.form['phone']


    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, username)

    data = cursor.fetchone()
    # #use fetchall() if you are expecting more than 1 data row
    error = None
    if data:
        error = "This user already exists"
        return render_template('register_staff.html', error=error)
    else:
        ins = 'INSERT INTO airline_staff VALUES(%s, MD5(%s), %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, f_name, l_name, birth_date, airline_name, phone))
        conn.commit()
        cursor.close()
        return render_template('index.html')


@app.route('/login_auth', methods=['GET', 'POST'])
def login_auth():
    user = request.form["user"]
    password = request.form["password"]
    option = request.form.get('option')
    # print(option)


    cursor = conn.cursor()
    if option == 'customer':
        query = 'SELECT * FROM customer WHERE email = %s and PASSWORD = MD5(%s)'
    if option == 'staff':
        query = 'SELECT * FROM airline_staff WHERE username = %s and PASSWORD = MD5(%s)'
    cursor.execute(query, (user, password))
    data = cursor.fetchone()
    cursor.close()

    error = None
    if data and option == 'customer':
        cursor = conn.cursor()
        query = 'SELECT NAME FROM customer WHERE email = %s'
        cursor.execute(query, user)
        data = cursor.fetchone()
        cursor.close()
        name = data["NAME"]
        session['name'] = name
        session['email'] = user
        # print(session)
        return redirect(url_for('home_customer'))
    elif data and option == 'staff':
        cursor = conn.cursor()
        query = 'SELECT f_name, l_name FROM airline_staff WHERE username = %s'
        cursor.execute(query, user)
        data = cursor.fetchone()
        name = data['f_name'] + data['l_name']
        cursor.close()
        session['name'] = name
        session['uname'] = user
        cursor = conn.cursor()
        query = "SELECT airline_name FROM airline_staff WHERE username = %s"
        cursor.execute(query, user)
        airline_name = cursor.fetchone()['airline_name']
        session['airline_name'] = airline_name
        return redirect(url_for('home_staff'))
    else:
        return render_template('login.html', error='Invalid login or username')


@app.route('/home_customer')
def home_customer():
    username = session['name']
    email = session['email']

    option = request.form.get('future_past')
    # print(option)

    cursor = conn.cursor()

    # future flights of this customer
    query = "SELECT * " \
            "FROM (ticket NATURAL JOIN flight)" \
            "WHERE dep_date_time >= now() AND email = %s"

    cursor.execute(query, email)
    data1 = cursor.fetchall()

    # all the future flights
    query = "SELECT * " \
            "FROM flight " \
            "WHERE dep_date_time >= now()"

    cursor.execute(query)
    data2 = cursor.fetchall()

    session["all_future_flights"] = data2

    # all the past flights
    query = "SELECT * " \
            "FROM ticket " \
            "WHERE dep_date_time < now() AND email = %s"

    cursor.execute(query, email)
    data3 = cursor.fetchall()

    # past flights of this customer
    query = "SELECT * " \
            "FROM (ticket NATURAL JOIN flight) " \
            "WHERE dep_date_time < now() AND email = %s"

    cursor.execute(query, email)
    data4 = cursor.fetchall()

    # last year spending
    query = "SELECT SUM(sold_price) AS Total_Spent " \
            "FROM ticket " \
            "WHERE email  = %s AND purchase_date_time >= DATE_SUB(NOW(), INTERVAL 1 YEAR)"

    cursor.execute(query, email)
    data5 = cursor.fetchall()

    print(data5)

    # last 6 month separate
    query = "SELECT MONTH(purchase_date_time) AS mn,SUM(sold_price) AS spent " \
            "FROM ticket " \
            "WHERE email=%s AND " \
            "adddate(purchase_date_time, INTERVAL 6 MONTH)>now() GROUP BY mn;"

    cursor.execute(query, email)
    data6 = cursor.fetchall()
    print(data6)

    cursor.close()
    return render_template('home_customer.html', username=username, future_flights=data1,
                           future_flights_all=data2, past_flights=data3, customer_past_flights=data4,
                           last_year_spending=data5, last_6_month_spending=data6)

@app.route('/cust_result', methods=['POST'])
def cust_result():
    # 1search flight cust
    cursor = conn.cursor()
    dep = request.form["dep"]
    arr = request.form["arr"]
    sdate = request.form["sdate"]
    edate = request.form["edate"]
    query = "SELECT airline_name, flight_number,dep_date_time, arr_date_time, dept_airport, arr_airport, DEP.NAME as 'Departure Airport', ARR.NAME as 'Arrival Airport'" \
            "FROM flight JOIN airport as dep on flight.dept_airport=dep.code JOIN airport as ARR on flight.arr_airport=arr.code " \
            "WHERE (flight.dept_airport= %s OR DEP.city = %s) AND (flight.arr_airport= %s OR arr.city = %s) AND dep_date_time > %s AND dep_date_time < %s"
    cursor.execute(query, (dep, dep, arr, arr, sdate, edate))
    cust_search = cursor.fetchall()
    cursor.close()
    return render_template('cust_result.html', cust_search=cust_search)

@app.route('/spent', methods=['GET', 'POST'])
def spent():
    email = session['email']
    begin_time = request.form["begin_time"]
    end_time = request.form["end_time"]
    cursor = conn.cursor()
    query = "SELECT SUM(sold_price) AS Total_Spent " \
            "FROM ticket " \
            "WHERE email  = %s AND purchase_date_time > %s AND purchase_date_time < %s"

    cursor.execute(query, (email, begin_time, end_time))

    spent_total = cursor.fetchall()
    print(spent_total, 12345)

    query = "SELECT MONTH(purchase_date_time) AS mn,SUM(sold_price) AS spent," \
            " YEAR(purchase_date_time) AS yr " \
            "FROM ticket " \
            "WHERE email=%s " \
            "AND purchase_date_time > %s AND purchase_date_time < %s GROUP BY mn"
    cursor.execute(query, (email, begin_time, end_time))
    spent_per_month = cursor.fetchall()
    return render_template('spent.html', spent_total=spent_total, spent_per_month=spent_per_month)


@app.route('/customer_search', methods=['GET', 'POST'])
def customer_search():
    email = session['email']
    begin_time = request.form["begin_time"]
    end_time = request.form["end_time"]
    cursor = conn.cursor()
    query = "SELECT * " \
            "FROM (ticket NATURAL JOIN flight)" \
            "WHERE email  = %s AND dep_date_time > %s AND dep_date_time < %s"

    cursor.execute(query, (email, begin_time, end_time))
    customer_past_flights = cursor.fetchall()
    return render_template('customer_search.html', customer_past_flights=customer_past_flights)


@app.route('/cancel', methods=['GET', 'POST'])
def cancel_ticket():
    username = session['name']
    cursor = conn.cursor()
    drop_id = request.form.getlist("check")
    # print(drop_id)
    for ticket_id in drop_id:
        query = "DELETE FROM ticket WHERE ticket_id=%s"
        cursor.execute(query, ticket_id)
    conn.commit()
    cursor.close()
    return redirect(url_for('home_customer'))


@app.route('/comment', methods=['GET', 'POST'])
def comment():
    email = session['email']
    cursor = conn.cursor()
    comments = request.form.get("comments")
    rating = request.form.get("star")
    flight_info = request.form.get("info").split('_')
    airline_name = flight_info[0]
    flight_number = flight_info[1]
    dep_date_time = flight_info[2]
    # print(comments, rating, flight_info)
    query = "INSERT INTO rate_comment VALUES(%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (airline_name, flight_number, dep_date_time, email, rating, comments))
    cursor.close()
    return redirect(url_for('home_customer'))


@app.route('/purchase', methods=['GET', 'POST'])
def purchase_ticket():
    username = session['name']
    all_future = session['all_future_flights']

    check = request.form.getlist("check")
    # print(check)
    email = session['email']
    card_type = request.form.get('card_type')
    card_number = request.form['card_number']
    name_on_card = request.form['name_on_card']
    exp_date = request.form['exp_date']
    travel_class_list = request.form.getlist('travel_class')

    # print(travel_class)

    exp_date = exp_date[-2:] + '/' + exp_date[-5:-3]

    cursor = conn.cursor()
    for item in check:
        index = int(item)
        travel_class = travel_class_list[index]
        airline_name = all_future[index]["airline_name"]
        flight_number = all_future[index]["flight_number"]
        dep_date_time = all_future[index]["dep_date_time"]
        base_price = all_future[index]["base_price"]
        if travel_class == "economy class":
            sold_price = base_price
        elif travel_class == "business class":
            sold_price = base_price*2
        elif travel_class == "first class":
            sold_price = base_price*3
        username = session['name']
        query = "select (MAX(ticket_ID)+1) AS new_id from ticket"
        cursor.execute(query)
        temp = cursor.fetchall()
        if temp[0]['new_id'] is None:
            ticket_id = '1'
        else:
            ticket_id = temp[0]['new_id']

        # print(sold_price, airline_name, dep_date_time, base_price)
        query = "INSERT INTO ticket VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (ticket_id, email, airline_name, flight_number, dep_date_time,
                               travel_class, sold_price, card_type, card_number, name_on_card,
                               exp_date, datetime.datetime.now()))
    conn.commit()
    cursor.close()
    return redirect(url_for('home_customer'))

@app.route('/pub_status', methods=['GET', 'POST'])
def pub_status(): 
    cursor = conn.cursor()
    airline_name = request.form['airline']
    dep = request.form['dep']
    num = request.form['flight']
    query = "SELECT *" \
            "FROM flight " \
            "WHERE airline_name = %s AND dep_date_time = %s AND flight_number = %s"
    cursor.execute(query, (airline_name, dep, num))
    pub_st = cursor.fetchall()
    cursor.close()
    return render_template('pub_result.html', pub_st=pub_st)

@app.route('/home_staff')
def home_staff():
    username = session['uname']
    name = session['name']
    airline_name = session["airline_name"]

    cursor = conn.cursor()

    # Default: View Flights
    query = "SELECT airline_name, flight_number,dep_date_time, dept_airport, arr_airport, status" \
            " FROM flight " \
            "WHERE airline_name = %s AND flight.dep_date_time > now() AND flight.dep_date_time < DATE_ADD(now(),INTERVAL 30 year)"
    cursor.execute(query, airline_name)
    s1default = cursor.fetchall()
    cursor.close()
    cursor = conn.cursor()
    # most frequent customer
    query = """ SELECT MAX(freq) as mfreq, email
                FROM
                (SELECT count(email) AS freq, email
                FROM ticket
                WHERE dep_date_time > now() AND dep_date_time>subdate(now(),interval 1 year) AND airline_name = %s
                GROUP BY email) AS freq_count"""
    cursor.execute(query, airline_name)
    freq = cursor.fetchall()
    cursor.close()
    cursor = conn.cursor()
    query = """SELECT *
                FROM ticket
                WHERE email = %s
                AND 
                airline_name=%s"""
    if (freq[0]['email']):
        cursor.execute(query, (freq[0]['email'], airline_name))
        freq_trips = cursor.fetchall()
    else:
        freq_trips = [{'ticket_id': 'No Tickets'}]

    cursor = conn.cursor()
    query = """SELECT SUM(sold_price) AS lastmonth 
                FROM ticket 
                WHERE purchase_date_time < now() AND DATE_ADD(purchase_date_time,INTERVAL 1 month) > now()"""
    cursor.execute(query)
    lastmonth = cursor.fetchall()
    cursor.close()
    cursor = conn.cursor()
    query = """SELECT SUM(sold_price) AS lastyear 
                FROM ticket 
                WHERE purchase_date_time < now() AND DATE_ADD(purchase_date_time,INTERVAL 1 year) > now()"""
    cursor.execute(query)
    lastyear = cursor.fetchall()
    cursor.close()

    cursor = conn.cursor()
    query = """SELECT arr_airport, count(*) 
                FROM ticket natural join flight
                WHERE dep_date_time<now() and adddate(dep_date_time,interval 3 month) >now() 
                GROUP BY arr_airport 
                ORDER BY count(*) DESC 
                LIMIT 3;"""
    cursor.execute(query)
    top3month = cursor.fetchall()
    cursor.close()

    cursor = conn.cursor()
    query = """SELECT arr_airport, count(*) 
                FROM ticket natural join flight
                WHERE dep_date_time<now() and adddate(dep_date_time,interval 1 year) >now() 
                GROUP BY arr_airport 
                ORDER BY count(*) DESC 
                LIMIT 3;"""
    cursor.execute(query)
    top3year = cursor.fetchall()
    cursor.close()

    # Update Flight
    # query = "SELECT flight"
    return render_template('home_staff.html', name=name, username=username, airline_name=airline_name,
                           s1default=s1default, freq=freq, freq_trips=freq_trips, lastyear=lastyear,
                           lastmonth=lastmonth, top3month=top3month, top3year=top3year)


@app.route('/staff_result', methods=['POST'])
def staff_result():
    # 1search flight
    airline = session["airline_name"]
    cursor = conn.cursor()
    dep = request.form["dep"]
    arr = request.form["arr"]
    sdate = request.form["sdate"]
    edate = request.form["edate"]
    query = "SELECT airline_name, flight_number,dep_date_time, dept_airport, arr_airport, DEP.NAME as 'Departure Airport', ARR.NAME as 'Arrival Airport'" \
            "FROM flight JOIN airport as dep on flight.dept_airport=dep.code JOIN airport as ARR on flight.arr_airport=arr.code " \
            "WHERE (flight.dept_airport= %s OR DEP.city = %s) AND (flight.arr_airport= %s OR arr.city = %s) AND dep_date_time > %s AND dep_date_time < %s AND flight.airline_name=%s"
    cursor.execute(query, (dep, dep, arr, arr, sdate, edate, airline))
    s1search = cursor.fetchall()
    cursor.close()
    return render_template('staff_result.html', s1search=s1search)


@app.route('/new_flight', methods=['GET', 'POST'])
def new_flight():
    airline_name = session['airline_name']

    cursor = conn.cursor()
    flight_number = request.form["flight_number"]
    dep_date_time = request.form["dep_datetime"]
    dep_airport = request.form["dep_airport"]
    arr_airport = request.form["arr_airport"]
    arr_date_time = request.form["arr_datetime"]
    base_price = request.form["base_price"]
    plane_id = request.form["plane_id"]
    status = request.form["status"]
    query = "INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (
    airline_name, flight_number, dep_date_time, dep_airport, arr_airport, arr_date_time, base_price, plane_id, status))
    conn.commit()
    cursor.close()
    return redirect(url_for('home_staff'))


@app.route('/update_flight', methods=['GET', 'POST'])
def update_flight():
    username = session['uname']
    airline_name = session['airline_name']

    cursor = conn.cursor()
    flight_number = request.form["flight_number"]
    dep_date_time = request.form["dept_date"]
    status = request.form["status"]

    query = """UPDATE flight SET STATUS = %s
            WHERE flight_number = %s and airline_name= %s and dep_date_time=%s"""
    cursor.execute(query, (status, flight_number, airline_name, dep_date_time))
    conn.commit()
    cursor.close()
    return redirect(url_for('home_staff'))


@app.route('/new_plane', methods=['GET', 'POST'])
def new_plane():
    airline_name = session['airline_name']

    cursor = conn.cursor()
    airplane_id = request.form["airplane_id"]
    seat_number = request.form["seat"]
    manufacturer = request.form["Manufacturer"]
    age = request.form["age"]
    query = """insert into airplane
                values
                (%s, %s, %s, %s, %s)
                """
    cursor.execute(query, (airline_name, airplane_id, seat_number, manufacturer, age))
    cursor.close()
    return redirect(url_for('home_staff'))


@app.route('/new_port', methods=['GET', 'POST'])
def new_port():
    cursor = conn.cursor()
    code = request.form["code"]
    name = request.form["name"]
    city = request.form["city"]
    country = request.form["country"]
    type = request.form["type"]
    query = """insert into airport
                values(%s, %s, %s, %s, %s)"""
    cursor.execute(query, (code, name, city, country, type))
    cursor.close()
    return redirect(url_for('home_staff'))


@app.route('/rate_result', methods=['GET', 'POST'])
def rate_result():
    airline_name = session["airline_name"]
    cursor = conn.cursor()

    dep = request.form["dep_datetime"]
    num = request.form["flight_number"]
    query = """ SELECT   
                        flight_number, 
	                    dep_date_time, 
                        rate, 
                        comment
                FROM rate_comment
                WHERE
                    airline_name=%s AND flight_number=%s AND dep_date_time=%s
"""
    cursor.execute(query, (airline_name, num, dep))
    
    rate = cursor.fetchall()
    avg = 0
    cnt = 0
    for line in rate: 
        print(line['rate'])
        avg += int(line['rate'])
        cnt += 1
    avg = avg / cnt
    cursor.close()
    return render_template('rate_result.html', rate=rate, avg = avg)


@app.route('/reports', methods=['GET', 'POST'])
def reports():
    airline = session['airline_name']
    large = request.form["edate"]
    small = request.form["sdate"]
    # print(small, large)
    cursor = conn.cursor()
    query = """ SELECT COUNT(ticket_ID) AS cnt
                FROM ticket 
                WHERE purchase_date_time<%s AND purchase_date_time>%s AND airline_name = %s"""
    cursor.execute(query, (large, small, airline))
    report = cursor.fetchall()

    cursor = conn.cursor()
    query = """SELECT year(purchase_date_time) as year, month(purchase_date_time) as mn, COUNT(ticket_ID) as cnt
                FROM ticket
                WHERE purchase_date_time<%s AND purchase_date_time>%s AND airline_name = %s
                GROUP BY mn"""
    cursor.execute(query, (large, small, airline))
    reportmn = cursor.fetchall()
    cursor.close()
    return render_template('report.html', report=report, reportmn=reportmn)


@app.route('/revenue_class', methods=['GET', 'POST'])
def revenue_class():
    cursor = conn.cursor()
    rclass = request.form["class"]
    query = """SELECT SUM(sold_price) AS "byclass", travel_class 
    FROM ticket 
    WHERE travel_class = %s"""
    cursor.execute(query, rclass)
    byclass = cursor.fetchall()
    cursor.close()
    return render_template('byclass.html', byclass=byclass)


@app.route('/everyone', methods=['GET', 'POST'])
def everyone():
    airline = session['airline_name']
    cursor = conn.cursor()
    num = request.form['flight']
    date = request.form['date']
    query = """SELECT customer.NAME, customer.email 
    FROM ticket NATURAL JOIN customer 
    WHERE flight_number =%s AND airline_name = %s AND dep_date_time = %s AND purchase_date_time < %s"""
    cursor.execute(query, (num, airline, date, date))
    every = cursor.fetchall()
    print(every)
    cursor.close()
    return render_template('everyone.html', every=every)


@app.route('/logout_customer')
def logout_customer():
    session.pop('name')
    session.pop('email')
    return redirect('/')


@app.route('/logout_staff')
def logout_staff():
    session.pop('name')
    session.pop('uname')
    session.pop('airline_name')
    return redirect('/')


app.secret_key = '7270600ff6243e7cf10c504ba767c933'  # MD5: database_project

if __name__ == "__main__":
    app.run('localhost', 5000, debug=True)

# AirlineDB

A Flask-based airline reservation and management application built around a MySQL database. The project supports both customer-facing booking workflows and airline-staff administrative tasks, including flight searches, ticket purchases, cancellations, ratings, and operational reporting.

## Overview

This application simulates a simplified airline system with two user types:

- Customers can register, log in, search flights, buy tickets, cancel reservations, view spending history, and submit comments/ratings.
- Airline staff can register, log in, manage flights and aircraft, add airports, update flight status, review customer activity, and generate reports.

The app uses Flask for the web layer and PyMySQL to communicate with a MySQL database named `project`.

---

## Features

### Customer Features

- Customer registration and login
- Flight search by departure/arrival and date range
- Ticket purchase with seat class selection
- Ticket cancellation
- View upcoming and past flights
- Spending summaries for the last year and last 6 months
- Custom date-range customer trip search
- Flight rating and commenting

### Staff Features

- Staff registration and login
- Airline-specific staff dashboard
- View upcoming flights for the airline
- Search flights for a specific airline
- Add new flights
- Update flight status
- Add new airplanes
- Add new airports
- Review customer frequency and travel data
- Revenue and reporting views by date range
- View airline-specific ratings and comments

### Public Features

- Public flight status and search pages
- Airport/flight queries without logging in

---

## Tech Stack

- Python 3
- Flask
- PyMySQL
- MySQL
- Jinja2 templates
- HTML/CSS

---

## Project Structure

```text
AirlineDB/
├── project.py              # Main Flask app and route definitions
├── css/                    # Static CSS files
├── templates/              # HTML templates for views
├── list-of-file.txt        # File listing for the project
├── summary of work.pdf     # Project summary document
├── final sql with comment.pdf  # SQL documentation/reference
└── README.md               # Project documentation
```

---

## Prerequisites

Before running the project, make sure you have:

- Python 3.8+ installed
- MySQL Server installed and running locally
- A MySQL database named `project`
- The required schema/tables created in the database
- A MySQL user with access to the database

---

## Database Configuration

The application connects to MySQL using the following default settings in `project.py`:

```python
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='project',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
```

If your local MySQL setup uses a different username, password, or database name, update these values in `project.py` before running the server.

> The app assumes a database schema that contains tables such as `customer`, `airline_staff`, `flight`, `airport`, `ticket`, `rate_comment`, and `airplane`.

---

## Python Dependencies

Install the required packages with:

```bash
pip install flask pymysql
```

If you use a virtual environment, activate it first and then run the command above.

---

## Running the Application

From the project root, start the app with:

```bash
python project.py
```

Then open the following in your browser:

```text
http://localhost:5000/
```

The app runs with debug mode enabled:

```python
if __name__ == "__main__":
    app.run('localhost', 5000, debug=True)
```

---

## Main Routes

The Flask app defines the following major routes:

### Public Routes

- `/` — home page
- `/login` — customer/staff login page
- `/register` — customer registration
- `/register_staff` — staff registration
- `/public_result` — public flight search results

### Customer Routes

- `/login_auth` — login handler for customer/staff
- `/home_customer` — customer dashboard
- `/cust_result` — customer flight search results
- `/purchase` — ticket purchase flow
- `/cancel` — cancel tickets
- `/comment` — submit flight comments/ratings
- `/spent` — spending analytics
- `/customer_search` — search past flights by date range
- `/logout_customer` — customer logout

### Staff Routes

- `/home_staff` — staff dashboard
- `/staff_result` — airline flight search results
- `/new_flight` — add new flight
- `/update_flight` — update flight status
- `/new_plane` — add airplane information
- `/new_port` — add airport information
- `/rate_result` — review customer ratings
- `/reports` — report generation
- `/revenue_class` — revenue by service class
- `/everyone` — list passengers on a flight
- `/logout_staff` — staff logout

---

## Typical User Workflow

### Customer Workflow

1. Register a new customer account.
2. Log in with the email and password.
3. Search for flights.
4. Select a flight and class.
5. Enter payment details and purchase a ticket.
6. Review future/past flights and spending history.
7. Leave a rating/comment for a completed flight.

### Staff Workflow

1. Register as airline staff.
2. Log in to the airline dashboard.
3. View airline flights and current analytics.
4. Add a new flight, plane, or airport.
5. Update flight status as needed.
6. Review customer ticket and revenue data.
7. Downstream reporting and rating analysis.

---

## Notes and Caveats

- This app is an academic exercise. It does not, and should never, be used in a customer-facing production environment.
- The app uses a hardcoded secret key!
- The app is configured for local development and does not include environment management, Docker configuration, or deployment scaffolding.
- SQL queries are written against a specific database schema; if your schema differs, you may need to adjust field names or table names.
- Some queries rely on MySQL date functions and conditional logic, so compatibility with other database engines is limited.

---

## Possible Improvements

- Move database credentials to environment variables
- Add input validation and form sanitization
- Enhance session authorization checks
- Add error handling for database failures
- Split the app into modular blueprints for cleaner maintenance
- Add unit/integration tests
- Improve UI consistency and responsive design

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Project Status

This is a database-driven web application for an airline ticketing and operations workflow. It is suitable for coursework, prototype demos, or learning how to integrate Flask with MySQL and implement role-based application features.

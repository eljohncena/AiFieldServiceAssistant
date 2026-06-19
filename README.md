AI Field Service Assistant

AI Field Service Assistant is a backend API project built with FastAPI, SQLAlchemy, and SQLite. The project simulates a field service operations system where users can view work orders, technicians, job sites, and dashboard summary data.

The current version focuses on backend development fundamentals such as API routing, database models, seeded data, filtering, and basic dashboard metrics. Future versions will include route optimization using the Google Maps API, route caching, AI-assisted dispatch recommendations, a frontend dashboard, and deployment.

Project Goal

The goal of this project is to build a field service assistant that can help organize and analyze work orders for technicians in different locations.

I wanted to create a project that connects software engineering with a real-world operations problem: assigning and tracking field service work. This project is inspired by field service workflows where teams need to manage work orders, technician coverage areas, site locations, priorities, safety escalations, and SLA deadlines.

Current Project Status

This project is currently in progress.

The backend API is working locally and currently supports:

* Viewing all work orders
* Filtering work orders by different fields
* Viewing individual work orders
* Viewing technicians
* Viewing individual technicians
* Viewing a basic dashboard summary
* Checking database record counts

The AI, routing optimization, frontend, and deployment features are planned future improvements.

Tech Stack

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Uvicorn

Current Features

Work Order API

The application includes a /work-orders endpoint that returns all work orders from the database.

Work orders include fields such as:

* Work order ID
* Customer
* Site ID
* Issue
* Technician
* Status
* Priority
* Created date
* Safety escalation
* City
* State
* SLA status

Example:

GET /work-orders

Work Order Filtering

The /work-orders endpoint supports query parameters so the user can filter work orders by specific values.

Current filters include:

* Status
* Priority
* City
* State
* Technician
* SLA status
* Safety escalation
* Site ID

Examples:

GET /work-orders?status=Open
GET /work-orders?priority=P1
GET /work-orders?city=Raleigh
GET /work-orders?site_id=002

This helped me practice using FastAPI query parameters and SQLAlchemy filtering.

Single Work Order Lookup

A specific work order can be viewed using its work order ID.

Example:

GET /work-orders/1001

This route is useful for looking up the details of one specific job.

Dashboard Summary

The /dashboard endpoint returns a basic summary of work order data.

The dashboard currently shows:

* Total work orders
* Open work orders
* In-progress work orders
* Closed work orders
* Overdue work orders
* Due soon work orders
* Safety escalations
* P1 priority work orders

Example:

GET /dashboard

This endpoint is meant to support a future frontend dashboard with summary cards.

Technician API

The project also includes technician endpoints.

View all technicians:

GET /technicians

View one technician:

GET /technicians/1

These endpoints are part of the foundation for future technician assignment and dispatch logic.

Database Test Endpoint

The /db-test endpoint checks that the database connection is working and returns record counts for the main tables.

Example:

GET /db-test

Example response:

{
  "work_orders": 10,
  "technicians": 5,
  "sites": 5
}

API Routes

Method	Route	Description
GET	/	Home route
GET	/health	Health check
GET	/work-orders	View and filter work orders
GET	/work-orders/{work_order_id}	View a single work order
GET	/dashboard	View dashboard summary data
GET	/technicians	View all technicians
GET	/technicians/{technician_id}	View a single technician
GET	/db-test	Test database connection and record counts

How to Run the Project Locally

From the backend folder, run:

uvicorn main:app --reload

Then open:

http://127.0.0.1:8000

FastAPI automatically provides interactive API documentation at:

http://127.0.0.1:8000/docs

Example Use Cases

This project could eventually support field service workflows such as:

* Viewing all open work orders
* Filtering urgent P1 or P2 work orders
* Checking which work orders have safety escalations
* Looking up work orders by city or state
* Finding work orders assigned to a specific technician
* Reviewing dashboard metrics for field service operations
* Planning technician routes to job sites
* Recommending technicians based on location, priority, and SLA urgency

Planned Roadmap

1. Google Maps API Integration

The next major feature I plan to add is Google Maps API integration.

The goal is to calculate travel distance and estimated drive time between technicians and job sites.

This would allow the project to support route-based field service decisions, such as identifying which technician is closest to a job site.

Planned route data includes:

* Technician starting location
* Job site destination
* Distance in miles
* Estimated drive time
* Route calculation timestamp

2. Route Caching

After adding Google Maps API route calculations, I plan to cache route results in storage.

The reason for caching is to avoid making repeated API calls for the same technician-site route. This can help:

* Reduce unnecessary API usage
* Improve response speed
* Store previously calculated routes
* Make the system more efficient

For example, if the application already calculated the distance between a technician and a site, it could reuse that stored result instead of calling the Google Maps API again.

3. 100-Mile Radius Logic

I plan to add logic that checks whether a technician is within a 100-mile radius of a job site.

This would simulate a real field service dispatch rule where technicians may only cover jobs within a certain service area.

Example:

If technician distance from site <= 100 miles:
    technician is eligible for assignment
else:
    technician is outside service range

This feature will help connect the work order data with location-based assignment logic.

4. AI-Assisted Dispatching

Once routing and distance logic are working, I plan to explore AI-assisted dispatch recommendations.

The AI feature would not replace the backend logic. Instead, it would use the data from the application to help recommend which technician may be the best fit for a work order.

Possible factors could include:

* Technician distance from the job site
* Work order priority
* SLA urgency
* Safety escalation status
* Technician availability
* City and state coverage
* Current work order status

The AI portion is a planned future enhancement and is not included in the current version.

5. Frontend Dashboard

I plan to build a frontend so users can interact with the project visually instead of only using API routes.

The frontend could include:

* Work order table
* Search and filter controls
* Dashboard summary cards
* Technician list
* Site details
* Work order detail page
* Route and distance display
* AI recommendation display

This would make the project easier to demo and more useful as a portfolio project.

6. Deployment

After the backend and frontend are more complete, I plan to deploy the project so it can be accessed online.

The deployment step would help me practice moving a local project into a hosted environment.

What I Learned

While building this project, I practiced:

* Creating routes with FastAPI
* Using query parameters
* Filtering database results
* Creating SQLAlchemy models
* Connecting to a local SQLite database
* Seeding sample data
* Debugging API errors
* Reading local server logs
* Testing endpoints in the browser
* Structuring a backend project
* Thinking through future system design improvements

Challenges I Ran Into

Some of the main challenges I worked through were:

* Making sure API routes were registered correctly
* Debugging 404 errors when an endpoint was not being found
* Debugging 500 errors from SQLAlchemy filter issues
* Fixing syntax errors that stopped the server from starting
* Making sure site_id filtering worked correctly
* Understanding how query parameters connect to database filters

These issues helped me better understand how FastAPI, SQLAlchemy, and Uvicorn work together.

Current Limitations

This is still an early version of the project.

Current limitations include:

* No frontend yet
* No user authentication
* No create, update, or delete routes yet
* No Google Maps API integration yet
* No route optimization yet
* No AI recommendation logic yet
* SLA logic is still basic
* The database uses sample/local data
* Error handling can be improved
* Testing is currently manual

Future Improvements

Future improvements include:

* Add POST routes to create new work orders
* Add PUT or PATCH routes to update work orders
* Add DELETE routes for removing work orders
* Add stronger validation with Pydantic schemas
* Add Google Maps API route calculations
* Cache route results in the database
* Add 100-mile technician coverage logic
* Add AI-assisted dispatch recommendations
* Build a frontend dashboard
* Add automated tests
* Deploy the full application

Personal Note:
This project was built as a hands on learning exercise while developing my backend engineering skills. I used AI as a coding assistant throughout — but my focus was on understanding why the code works, not just getting it to run. That meant debugging issues myself, tracing logic through the stack, and thinking through real-world constraints like routing, scheduling conflicts, and API cost management.
This is not a finished production application. It represents my current progress in building APIs, working with databases, and planning realistic features incrementally.

Where it's headed:
The long-term goal is to grow this into a complete field service assistant with route optimization, cached travel data, AI-assisted dispatch recommendations, and a frontend dashboard.

- Key Files & Components under src
  main.py – Entry point for the FastAPI app and routing.
  models.py – Defines SQLAlchemy database models.
  schemas.py – Pydantic models for request validation and serialization.
  routers.py - API gateway/routing and interacting with views layer.
  views.py - API endpoints and interacting with service layer.
  services.py – Contains the business logic for interacting with the database.
  dependencies.py – Common dependencies like database connection and authentication.
  utils.py – Utility functions for predictive analytics, reporting, etc.
  config.py – Configuration file for app settings and environment variables.

- Alembic:
  Alembic setup and generate a migrations folder: alembic init migrations
  inside alembic.ini file comment out the 'sqlalchemy.url =' line
  configure env.py file under migrations folder
  Now run:
  generate migration file: alembic revision --autogenerate -m "Create initial tables"
  apply migration to create tables: alembic upgrade head
  Generate a new migration: alembic revision --autogenerate -m "description"
  downgrade: alembic downgrade -1

######################################

### Backend API Endpoints:

Module:
Auth: for User authentications
/api/v1/auth/signup/
/api/v1/auth/login/
/api/v1/auth/users/me/

Transaction:
/api/v1/transaction/categories
/api/v1/transaction/sub-categories
/api/v1/transaction/create/
/api/v1/transaction/read/{transaction_id}
/api/v1/transaction/update/{transaction_id}
/api/v1/transaction/delete/{transaction_id}
/api/v1/transaction/list/

Budget:
/api/v1/budget/create/
/api/v1/budget/update/{budget_id}
/api/v1/budget/delete/{budget_id}
/api/v1/budget/list/
/api/v1/budget/update/status/{budget_id}

Stat:
/api/v1/stat/periodical-expense/
/api/v1/stat/monthly-expense-of-category/
/api/v1/stat/monthly-income-vs-expense/
/api/v1/stat/monthly-budget-vs-expense

Application description:
User can register in the platform.
Add their Income and Expense Transactions.
Update and Delete Transactions.
Search, Filter, Order Transactions.
Setup budget and keep track of expenses.
If expense exceeds the budget limit then user will get notified.
Various Charts to visualize Expense of categories etc.

Application flow:
User can register in the platform.
Add their Income and Expense transactions.
Setup budget and keep track of expenses.
When a new trasaction added and if the category of the transaction is budgeted,
then send the transaction details to kafka topic by producer and consumer will
consume the message(transaction details) and analysis the budget status.

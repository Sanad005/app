from flask import Flask
from app.db import engine
from app.models import metadata, users, categories, expenses
from sqlalchemy import Float, extract, insert, select, text, update, delete, func, and_,cast
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

metadata.create_all(engine)

# -------------------------------------------------------------------
# Auth Queries
# -------------------------------------------------------------------
def insert_user(name, password_hash, email):
    with engine.connect() as conn:
        try:
            stmt = insert(users).values(
                name=name,
                password_hash=password_hash,
                email=email,
            ).returning(users.c.id)
            result = conn.execute(stmt)
            inserted_id = result.scalar()
            conn.commit()
            return str(inserted_id)
        except SQLAlchemyError:
            conn.rollback()
            return None

# ... all your existing functions ...

def delete_expense(expense_id, user_id):
    """Deletes an expense item by explicitly casting IDs to UUID."""
    print(f"--> ATTEMPTING DELETE: expense_id='{expense_id}', user_id='{user_id}'")
    
    with engine.begin() as conn:
        try:
            stmt = delete(expenses).where(
                and_(
                    expenses.c.id == cast(expense_id, UUID),
                    expenses.c.user_id == cast(user_id, UUID)
                )
            )
            result = conn.execute(stmt)
            print(f"--> SUCCESS: Deleted {result.rowcount} row(s) from database.")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            print(f"--> ERROR during deletion: {e}")
            return False

def search_expenses(user_id, category_id=None, min_amount=None, max_amount=None, start_date=None, end_date=None):
    with engine.connect() as conn:
        try:
            conditions = [expenses.c.user_id == user_id]

            if category_id:
                conditions.append(expenses.c.category_id == category_id)
            if min_amount:
                conditions.append(expenses.c.amount >= float(min_amount))
            if max_amount:
                conditions.append(expenses.c.amount <= float(max_amount))
            if start_date:
                conditions.append(expenses.c.expense_date >= start_date)
            if end_date:
                conditions.append(expenses.c.expense_date <= end_date)

            query = (
                select(expenses, categories.c.name.label("category_name"))
                .select_from(
                    expenses.join(categories, expenses.c.category_id == categories.c.id)
                )
                .where(and_(*conditions))
                .order_by(expenses.c.expense_date.desc())
            )

            result = conn.execute(query).mappings().all()
            return [dict(row) for row in result]
        except SQLAlchemyError:
            return []


# ✅ ADD THIS AT THE END OF main.py
def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-change-me'
    
    @app.route('/')
    def index():
        return {'message': 'Expense Tracker API is running'}
    
    @app.route('/health')
    def health():
        return {'status': 'ok'}
    
    return app
"""
SQLite fallback database module for local development
"""
import sqlite3
import json
import os
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pathlib import Path

# Constants for sorting
ASCENDING = 1
DESCENDING = -1

# Database file location
DB_FILE = os.path.join(os.path.dirname(__file__), 'finance_tracker.db')

def get_db():
    """Get SQLite database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database with required tables"""
    conn = get_db()
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Transactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Budgets table
    c.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            month TEXT NOT NULL,
            category TEXT NOT NULL,
            budget_limit REAL NOT NULL,
            UNIQUE(user_id, month, category),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Create indexes
    c.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, date DESC)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_type ON transactions(user_id, type)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_category ON transactions(user_id, category)')
    
    conn.commit()
    conn.close()

# Initialize database on import
try:
    init_db()
    print("✅ SQLite database initialized successfully")
except Exception as e:
    print(f"Warning: Could not initialize SQLite database: {e}")

# Compatibility functions

def users_col():
    """Mock collection object for users"""
    class UsersCollection:
        def find_one(self, query, projection=None):
            conn = get_db()
            c = conn.cursor()
            if '_id' in query:
                c.execute('SELECT * FROM users WHERE id = ?', (query['_id'],))
            elif 'username' in query:
                c.execute('SELECT * FROM users WHERE username = ?', (query['username'],))
            row = c.fetchone()
            conn.close()
            if not row:
                return None
            result = {'_id': row['id'], 'username': row['username'], 'password_hash': row['password_hash']}
            return result
        
        def insert_one(self, doc):
            conn = get_db()
            c = conn.cursor()
            user_id = str(ObjectId())
            c.execute('INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)',
                     (user_id, doc['username'], doc['password_hash']))
            conn.commit()
            conn.close()
            class InsertResult:
                inserted_id = user_id
            return InsertResult()
        
        def update_one(self, query, update):
            conn = get_db()
            c = conn.cursor()
            user_id = query.get('_id')
            if user_id:
                new_hash = update['$set'].get('password_hash')
                c.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user_id))
                conn.commit()
                matched = c.rowcount
                conn.close()
                class UpdateResult:
                    matched_count = matched
                return UpdateResult()
            conn.close()
            class UpdateResult:
                matched_count = 0
            return UpdateResult()
    
    return UsersCollection()

def transactions_col():
    """Mock collection object for transactions"""
    class TransactionsCollection:
        def find(self, query):
            return TransactionsCursor(query)
        
        def insert_one(self, doc):
            conn = get_db()
            c = conn.cursor()
            trans_id = str(ObjectId())
            c.execute('''INSERT INTO transactions (id, user_id, date, type, category, amount, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (trans_id, doc['user_id'], doc['date'], doc['type'], 
                      doc['category'], doc['amount'], doc.get('description')))
            conn.commit()
            conn.close()
            class InsertResult:
                inserted_id = trans_id
            return InsertResult()
        
        def delete_one(self, query):
            conn = get_db()
            c = conn.cursor()
            c.execute('DELETE FROM transactions WHERE id = ?', (query['_id'],))
            conn.commit()
            deleted = c.rowcount
            conn.close()
            class DeleteResult:
                deleted_count = deleted
            return DeleteResult()
        
        def update_one(self, query, update):
            conn = get_db()
            c = conn.cursor()
            trans_id = query.get('_id')
            if trans_id and '$set' in update:
                update_data = update['$set']
                set_clause = ', '.join([f'{k} = ?' for k in update_data.keys()])
                values = list(update_data.values()) + [trans_id]
                c.execute(f'UPDATE transactions SET {set_clause} WHERE id = ?', values)
                conn.commit()
                matched = c.rowcount
                conn.close()
                class UpdateResult:
                    matched_count = matched
                return UpdateResult()
            conn.close()
            class UpdateResult:
                matched_count = 0
            return UpdateResult()
        
        def create_index(self, fields, **kwargs):
            # Indexes already created in init_db
            pass
    
    return TransactionsCollection()

class TransactionsCursor:
    def __init__(self, query):
        self.query = query
        self.skip_count = 0
        self.limit_count = None
        self.sort_fields = []
    
    def skip(self, n):
        self.skip_count = n
        return self
    
    def limit(self, n):
        self.limit_count = n
        return self
    
    def sort(self, fields):
        self.sort_fields = fields
        return self
    
    def __iter__(self):
        conn = get_db()
        c = conn.cursor()
        
        where_clause = []
        params = []
        
        if 'user_id' in self.query:
            where_clause.append('user_id = ?')
            params.append(self.query['user_id'])
        if 'type' in self.query:
            where_clause.append('type = ?')
            params.append(self.query['type'])
        if 'category' in self.query:
            where_clause.append('category = ?')
            params.append(self.query['category'])
        
        sql = 'SELECT * FROM transactions'
        if where_clause:
            sql += ' WHERE ' + ' AND '.join(where_clause)
        
        if self.sort_fields:
            order_parts = []
            for field, direction in self.sort_fields:
                order_dir = 'DESC' if direction == -1 else 'ASC'
                order_parts.append(f'{field} {order_dir}')
            sql += ' ORDER BY ' + ', '.join(order_parts)
        
        if self.limit_count:
            sql += f' LIMIT {self.limit_count}'
        if self.skip_count:
            sql += f' OFFSET {self.skip_count}'
        
        c.execute(sql, params)
        rows = c.fetchall()
        conn.close()
        
        for row in rows:
            yield {
                '_id': row['id'],
                'user_id': row['user_id'],
                'date': row['date'],
                'type': row['type'],
                'category': row['category'],
                'amount': row['amount'],
                'description': row['description']
            }

def budgets_col():
    """Mock collection object for budgets"""
    class BudgetsCollection:
        def find(self, query):
            return BudgetsCursor(query)
        
        def insert_one(self, doc):
            conn = get_db()
            c = conn.cursor()
            budget_id = str(ObjectId())
            c.execute('''INSERT INTO budgets (id, user_id, month, category, budget_limit)
                        VALUES (?, ?, ?, ?, ?)''',
                     (budget_id, doc['user_id'], doc['month'], 
                      doc['category'], doc['limit']))
            conn.commit()
            conn.close()
            class InsertResult:
                inserted_id = budget_id
            return InsertResult()
        
        def delete_one(self, query):
            conn = get_db()
            c = conn.cursor()
            c.execute('DELETE FROM budgets WHERE id = ?', (query['_id'],))
            conn.commit()
            deleted = c.rowcount
            conn.close()
            class DeleteResult:
                deleted_count = deleted
            return DeleteResult()
        
        def update_one(self, query, update):
            conn = get_db()
            c = conn.cursor()
            budget_id = query.get('_id')
            if budget_id and '$set' in update:
                update_data = update['$set']
                set_clause = ', '.join([f'{k} = ?' for k in update_data.keys()])
                values = list(update_data.values()) + [budget_id]
                c.execute(f'UPDATE budgets SET {set_clause} WHERE id = ?', values)
                conn.commit()
                matched = c.rowcount
                conn.close()
                class UpdateResult:
                    matched_count = matched
                return UpdateResult()
            conn.close()
            class UpdateResult:
                matched_count = 0
            return UpdateResult()
        
        def create_index(self, fields, **kwargs):
            # Indexes already created in init_db
            pass
    
    return BudgetsCollection()

class BudgetsCursor:
    def __init__(self, query):
        self.query = query
        self.skip_count = 0
        self.limit_count = None
    
    def skip(self, n):
        self.skip_count = n
        return self
    
    def limit(self, n):
        self.limit_count = n
        return self
    
    def __iter__(self):
        conn = get_db()
        c = conn.cursor()
        
        where_clause = []
        params = []
        
        if 'user_id' in self.query:
            where_clause.append('user_id = ?')
            params.append(self.query['user_id'])
        if 'month' in self.query:
            where_clause.append('month = ?')
            params.append(self.query['month'])
        
        sql = 'SELECT * FROM budgets'
        if where_clause:
            sql += ' WHERE ' + ' AND '.join(where_clause)
        
        if self.limit_count:
            sql += f' LIMIT {self.limit_count}'
        if self.skip_count:
            sql += f' OFFSET {self.skip_count}'
        
        c.execute(sql, params)
        rows = c.fetchall()
        conn.close()
        
        for row in rows:
            yield {
                '_id': row['id'],
                'user_id': row['user_id'],
                'month': row['month'],
                'category': row['category'],
                'limit': row['budget_limit']
            }

def _db():
    """Mock database object"""
    class Database:
        users = users_col()
        transactions = transactions_col()
        budgets = budgets_col()
    return Database()

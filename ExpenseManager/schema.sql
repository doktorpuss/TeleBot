CREATE TABLE users (
	user_id INTEGER NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	email VARCHAR(100), 
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (user_id), 
	UNIQUE (username)
);
CREATE INDEX ix_users_user_id ON users (user_id);
CREATE TABLE wallets (
	wallet_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	wallet_name VARCHAR(100) NOT NULL, 
	balance DECIMAL(15, 2), 
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (wallet_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
);
CREATE INDEX ix_wallets_wallet_id ON wallets (wallet_id);
CREATE TABLE expenses (
	expense_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	wallet_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	amount DECIMAL(15, 2) NOT NULL, 
	wallet_balance DECIMAL(15, 2) NOT NULL, 
	expense_date DATE NOT NULL, 
	note TEXT, 
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (expense_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id), 
	FOREIGN KEY(wallet_id) REFERENCES wallets (wallet_id), 
	FOREIGN KEY(category_id) REFERENCES categories (category_id)
);
CREATE INDEX ix_expenses_expense_id ON expenses (expense_id);
CREATE TABLE incomes (
	income_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	wallet_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	amount DECIMAL(15, 2) NOT NULL, 
	wallet_balance DECIMAL(15, 2) NOT NULL, 
	income_date DATE NOT NULL, 
	note TEXT, 
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (income_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id), 
	FOREIGN KEY(wallet_id) REFERENCES wallets (wallet_id), 
	FOREIGN KEY(category_id) REFERENCES categories (category_id)
);
CREATE INDEX ix_incomes_income_id ON incomes (income_id);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE IF NOT EXISTS "categories" (
	category_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL,
	budget_id INTEGER,
	category_name VARCHAR(100) NOT NULL, 
	type VARCHAR(7) NOT NULL, 
	PRIMARY KEY (category_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id),
	FOREIGN KEY(budget_id) REFERENCES budgets (budget_id)
);
CREATE INDEX ix_categories_category_id ON categories (category_id);
CREATE TABLE IF NOT EXISTS "budgets" (
    budget_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_name    VARCHAR(100) NOT NULL,
    user_id        INTEGER ,
    balance        DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

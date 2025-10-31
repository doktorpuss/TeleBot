CREATE TABLE users (
	user_id INTEGER NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	user_tele_id VARCHAR(255) NOT NULL, 
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
CREATE TABLE categories (
	category_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	category_name VARCHAR(100) NOT NULL, 
	type VARCHAR(7) NOT NULL, 
	PRIMARY KEY (category_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
);
CREATE INDEX ix_categories_category_id ON categories (category_id);
CREATE TABLE budgets (
	budget_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	budget_name VARCHAR(100) NOT NULL, 
	balance DECIMAL(15, 2) NOT NULL, 
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (budget_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
);
CREATE INDEX ix_budgets_budget_id ON budgets (budget_id);
CREATE TABLE transactions (
	transaction_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	wallet_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	amount DECIMAL(15, 2) NOT NULL, 
	wallet_balance DECIMAL(15, 2) NOT NULL, 
	transaction_date DATE NOT NULL, 
	note TEXT, 
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (transaction_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id) ON DELETE CASCADE, 
	FOREIGN KEY(wallet_id) REFERENCES wallets (wallet_id) ON DELETE CASCADE, 
	FOREIGN KEY(category_id) REFERENCES categories (category_id) ON DELETE CASCADE
);
CREATE INDEX ix_transactions_transaction_id ON transactions (transaction_id);
CREATE TABLE wishlists(
    wish_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    wish_name VARCHAR(50) NOT NULL, 
    cost DECIMAL(15, 2) NOT NULL ,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (wish_id), 
	FOREIGN KEY (user_id) REFERENCES users (user_id)
);
CREATE INDEX ix_wishlists_wish_id ON wishlists (wish_id);
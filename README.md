# Telegram Personal Assistant Bot

This project is a **Telegram bot** built using **python-telegram-bot**, integrated with **Google Calendar API** for schedule management and **SQLite3** for personal finance tracking.

---

## 🚀 Features

* **Schedule management** integrated with Google Calendar.  
* **Expense tracking** stored in SQLite database.  
* **Interactive Telegram interface** using inline buttons and commands.

---

## 🧩 Requirements

* Python 3.10 or higher  
* A Google account (for Google Calendar integration)  
* A Telegram bot token  

---

## 📦 Setup Instructions

### 1️⃣ Clone the repository

### 2️⃣ Create and activate a virtual environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Providing Personal Credentials

### 🗓️ Google Calendar Credentials

If you want to use the Google Calendar reminder feature, you’ll need to set up your Google API credentials.

1. Follow the instructions in the YouTube video linked below to create and download your **Google API Credential file**.  
   https://www.youtube.com/watch?v=B2E82UPUnOY&t=1361s  
2. Move the downloaded file to the folder:
   ```
   Scheduler/token/
   ```
3. Rename the file to:
   ```
   CalendarCredential.json
   ```
4. When you run the bot for the first time, a Google authorization process will open in your browser. Follow the prompts to allow access.

> ⚠️ Note: The Google authentication requires a desktop environment capable of displaying a browser.

---

### 🤖 Telegram Bot Secret

1. Follow the YouTube tutorial provided with this project to **create your own Telegram bot**.  
   https://www.youtube.com/watch?v=vZtm1wuA2yc&t=222s  

2. Copy the necessary information (like your bot token) into the file:
   ```
   user_secrete.py
   ```
3. Rename the file to:
   ```
   secrete.py
   ```

This file is used to securely store your bot configuration and should **never be shared publicly**.

---

## ▶️ Running the Bot

After setup is complete:

```bash
python main.py
```

The bot will start and connect to Telegram.  
If Google Calendar integration is enabled, it will authenticate automatically on first run.

---

## 💰 ExpenseManager Setup

To enable and configure the **Expense Manager** module (personal finance tracking):

### 1️⃣ Install Required Packages

```bash
sudo apt install sqlite3 wkhtmltopdf
```

These tools are required for database operations and generating PDF reports.

---

### 2️⃣ Initialize the Database

Navigate to the `ExpenseManager` directory and create the database:

```bash
sqlite3 expense.db < schema.sql
```

After the database is created, you can optionally add sample data into the following tables:
- **user**
- **category**
- **wallet**
- **budget**

This data will be used by the Expense Manager module to organize transactions and reports.

---

### 3️⃣ Install Fonts for Report Generation

#### 🅰️ Dongle Font

```bash
sudo mkdir -p /usr/share/fonts/truetype/dongle
sudo cp Dongle/*.ttf /usr/share/fonts/truetype/dongle
sudo fc-cache -f -v
```

#### 🖼️ Noto Color Emoji Font

```bash
sudo apt install fonts-noto-color-emoji
```

These fonts ensure proper rendering of special characters and emojis in generated reports.

---

## 💡 Notes

* Keep your `CalendarCredential.json` and `secrete.py` files private.  
* SQLite is used for local data storage; your data is automatically saved in `.db` files.  
* Expense reports are generated as PDFs using `wkhtmltopdf`.  

---

## 🧠 Technologies Used

* **python-telegram-bot** — for Telegram interaction  
* **Google Calendar API** — for schedule management  
* **SQLite3** — for local data storage  
* **wkhtmltopdf** — for report generation  

---

## 📝 License

This project is open-source and available under the MIT License.
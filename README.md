# 🤖 Telegram Personal Assistant Bot

This project is a **Telegram bot** built using **python-telegram-bot**, integrated with **Google Calendar API** for schedule management and **SQLite3** for personal finance tracking (Expense Manager).

---

## 🚀 Features

* 🗓️ **Schedule Management** integrated with Google Calendar.
* 💰 **Expense Tracking** stored in SQLite database.
* 💬 **Interactive Telegram Interface** using inline buttons and commands.
* 📊 **PDF/HTML Report Generation** with custom fonts and chart visualization.

---

## 🧩 Requirements

### System Packages (Ubuntu/Debian)
Before running the bot, install the following system dependencies:
```bash
sudo apt update
sudo apt install sqlite3 wkhtmltopdf
```

### Python Environment
* Python 3.10 or higher  
* A Google account (for Google Calendar integration)  
* A Telegram bot token  

---

## 📦 Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/TeleBot.git
cd TeleBot
```

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

## 💾 Expense Manager Setup

### 1️⃣ Create the SQLite database
Go to the `ExpenseManager` directory and run:
```bash
sqlite3 expense.db < schema.sql
```

After creation, you can manually add or import initial records to tables like:
- `users`
- `categories`
- `wallets`
- `budgets`

⚠️ Note: You do **not** need to include `sqlite_sequence` in your schema.

---

### 2️⃣ Install Fonts for Report Generation

#### Dongle Font
```bash
sudo mkdir -p /usr/share/fonts/truetype/dongle
sudo cp report_fonts/Dongle/*.ttf /usr/share/fonts/truetype/dongle
sudo fc-cache -f -v
```

#### Noto Color Emoji
```bash
sudo apt install fonts-noto-color-emoji
```

---

## 🔐 Providing Personal Credentials

### 🗓️ Google Calendar Credentials
To enable Google Calendar integration:
1. Follow the instructions in this video to create your **Google API credentials**:  
   [▶️ YouTube Guide](https://www.youtube.com/watch?v=B2E82UPUnOY&t=1361s)
2. Move the credential file to:
   ```
   Scheduler/token/
   ```
3. Rename it to:
   ```
   CalendarCredential.json
   ```
4. The first time you run the bot, your browser will prompt you to grant access.

---

### 🤖 Telegram Bot Secret
1. Follow this video to create your own Telegram Bot:  
   [▶️ YouTube Guide](https://www.youtube.com/watch?v=vZtm1wuA2yc&t=222s)
2. Copy the configuration into:
   ```
   user_secrete.py
   ```
3. Rename it to:
   ```
   secrete.py
   ```
> ⚠️ Keep this file private — do not upload it to GitHub.

---

## ▶️ Running the Bot
After setup is complete, run:
```bash
python main.py
```

The bot will connect to Telegram.  
If Google Calendar integration is enabled, it will automatically authenticate on first run.

---

## 💬 Telegram Command Menu

| Command | Description |
|----------|--------------|
| `/today` | Show today’s events from Google Calendar. |
| `/week` | Show events of the current week. |
| `/month` | Show events of the current month. |
| `/create_event` | Create a new event via conversation. |
| `/event` | View events in a specific time range. |
| `/add_income` | Add a new income record. |
| `/add_expense` | Add a new expense record. |
| `/report` | Generate financial report. |
| `/add_budget` | Create or update a spending budget. |
| `/oke` | Confirm or accept an action. |
| `/cancel` | Cancel the current operation. |

---

### 🛠️ Updating Commands in @BotFather
1. Open Telegram and chat with **@BotFather**  
2. Send the command:
   ```
   /setcommands
   ```
3. Choose your bot.
4. Paste the following text:
   ```
   today - get today events
   week - get this week events
   month - get this month events
   create_event - insert new event to calendar
   event - get event list in specific time range
   add_income - add new income
   add_expense - add new expense
   report - generate finance report
   add_budget - create or update a budget
   oke - accept
   cancel - decline
   ```

---

## 🧠 Technologies Used
* **python-telegram-bot** — Telegram bot framework  
* **Google Calendar API** — schedule management  
* **SQLite3** — local data storage  
* **Matplotlib / Altair / ReportLab** — report and visualization  

---

## 📝 License
This project is open-source and available under the **MIT License**.

---

## 💡 Tips
* Keep your `CalendarCredential.json` and `secrete.py` files private.  
* You can duplicate your `expense.db` as a clean **template database** for future use.
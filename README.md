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

1. Follow the instructions in the YouTube video linked belowed to create and download your **Google API Credential file**. 
https://www.youtube.com/watch?v=B2E82UPUnOY&t=1361s

2. Move the downloaded file to the following folder:

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

The bot will start and connect to Telegram. If Google Calendar integration is enabled, it will authenticate automatically on first run.

---

## 💡 Notes

* Keep your `CalendarCredential.json` and `secrete.py` files private.
* The bot uses SQLite for local storage; your data is saved automatically.

---

## 🧠 Technologies Used

* **python-telegram-bot** — for Telegram bot interaction.
* **Google Calendar API** — for schedule management.
* **SQLite3** — for local data storage.

---

## 📺 Support

Watch the official setup videos for guidance on:

* Creating Google API credentials.
* Creating and configuring your Telegram bot.

---

## 📝 License

This project is open-source and available under the MIT License.

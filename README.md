# 🪖 SitRep — CDS Current Affairs Telegram Bot

Fully automatic. Runs 24/7 on Railway (free). No manual commands needed.

---

## 📅 What Gets Sent

| Time (IST) | Message |
|---|---|
| 7:00 AM | 🌅 Full morning digest — Defence, International, Sports, Tech |
| 1:00 PM | ⚡ Defence & International flash |
| 6:30 PM | 🏆 Sports update |
| 9:00 PM | 💻 Tech & AI brief |
| Anytime | 🚨 Instant alert if catastrophe/danger detected |

---

## 🔑 Free API Keys (No Card Required)

| Service | URL | Free Limit |
|---|---|---|
| Telegram Bot | t.me/BotFather | Unlimited |
| Groq (AI) | console.groq.com | 14,400 req/day |
| Currents API | currentsapi.services | 600 req/day |
| NewsAPI | newsapi.org | 100 req/day |

---

## ⚙️ Setup (Windows + Conda)

### Step 1 — Activate your environment
```cmd
conda activate blackrails
pip install -r requirements.txt
```

### Step 2 — Get your keys

**Telegram:**
- Open Telegram → @BotFather → /newbot → name it SitRep
- Copy the token
- Send any message to your bot, then open:
  `https://api.telegram.org/bot<TOKEN>/getUpdates`
- Find your chat ID in the response

**Groq:**
- console.groq.com → sign up → API Keys → Create

**Currents API:**
- currentsapi.services → Register → copy key

**NewsAPI:**
- newsapi.org → Register → copy key

### Step 3 — Test locally
```cmd
copy .env.example .env
# Fill in all keys in .env
python bot.py
```
You should get a Telegram message: "SitRep is online."

---

## ☁️ Deploy to Railway (Free, 24/7)

### Step 1 — Push to GitHub
```cmd
git init
git add .
git commit -m "SitRep bot"
git remote add origin https://github.com/YOUR_USERNAME/sitrep-bot.git
git push -u origin main
```
⚠️ Make sure `.env` is in `.gitignore` — never push your keys!

### Step 2 — Connect Railway
1. Go to railway.app → New Project
2. Deploy from GitHub repo → select `sitrep-bot`
3. Railway auto-detects Python

### Step 3 — Add environment variables
In Railway dashboard → your project → Variables tab, add:
```
TELEGRAM_BOT_TOKEN = ...
TELEGRAM_CHAT_ID   = ...
GROQ_API_KEY       = ...
CURRENTS_API_KEY   = ...
NEWSAPI_KEY        = ...
```

### Step 4 — Deploy
Railway will build and start automatically.
Check logs — you should see "SitRep is live" and get a Telegram message.

---

## 📁 File Structure

```
sitrep-bot/
├── bot.py           # Main entry — scheduler + alert scanner
├── fetcher.py       # RSS + Currents + NewsAPI news fetching
├── summarizer.py    # Groq AI digest builder
├── config.py        # All settings, schedule, keywords
├── requirements.txt
├── Procfile         # Railway process definition
├── railway.toml     # Railway build config
├── .env.example     # Key template
└── .gitignore
```

---

## 🆓 Free Tier Usage Per Day

| Service | Limit | Bot Uses |
|---|---|---|
| Groq | 14,400 req/day | 4 req/day ✅ |
| Currents API | 600 req/day | ~8 req/day ✅ |
| NewsAPI | 100 req/day | ~8 req/day ✅ |
| RSS Feeds | Unlimited | ~50 req/day ✅ |
| Railway | $5 credit/mo | ~$0.50/mo ✅ |

# Lunes Host Auto Keepalive

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Enabled-brightgreen)](https://github.com/features/actions)

Automatically login to Lunes Host and keep your account active by visiting your server page.

## 🌟 Features

- 🔐 Automatic login with email/password
- 🛡️ 2FA/TOTP support
- 🌐 Cloudflare bypass
- 📱 Telegram notifications
- ⏰ Scheduled daily runs
- 🎯 Custom server URL support

## 📋 Requirements

- A Lunes Host account (https://ctrl.lunes.host)
- GitHub account
- (Optional) Telegram Bot for notifications

## 🚀 Setup

### 1. Fork this Repository

Click the "Fork" button at the top right of this page.

### 2. Configure Secrets

Go to your forked repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secrets:

| Secret | Required | Description |
|--------|----------|-------------|
| `LUNES_EMAIL` | ✅ | Your Lunes Host email |
| `LUNES_PASSWORD` | ✅ | Your Lunes Host password |
| `LUNES_SERVER_URL` | ✅ | Your server page URL (e.g., `https://betadash.lunes.host/servers/12345`) |
| `TG_BOT_TOKEN` | ❌ | Telegram Bot Token for notifications |
| `TG_CHAT_ID` | ❌ | Telegram Chat ID for notifications |

### 3. Get Telegram Bot Token (Optional)

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow the instructions to create a bot
4. Save the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Start a chat with your bot and send `/start`
6. Get your Chat ID by visiting:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
   Look for `"chat":{"id":123456789`

### 4. Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. Click "I understand my workflows, go ahead and enable them"

### 5. Test Run

1. Go to **Actions** → **Lunes Host Auto Keepalive**
2. Click **Run workflow**
3. Check the logs

## ⏰ Schedule

By default, the workflow runs daily at 02:00 UTC. You can modify this in `.github/workflows/auto_login.yml`:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 02:00 UTC
```

## 🔐 Two-Factor Authentication (2FA)

If you have 2FA enabled:

1. The script will detect the 2FA page
2. You'll receive a Telegram notification: `🔐 2FA code required`
3. Reply with: `/code 123456` (your 6-digit code)
4. The script will automatically continue

## 🛠️ Local Testing

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/lunes-keepalive-universal.git
cd lunes-keepalive-universal

# Install dependencies
pip install cloudscraper requests

# Run locally
export LUNES_EMAIL="your@email.com"
export LUNES_PASSWORD="yourpassword"
export LUNES_SERVER_URL="https://betadash.lunes.host/servers/12345"
python auto_login.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Use at your own risk. Make sure you have permission to use automated tools on the target platform.

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## 💡 Related Projects

- [ClawCloud-Run](https://github.com/oyz8/ClawCloud-Run) - Keep ClawCloud account active

## 📧 Support

If you encounter any issues, please open an issue on GitHub.

---

Made with ❤️ by the open source community
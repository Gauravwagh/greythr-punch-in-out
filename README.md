# greytHR Auto Punch

Automatically sign in and sign out on [greytHR](https://www.greythr.com/) on weekdays using a cron job.

Uses Selenium with headless Chrome to log into the greytHR portal and click the Sign In / Sign Out button on the dashboard.

## Prerequisites

- **macOS** (tested on macOS; Linux users may need to adjust Chrome binary path in `greythr_punch.py`)
- **Python 3.8+**
- **Google Chrome** installed

## Setup Instructions

### Quick Setup (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/Gauravwagh/greythr-punch-in-out.git
   cd grayhr-punch-in-out
   ```

2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. The setup script will interactively walk you through:
   - Verifying Python 3 and Google Chrome are installed
   - Installing Python dependencies (`selenium`, `webdriver-manager`) via pip
   - Prompting for your greytHR URL, Login ID, and Password (saved securely to a local `.env` file)
   - Optionally setting up cron jobs for automated daily punch (10:05 AM sign-in, 9:50 PM sign-out, weekdays only)
   - Optionally running a test sign-in to verify everything works

### Manual Setup

If you prefer to set things up manually:

1. Install dependencies:
   ```bash
   pip3 install selenium webdriver-manager
   ```

2. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your credentials:
   ```
   GREYTHR_URL=https://your-company.greythr.com/
   GREYTHR_LOGIN_ID=your_login_id
   GREYTHR_PASSWORD=your_password
   ```

4. Test it:
   ```bash
   python3 greythr_punch.py signin
   python3 greythr_punch.py signout
   ```

## Cron Jobs

The `setup.sh` script can configure cron jobs for you automatically. To set them up manually, run `crontab -e` and add:

```cron
5 10 * * 1-5 cd /path/to/greythr && python3 greythr_punch.py signin >> greythr_punch.log 2>&1
50 21 * * 1-5 cd /path/to/greythr && python3 greythr_punch.py signout >> greythr_punch.log 2>&1
```

This schedules:
- **Sign In** at 10:05 AM IST, Monday to Friday
- **Sign Out** at 9:50 PM IST, Monday to Friday

> **Important:** Your Mac must be **awake and not sleeping** at the scheduled times for cron to fire. Consider using [Amphetamine](https://apps.apple.com/app/amphetamine/id937984704) or adjusting System Settings > Energy Saver to prevent sleep.

## All Files

| File | Description | Shared? |
|---|---|---|
| `greythr_punch.py` | Main script - handles login and punch in/out | Yes |
| `setup.sh` | Interactive setup script | Yes |
| `.env.example` | Template showing required credentials | Yes |
| `README.md` | This documentation | Yes |
| `.env` | Your actual credentials (auto-created by setup) | No |
| `greythr_punch.log` | Log file (auto-created on first run) | No |
| `error_signin.png` | Screenshot captured on sign-in failure | No |
| `error_signout.png` | Screenshot captured on sign-out failure | No |

## Troubleshooting

- **Check logs:** `tail -f greythr_punch.log`
- **Check error screenshots:** Open `error_signin.png` or `error_signout.png` if a run failed
- **Chrome version mismatch:** Delete the `~/.wdm` folder and re-run; `webdriver-manager` will download the correct ChromeDriver
- **Button not found:** greytHR uses shadow DOM. If greytHR updates their UI, the button selector in `punch()` may need updating
- **Cron not firing:** Verify your Mac was awake at the scheduled time. Check `crontab -l` to confirm jobs are registered

# Trading Journal - ICT Strategy Tracker

A Django-based trading journal application for tracking ICT (Inner Circle Trader) strategy trades with Docker support. This application provides comprehensive trade journaling, statistics tracking, and performance analysis.

## Features

- **Trade Management**: Full CRUD operations for trades
- **Dashboard**: Overview of daily, weekly, and all-time performance
- **Advanced Filtering**: Filter trades by date, symbol, outcome, entry type, and direction
- **Detailed Statistics**: Performance breakdown by entry type, symbol, confidence level, and direction
- **Auto-Calculations**: Automatic calculation of Risk/Reward ratios and P&L
- **Time Validation**: Enforces trading window (9:30-11:00 AM EST)
- **Price Validation**: Validates stop loss and take profit placement based on direction
- **Screenshot Upload**: Attach trade setup screenshots
- **Admin Panel**: Full admin interface with CSV export functionality
- **Responsive Design**: Mobile-friendly Bootstrap 5 interface

## Technology Stack

- **Backend**: Django 5.2.7
- **Database**: PostgreSQL 15
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Forms**: Django Crispy Forms with Bootstrap 5
- **Containerization**: Docker & Docker Compose
- **Image Processing**: Pillow

## Project Structure

```
trading-journal/
├── main/                      # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── trades/                    # Main trading app
│   ├── models.py             # Trade model
│   ├── views.py              # All views (Dashboard, CRUD, Statistics)
│   ├── forms.py              # Trade and filter forms
│   ├── urls.py               # URL routing
│   ├── admin.py              # Admin configuration
│   ├── utils.py              # Statistics utility functions
│   ├── templates/trades/     # HTML templates
│   └── static/trades/css/    # Custom CSS
├── media/                     # User uploads
├── static/                    # Collected static files
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

## Installation & Setup

### Prerequisites

Before you begin, you need to install Docker on your computer. Docker allows you to run the application in an isolated environment without worrying about dependencies.

#### Installing Docker

**For Windows:**
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop
2. Run the installer and follow the setup wizard
3. Restart your computer when prompted
4. Open Docker Desktop to verify it's running (you'll see a whale icon in your system tray)

**For Mac:**
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop
2. Open the downloaded `.dmg` file and drag Docker to Applications
3. Launch Docker from Applications
4. Wait for Docker to start (whale icon appears in menu bar)

**For Linux (Ubuntu/Debian):**
```bash
# Update package list
sudo apt update

# Install Docker
sudo apt install docker.io docker-compose-v2

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# Log out and log back in for changes to take effect
```

### Quick Start with Docker (Step-by-Step Guide)

Follow these steps carefully to get your trading journal running:

#### Step 1: Open Terminal/Command Prompt

**Windows:**
- Press `Windows Key + R`
- Type `cmd` and press Enter
- OR search for "Command Prompt" in Start Menu

**Mac:**
- Press `Command + Space`
- Type "Terminal" and press Enter

**Linux:**
- Press `Ctrl + Alt + T`

#### Step 2: Navigate to the Project Folder

In the terminal, type the following command to go to the project directory:

```bash
cd "Desktop/The MMXM Trader's 2024/Trading 001/trading-journal"
```

**Note:** If you placed the project in a different location, adjust the path accordingly.

#### Step 3: Set Up Environment Variables (First Time Only)

This step creates your configuration file:

**On Mac/Linux:**
```bash
cp .env.example .env
```

**On Windows:**
```bash
copy .env.example .env
```

**Optional but Recommended:** Edit the `.env` file to change the database password:
1. Open the `.env` file with any text editor (Notepad, TextEdit, etc.)
2. Find the line: `DB_PASSWORD=traderpass123`
3. Change `traderpass123` to your own secure password
4. Save and close the file

#### Step 4: Build and Start the Application

Run these commands one by one:

**Build the application** (this may take a few minutes the first time):
```bash
docker compose build
```

Wait for it to complete, then **start the application**:
```bash
docker compose up -d
```

You should see messages like:
- ✔ Container trading-journal-db-1 Started
- ✔ Container trading-journal-web-1 Started

**What's happening?** Docker is creating two containers:
- One for the database (PostgreSQL)
- One for the web application (Django)

#### Step 5: Create Your Admin Account (First Time Only)

Create your login credentials:

```bash
docker compose exec web python manage.py createsuperuser
```

You'll be asked to enter:
- **Username:** Choose any username (e.g., `admin` or your name)
- **Email:** Your email address (optional, can press Enter to skip)
- **Password:** Choose a strong password (you won't see it as you type)
- **Password (again):** Retype your password

**Important:** Remember these credentials! You'll need them to log in.

#### Step 6: Access the Application

Open your web browser and go to:

🌐 **Main Application:** http://localhost:8069

You'll be redirected to the login page. Use the username and password you just created.

**Additional URLs:**
- 🔧 **Admin Panel:** http://localhost:8069/admin
- 📊 **Dashboard:** http://localhost:8069/ (after login)

---

### Daily Usage - Starting the Application

After the initial setup, starting the app is simple:

1. **Open Terminal/Command Prompt**
2. **Navigate to project folder:**
   ```bash
   cd "Desktop/The MMXM Trader's 2024/Trading 001/trading-journal"
   ```
3. **Start the application:**
   ```bash
   docker compose up -d
   ```
4. **Open browser and go to:** http://localhost:8069

### Stopping the Application

When you're done using the app:

```bash
docker compose down
```

This stops the containers but keeps your data safe.

### Checking if the Application is Running

```bash
docker compose ps
```

You should see two containers running:
- `trading-journal-db-1`
- `trading-journal-web-1`

### Viewing Application Logs (Troubleshooting)

If something isn't working, check the logs:

```bash
docker compose logs -f web
```

Press `Ctrl + C` to stop viewing logs.

### Local Development (Without Docker)

1. **Create and activate virtual environment**:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and configure your local database settings.

4. **Set up PostgreSQL** (if running locally):
   ```bash
   # Create database
   createdb trading_journal
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**:
   ```bash
   python manage.py collectstatic
   ```

8. **Run development server**:
   ```bash
   python manage.py runserver 8069
   ```

## Usage

### Adding a Trade

1. Navigate to **Add Trade** from the navigation menu
2. Fill in all required fields:
   - **Timestamp**: When the trade was taken (must be 9:30-11:00 AM EST)
   - **Symbol**: Choose from NQ, ES, YM, or RTY
   - **Direction**: LONG or SHORT
   - **Entry Type**: Confirmation or Fail Flip
   - **Price Levels**: Entry, Stop Loss, Take Profit
   - **Position Size**: Number of contracts
   - **Confidence Level**: HIGH, MEDIUM, or LOW
   - **Screenshot** (optional): Upload trade setup image
   - **Notes** (optional): Additional trade notes

3. The system will automatically:
   - Generate a unique trade number
   - Calculate Risk/Reward ratio
   - Validate entry time and price levels

### Closing a Trade

1. Edit the trade
2. Set the **Exit Price**
3. The system will automatically:
   - Calculate P&L
   - Determine outcome (WIN/LOSS/BREAKEVEN)

### Viewing Statistics

Navigate to the **Statistics** page to view:
- Overall performance metrics
- Performance by entry type
- Performance by symbol
- Performance by confidence level
- Performance by direction
- Monthly P&L breakdown
- Best/worst trades and days
- Current winning/losing streak

## Docker Commands

### Start the application
```bash
docker-compose up -d
```

### Stop the application
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f web
```

### Access Django shell
```bash
docker-compose exec web python manage.py shell
```

### Access PostgreSQL
```bash
docker-compose exec db psql -U trader -d trading_journal
```

### Restart after code changes
```bash
docker-compose restart web
```

### Rebuild containers
```bash
docker-compose build --no-cache
docker-compose up -d
```

## Trading Rules

The application enforces the following ICT trading rules:

1. **Entry Time Window**: Trades must be taken between 9:30 AM and 11:00 AM EST
2. **LONG Trades**:
   - Stop Loss must be below Entry Price
   - Take Profit must be above Entry Price
3. **SHORT Trades**:
   - Stop Loss must be above Entry Price
   - Take Profit must be below Entry Price

## Admin Panel Features

Access the admin panel at `/admin` to:
- View and manage all trades
- Filter trades by multiple criteria
- Search trades by trade number or notes
- Export selected trades to CSV
- View detailed trade information

## Environment Variables

All environment variables are configured in `.env` file. Copy `.env.example` to `.env` and update the values:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-this
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1

# Web Server Settings
WEB_PORT=8069

# Database Settings
DB_NAME=trading_journal
DB_USER=trader
DB_PASSWORD=your-secure-database-password-here
DB_HOST=db
DB_PORT=5432
DB_EXTERNAL_PORT=5434
```

**Important:**
- Never commit `.env` to version control (it's in `.gitignore`)
- Generate a secure `SECRET_KEY` for production:
  ```bash
  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
  ```
- Use strong passwords for `DB_PASSWORD`
- Set `DEBUG=0` in production

## Database Schema

### Trade Model Fields

- **Identification**: user, trade_number, timestamp, symbol
- **Strategy**: direction, entry_type, timeframe_analysis, confidence_level
- **Price Levels**: entry_price, stop_loss, take_profit, exit_price
- **Position**: position_size
- **Results**: outcome, profit_loss, risk_reward_ratio (auto-calculated)
- **Documentation**: screenshot, notes
- **Timestamps**: created_at, updated_at

## Troubleshooting

### Common Issues and Solutions

#### 1. "Command not found: docker compose"

**Solution:** Docker is not installed or not running.
- Make sure Docker Desktop is running (check for whale icon in system tray/menu bar)
- On Linux, try: `sudo systemctl start docker`
- If still not working, reinstall Docker Desktop

#### 2. "Port is already allocated" or "Address already in use"

**Problem:** Port 8069 is being used by another application.

**Solution:**
```bash
# Stop the application
docker compose down

# Edit .env file and change WEB_PORT to a different number (e.g., 8070)
# Then restart
docker compose up -d
```

#### 3. Cannot Access http://localhost:8069

**Solutions to try:**
1. Check if containers are running:
   ```bash
   docker compose ps
   ```
2. If containers are not running, check logs:
   ```bash
   docker compose logs web
   ```
3. Restart the application:
   ```bash
   docker compose restart
   ```
4. Try rebuilding:
   ```bash
   docker compose down
   docker compose build --no-cache
   docker compose up -d
   ```

#### 4. Forgot Admin Password

**Solution:** Create a new superuser:
```bash
docker compose exec web python manage.py createsuperuser
```

#### 5. Database Connection Issues

**Solution:**
```bash
# Check if database container is running
docker compose ps

# Restart database
docker compose restart db

# If still not working, restart everything
docker compose down
docker compose up -d
```

#### 6. Static Files Not Loading (CSS/Images Missing)

**Solution:**
```bash
docker compose exec web python manage.py collectstatic --noinput
docker compose restart web
```

#### 7. "Permission Denied" Errors

**Solution (Linux only):**
```bash
# Fix media directory permissions
docker compose exec web chmod -R 755 /app/media

# If you get permission errors with docker commands, add sudo:
sudo docker compose up -d
```

#### 8. Application is Slow or Freezing

**Solutions:**
1. Restart Docker Desktop
2. Increase Docker memory allocation:
   - Open Docker Desktop → Settings → Resources
   - Increase Memory to at least 4GB
   - Click "Apply & Restart"

#### 9. Want to Start Fresh (Reset Everything)

**WARNING: This will delete all your trades and data!**

```bash
# Stop and remove everything
docker compose down -v

# Rebuild and start
docker compose build
docker compose up -d

# Create new superuser
docker compose exec web python manage.py createsuperuser
```

### Getting Help

If you're still having issues:

1. **Check the logs:**
   ```bash
   docker compose logs -f web
   ```
2. **Check Docker status:**
   ```bash
   docker compose ps
   docker version
   ```
3. **Restart everything:**
   ```bash
   docker compose down
   docker compose up -d
   ```

## Production Deployment

For production deployment:

1. Set `DEBUG=0` in `.env`
2. Update `SECRET_KEY` with a strong random key
3. Configure `ALLOWED_HOSTS` in `settings.py`
4. Set up HTTPS/SSL
5. Use a production-grade WSGI server (Gunicorn)
6. Configure nginx as reverse proxy
7. Set up database backups
8. Enable logging and monitoring

## Contributing

This is a personal trading journal application. Feel free to fork and customize for your own use.

## License

This project is for personal use.

## Support

For issues or questions, please refer to the Django documentation:
- Django: https://docs.djangoproject.com/
- Docker: https://docs.docker.com/

## Acknowledgments

- Built for tracking ICT (Inner Circle Trader) strategy trades
- Uses Bootstrap 5 for responsive design
- PostgreSQL for reliable data storage

# TradingView to MetaTrader5 Trade Copier (WINDOWS only)

Automatically copy trades from TradingView to MetaTrader5 using a proxy server that runs locally on your windows machine.

🌲 This does NOT involve storing or entering your TradingView or MT5 credentials anywhere on the internet.

This application has been built and tested on Windows machines only.
It will not work on MacOS or Linux or any of Linux's Distros.

## System Architecture

For an onverview of the System Architecture, please refer to [System Architecture](./assets/SystemArchitecture.md)

## Features

- Intercepts TradingView trades
- Copies trades to MT5 in real-time
- Supports market orders (buy, sell, adding/removing/updating take-profit and stop-loss, trailing-stops and partial-close)
- Position tracking and management
- Trade status monitoring
- Persistent storage in PostgreSQL
- Real-time trade synchronization using Redis Pub/Sub
- Asynchronous operations
- Clean logging and error handling

## Prerequisites

- Python 3.11.0
- Docker Desktop
- MetaTrader5 Desktop Terminal (❗This does NOT work on MetaTrader4)
- TradingView Desktop Application (Recommended, but not mandatory)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/abhidp/tradingview-to-metatrader5.git
cd tradingview-to-metatrader5
```

2. Create and activate virtual environment:

```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install mitm proxy certificate:

```bash
python src/scripts/install_certificate.py
```

## Environment Setup

1. Make a copy of the `.env.template` file and name it `.env`:

   - `cp .env.template .env`
   - overwrite the dummy values with your real credentials
   - ⚠️ IMPORTANT: Never commit your `.env` file to version control!
   - if you don't how how to find `TV_ACCOUNT_ID`, refer to [How-To-Find-TradingView-Account-Id](How-To-Find-TradingView-Account-Id.md)

2. Start services:

   `docker-compose up -d`

   Output should be similar to :

   ```
   [+] Running 2/2
   ✔ Container tradingview_db       Running     0.0s
   ✔ Container tradingview_redis    Running     0.0s
   ```

3. Verify docker containers are running

   ```
   $ docker ps -a
     CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS                   PORTS                    NAMES
     73c4a6bc2c3c   postgres:16   "docker-entrypoint.s…"   5 minutes ago   Up 5 minutes (healthy)   0.0.0.0:5432->5432/tcp   tradingview_db
     ac6d86109537   redis:7       "docker-entrypoint.s…"   5 minutes ago   Up 5 minutes (healthy)   0.0.0.0:6379->6379/tcp   tradingview_redis
   ```

4. Create Database and Tables

   ```
   python src/scripts/init_db.py
   ```

   select `Y`

5. Test if all setups are in place. All tests should pass when you run the command
   ```
   python run.py test-all
   ```

## Usage

Step-1 : Open a Terminal and Start the TradingView proxy server

`python run.py proxy`

Step-2 : Open Another Terminal and Start the MT5 worker

`python run.py worker`

Step-3 : Choose either option (a) or (b). Option (b) is recommended

(a) If you are using TradingView in browsers:
Open Proxy settings on your Windows machine and set the following values:

- Use a proxy server : `ON`
- Address : `127.0.0.1`
- Port : `8081`
- User the proxy sever except for addresses: `localhost;127.0.0.1;<local>`
- Don't use the proxy server for local (intranet) addresses : ☑

(b) If you are using TradingView Desktop Application (recommended):

- Go to TradingView --> App Settings --> Network
- ☑ Use a proxy server
- Proxy Protocol: HTTP
- Server IP address or domain name: `127.0.0.1`
- Port: `8081`
- Username: < blank >
- Password: < blank >

Step-4: Open TradingView and login to your account and connect to your broker

Step-5: Open MT5 Desktop and login to your account

Step-6: IMPORTANT: Turn ON ▶ Algo Trading in MT5 Terminal (without this being enabled, trades cannot be executed in MT5 automatically)

Step-7: Place a trade on TradingView, watch it copy over to MT5 within milliseconds

Step-8: Make sure the processes from Step-1 and Step-2 are running continuously in the background. Do NOT close any of the processes. If either of the processes stops, then trades will not be copied to MT5

## Misc info for those who are interested in Development

## Project Structure

```
.
├── src/
│   ├── config/                     # Configuration files
│   │   ├── database.py             # Database config
│   │   ├── mt5_config.py           # MT5 credentials
│   │   └── mt5_symbol_config.py    # Symbol mappings
│   ├── core/                       # Core functionality
│   │   ├── interceptor.py          # Proxy interceptor
│   │   └── trade_handler.py        # Trade processing
│   ├── models/                     # Database models
│   │   └── database.py             # SQLAlchemy models
│   ├── services/                   # External services
│   │   ├── mt5_service.py          # MT5 operations
│   │   └── tradingview_service.py  # TV operations
│   ├── utils/                      # Utilities
│   │   ├── database_handler.py     # DB operations
│   │   ├── queue_handler.py        # Redis operations
│   │   ├── ssl_handler.py          # SSL config
│   │   ├── symbol_mapper.py        # Symbol mapping
│   │   └── token_manager.py        # Auth management
│   └── workers/                    # Workers
│       └── mt5_worker.py           # MT5 trade executor
├── tests/                          # Test suite
│   └── infrastructure/             # Infrastructure tests
│       ├── test_db.py              # Database tests
│       ├── test_redis.py           # Redis tests
│       ├── test_mt5.py             # MT5 tests
│       └── test_tv.py              # TradingView tests
├── docker-compose.yml              # Docker services
├── requirements.txt                # Dependencies
└── run.py                          # CLI interface
```

### Symbol Management

```bash
# List all MT5 symbols
python run.py symbols

# Filter symbols
python run.py symbols --filter USD

# Show symbol management help
python run.py symbols-help
```

### Utility Commands

```bash
# Test database connection
python run.py test-db

# Clean Redis data
python run.py clean-redis

# Show all available commands
python run.py help

# Create an ExcelSheet with specifications of all available symbols
python src\scripts\symbol_specifications.py

```

### Adding New Dependencies

```bash
pip install package-name
python run.py update-reqs
```

### Database Management

```bash
# Initialize database
python src/scripts/init_db.py

# Check database status
python src/scripts/check_db.py
```

### Running Tests

Before running tests, ensure:

1. Docker containers are running
2. MT5 terminal is connected
3. Environment variables are properly set

Run tests:

```bash
# Run all tests
python run.py test-all

# Run specific test
python run.py test-mt5
```

### Symbol Management

```bash
# View all symbols
python src/scripts/manage_symbols.py --list

# Add mapping
python src/scripts/manage_symbols.py --add BTCUSD BTCUSD.r

# Update suffix
python src/scripts/manage_symbols.py --suffix .r
```

## System Requirements

- OS: Windows (primarily developed and tested), Linux/Mac (never tested, no gurantee it will work)
- RAM: 4GB minimum
- Disk Space: 1GB for installation
- Network: Stable internet connection
- Docker for PostgreSQL and Redis

## Developer Contact: abhi358@gmail.com

## 💝 Support the Project

If you find this tool helpful and want to support its continued development, you can contribute in the following ways:

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/abhidp)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/abhidp)

### Cryptocurrency Donations

- **Bitcoin**: `bc1qv734cfcwlm9l34da7naeqkvu7taf9mp9g8c0hh`
- **Ethereum**: `0x024e8D8A0F74b5966C86ef7FFefA6358d3713497`
- **USDT (TRC20)**: `TVcA2grqRLkB91S9LrfqaNM1ro7GYTP9dU`

### Other Ways to Support

- ⭐ Star this repository
- 🐛 Report bugs and contribute fixes
- 💡 Suggest new features and improvements
- 📖 Help improve documentation

Your support helps keep this project maintained and free for everyone! 🙏

## License

MIT License - see LICENSE file for details.

## License

MIT License - see LICENSE file for details.

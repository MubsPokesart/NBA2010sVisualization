# NBA 2010s Visualization - Backend

A Django REST API serving NBA team performance data from the 2010s decade. This backend processes and serves statistical data including offensive ratings, defensive ratings, and other performance metrics for all NBA teams from 2009-2019.

## Features

- Comprehensive NBA team statistics from 2009-2019
- REST API endpoints for accessing team, season, and performance data
- Automated data updates via Kaggle API
- SQLite database with BCNF normalization
- Statistical processing for advanced basketball metrics

## Prerequisites

- Python 3.11+
- Django 5.0+
- Virtual Environment
- Kaggle API credentials (for data updates)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd nba_backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Unix/MacOS
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Configure Kaggle API (for data updates):
   - Place your kaggle.json in the appropriate directory
   - Or set KAGGLE_USERNAME and KAGGLE_KEY environment variables

6. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

- `GET /api/data/` - Retrieve all NBA data
- `GET /api/teams/` - List all teams
- `GET /api/seasons/` - List all seasons
- `GET /api/stats/<season_id>/` - Get stats for a specific season
- `POST /api/update/` - Force update of data from Kaggle

## Data Structure

### Database Schema
- Seasons: Tracks individual seasons (2009-2019)
- Conferences: Eastern/Western conference data
- Teams: Team information and conference affiliations
- TeamStats: Comprehensive team statistics per season

### Statistical Metrics
- Offensive Rating
- Defensive Rating
- Net Rating
- Plus/Minus
- Relative Ratings

## Development

### Project Structure
```
nba_backend/
├── manage.py
├── requirements.txt
├── db/
│   └── decade.sqlite
├── nba_backend/
│   ├── settings.py
│   └── urls.py
└── nba_api/
    ├── models.py
    ├── views.py
    ├── urls.py
    └── utils/
        ├── data_handler.py
        ├── decade_parser.py
        └── db_utils.py
```

### Testing

Run the test suite:
```bash
python manage.py test
```

Or test individual endpoints:
```python
import requests

base_url = 'http://127.0.0.1:8000/api'
response = requests.get(f'{base_url}/data/')
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

None at the Moment

## Acknowledgments

- Data sourced from Kaggle's NBA database
- Built with Django and Django REST Framework
- Statistical calculations based on NBA's official formulas
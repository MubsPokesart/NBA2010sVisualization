import os
import numpy as np
import pandas as pd
from datetime import datetime

class TeamObject:
    # Static season dates dictionary
    SEASON_DATES = {
        "2009-10": {"start": "2009-10-27", "end": "2010-06-17"},
        "2010-11": {"start": "2010-10-26", "end": "2011-06-12"},
        "2011-12": {"start": "2011-12-25", "end": "2012-06-21"},
        "2012-13": {"start": "2012-10-30", "end": "2013-06-20"},
        "2013-14": {"start": "2013-10-29", "end": "2014-06-15"},
        "2014-15": {"start": "2014-10-28", "end": "2015-06-16"},
        "2015-16": {"start": "2015-10-27", "end": "2016-06-19"},
        "2016-17": {"start": "2016-10-25", "end": "2017-06-12"},
        "2017-18": {"start": "2017-10-17", "end": "2018-06-08"},
        "2018-19": {"start": "2018-10-16", "end": "2019-06-13"}
    }

    def __init__(self, name, id, conference):
        self.name = name
        self.id = id
        self.conference = conference
        self.games = {}

    @staticmethod
    def convert_to_datetime(date_input):
        """
        Convert various date formats to datetime object
        """
        if isinstance(date_input, pd.Timestamp):
            return date_input.to_pydatetime()
        elif isinstance(date_input, str):
            return datetime.strptime(date_input, "%Y-%m-%d")
        elif isinstance(date_input, datetime):
            return date_input
        else:
            raise ValueError(f"Unsupported date format: {type(date_input)}")

    @classmethod
    def get_season_dates(cls, season):
        """
        Get the start and end dates for a specific season
        Args:
            season (str): Season in format "YYYY-YY"
        Returns:
            dict: Dictionary containing start and end dates for the season
        """
        return cls.SEASON_DATES.get(season)

    @classmethod
    def is_date_in_season(cls, date_input, season):
        """
        Check if a given date falls within a specific season
        Args:
            date_input: Date in string, Timestamp, or datetime format
            season (str): Season in format "YYYY-YY"
        Returns:
            bool: True if date is within season, False otherwise
        """
        season_dates = cls.get_season_dates(season)
        if not season_dates:
            return False
        
        date = cls.convert_to_datetime(date_input)
        season_start = datetime.strptime(season_dates["start"], "%Y-%m-%d")
        season_end = datetime.strptime(season_dates["end"], "%Y-%m-%d")
        
        return season_start <= date <= season_end

    def get_games_by_season(self):
        """
        Organizes team's games by season.
        Returns:
            list: List of dictionaries where each dictionary contains games for a season
                  with keys formatted as 'season_teamname'
        """
        seasons_games = []
        
        for season in self.SEASON_DATES:
            season_dict = {f"{season} {self.name}": []}
            
            # Go through all games and check if they belong to this season
            for game_date, game_data in self.games.items():
                if self.is_date_in_season(game_date, season):
                    # Convert Timestamp to string format if needed
                    date_str = game_date
                    if isinstance(game_date, pd.Timestamp):
                        date_str = game_date.strftime("%Y-%m-%d")
                    
                    season_dict[f"{season} {self.name}"].append({
                        "date": date_str,
                        **game_data  # Include all other game data
                    })
            
            # Only append if there are games in this season
            if season_dict[f"{season} {self.name}"]:
                seasons_games.append(season_dict)
        
        return seasons_games

START_DATE = "2009-10-27" # First day filtering
END_DATE = "2019-10-22" # Last day filtering

# Teams in NBA based on dataset
WESTERN_CONFERENCE_TEAMS = {'Portland Trail Blazers', 'Los Angeles Lakers', 'Dallas Mavericks', 'Golden State Warriors', 'Denver Nuggets', 'Los Angeles Clippers', 'San Antonio Spurs', 'Minnesota Timberwolves', 'Memphis Grizzlies', 'New Orleans Hornets', 'Phoenix Suns', 'Oklahoma City Thunder', 'Utah Jazz', 'Houston Rockets', 'Sacramento Kings', 'LA Clippers', 'New Orleans Pelicans'}
EASTERN_CONFERENCE_TEAMS = {'Cleveland Cavaliers', 'Atlanta Hawks', 'Miami Heat', 'Boston Celtics',  'Orlando Magic', 'Toronto Raptors', 'Chicago Bulls', 'New Jersey Nets', 'Detroit Pistons', 'Charlotte Bobcats', 'Philadelphia 76ers', 'Indiana Pacers', 'Washington Wizards', 'New York Knicks', 'Milwaukee Bucks', 'Brooklyn Nets', 'Charlotte Hornets'}
ALL_NBA_TEAMS = WESTERN_CONFERENCE_TEAMS.union(EASTERN_CONFERENCE_TEAMS)

def process_filter_db(dataframe=None):
    # Create DataFrame for summary and filter data 
    if dataframe is None:
        raise ValueError("The dataframe must be provided")
    
    summary_df = dataframe
    summary_df['game_date'] = pd.to_datetime(summary_df['game_date'])
    range_dataframe = summary_df[(summary_df['game_date'] >= START_DATE) & (summary_df['game_date'] < END_DATE)]

    # Find every unique team in the dataset and pass them to the TeamObject with their name and id
    teams = range_dataframe['team_id_home'].unique()
    team_objects = []
    for team in teams:
        team_name = range_dataframe[range_dataframe['team_id_home'] == team]['team_name_home'].iloc[0]
        if team_name in WESTERN_CONFERENCE_TEAMS:
            team_objects.append(TeamObject(team_name, team, 'Western'))
        elif team_name in EASTERN_CONFERENCE_TEAMS:
            team_objects.append(TeamObject(team_name, team, 'Eastern'))

    return range_dataframe, team_objects

def generate_dataframe_metrics(range_dataframe, team_objects):
    # Generate possession-based metrics for each game
    for team in team_objects:
        team_games = range_dataframe[(range_dataframe['team_id_home'] == team.id) | (range_dataframe['team_id_away'] == team.id)]
        # Iterate through every game and find the metrics
        for index, game in team_games.iterrows():
            game_stats = {}
            
            if game['team_id_home'] == team.id:
                # Team is home team
                # Calculate possession for team (home perspective)
                team_orb_denom = np.maximum(game['oreb_home'] + game['dreb_away'], 1)  # Avoid division by zero
                opp_orb_denom = np.maximum(game['oreb_away'] + game['dreb_home'], 1)
                
                team_orb_pct = np.divide(game['oreb_home'], team_orb_denom)
                opp_orb_pct = np.divide(game['oreb_away'], opp_orb_denom)
                
                # Vectorized possession calculations
                team_poss = np.sum([
                    game['fga_home'],
                    0.4 * game['fta_home'],
                    -1.07 * team_orb_pct * (game['fga_home'] - game['fgm_home']),
                    game['tov_home']
                ])
                
                opp_poss = np.sum([
                    game['fga_away'],
                    0.4 * game['fta_away'],
                    -1.07 * opp_orb_pct * (game['fga_away'] - game['fgm_away']),
                    game['tov_away']
                ])
                
                # Store stats using numpy operations
                game_stats['plus_minus'] = game['plus_minus_home']
                game_stats['offensive_rating'] = np.multiply(np.divide(game['pts_home'], team_poss), 100)
                game_stats['defensive_rating'] = np.multiply(np.divide(game['pts_away'], opp_poss), 100)
                
            elif game['team_id_away'] == team.id:
                # Team is away team
                # Calculate possession for team (away perspective)
                team_orb_denom = np.maximum(game['oreb_away'] + game['dreb_home'], 1)
                opp_orb_denom = np.maximum(game['oreb_home'] + game['dreb_away'], 1)
                
                team_orb_pct = np.divide(game['oreb_away'], team_orb_denom)
                opp_orb_pct = np.divide(game['oreb_home'], opp_orb_denom)
                
                # Vectorized possession calculations
                team_poss = np.sum([
                    game['fga_away'],
                    0.4 * game['fta_away'],
                    -1.07 * team_orb_pct * (game['fga_away'] - game['fgm_away']),
                    game['tov_away']
                ])
                
                opp_poss = np.sum([
                    game['fga_home'],
                    0.4 * game['fta_home'],
                    -1.07 * opp_orb_pct * (game['fga_home'] - game['fgm_home']),
                    game['tov_home']
                ])
                
                # Store stats using numpy operations
                game_stats['plus_minus'] = game['plus_minus_away']
                game_stats['offensive_rating'] = np.multiply(np.divide(game['pts_away'], team_poss), 100)
                game_stats['defensive_rating'] = np.multiply(np.divide(game['pts_home'], opp_poss), 100)
            
            # Add net rating
            game_stats['net_rating'] = game_stats['offensive_rating'] - game_stats['defensive_rating']
            game_stats['possessions'] = np.mean([team_poss, opp_poss])
            
            # Store all stats for this game date
            team.games[game['game_date']] = game_stats
        
    return team_objects

def generate_individual_season_metrics(team_objects):
    # Generate possession-based metrics for every team in each season
    seasons_dict = {season: [] for season in TeamObject.SEASON_DATES.keys()}
    season_name_length = len(list(TeamObject.SEASON_DATES.keys())[0])

    for team in team_objects:
        team_seasons = team.get_games_by_season()

        for season in team_seasons:
            season_name = list(season.keys())[0]
            game_statistics = list(season.values())[0]
            average_net_rating = np.mean([game['net_rating'] for game in game_statistics])
            average_offensive_rating = np.mean([game['offensive_rating'] for game in game_statistics])
            average_defensive_rating = np.mean([game['defensive_rating'] for game in game_statistics])
            average_plus_minus = np.mean([game['plus_minus'] for game in game_statistics])

            seasons_dict[season_name[:season_name_length]].append({
                "team": team.name,
                "conference": team.conference,
                "average_offensive_rating": average_offensive_rating,
                "average_defensive_rating": average_defensive_rating,
                "average_net_rating": average_net_rating,
                "average_plus_minus": average_plus_minus
            })
    return seasons_dict

def generate_relative_metrics(seasons_dict):
    # Add relative net rating to each season
    for season, teams_data in seasons_dict.items():
        mean_net_rating = np.mean([team_data['average_net_rating'] for team_data in teams_data])
        mean_offensive_rating = np.mean([team_data['average_offensive_rating'] for team_data in teams_data])
        mean_defensive_rating = np.mean([team_data['average_defensive_rating'] for team_data in teams_data])
        
        for team_data in teams_data:
            team_data['relative_net_rating'] = team_data['average_net_rating'] - mean_net_rating
            team_data['relative_offensive_rating'] = team_data['average_offensive_rating'] - mean_offensive_rating
            team_data['relative_defensive_rating'] = team_data['average_defensive_rating'] - mean_defensive_rating
    
def parse_decade_data(unfiltered_data):
    # Process data and filter based on date
    range_dataframe, team_objects = process_filter_db(unfiltered_data)
    
    # Generate possession-based metrics for each game
    team_objects = generate_dataframe_metrics(range_dataframe, team_objects)
    
    # Generate possession-based metrics for each team in each season
    seasons_dict = generate_individual_season_metrics(team_objects)
    
    # Add relative net rating to each season
    generate_relative_metrics(seasons_dict)
    
    return seasons_dict
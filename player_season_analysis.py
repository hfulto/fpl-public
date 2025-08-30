"""
Script to retrieve and display any player's game-by-game data for the 2024/25 season
Shows fixture difficulty ratings and points earned for each match
"""
import pandas as pd
import matplotlib.pyplot as plt
import requests
import os
from datetime import datetime

def get_player_match_data(player_name="Pickford", season="2024-25"):
    """
    Fetch a player's match-by-match data from Vaastav's repository
    
    Parameters:
    - player_name: Name of the player to analyze (default: Pickford)
    - season: Season to fetch (default: 2024-25)
    
    Returns:
    - DataFrame with the player's match data
    """
    print(f"Fetching {player_name}'s match data for {season} season...")
    
    # Base URL for Vaastav's data
    base_url = f"https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/{season}"
    
    # Initialize dictionaries
    team_name_map = {}
    team_short_map = {}
    position_map = {1: "Goalkeeper", 2: "Defender", 3: "Midfielder", 4: "Forward"}
    
    # 1. Get players_raw.csv to find player's ID
    try:
        players_url = f"{base_url}/players_raw.csv"
        players_df = pd.read_csv(players_url)
        
        # Find player's entry (case-insensitive search)
        player_entries = players_df[players_df['web_name'].str.contains(player_name, case=False)]
        
        if len(player_entries) == 0:
            print(f"Error: Could not find {player_name} in the players data")
            return None
            
        # 2. Get teams data early for displaying player options
        try:
            teams_url = f"{base_url}/teams.csv"
            teams_df = pd.read_csv(teams_url)
            # Create mapping dictionaries
            team_name_map = dict(zip(teams_df['id'], teams_df['name']))
            team_short_map = dict(zip(teams_df['id'], teams_df['short_name']))
        except Exception as e:
            print(f"Error loading teams data: {e}")
            team_name_map = {}
            team_short_map = {}
            
        # 3. Get position mapping early for displaying player options
        try:
            elements_url = f"{base_url}/element_types.csv"
            elements_df = pd.read_csv(elements_url)
            position_map = dict(zip(elements_df['id'], elements_df['singular_name']))
        except Exception as e:
            # Default position mapping if we can't load from the API
            print(f"Warning: Could not load position data: {e}")
            position_map = {1: "Goalkeeper", 2: "Defender", 3: "Midfielder", 4: "Forward"}
            
        # Handle multiple player matches
        if len(player_entries) > 1:
            print(f"Found multiple matches for '{player_name}':")
            
            # Ask the user to select a player
            while True:
                try:
                    for i, player in enumerate(player_entries.iterrows(), 1):
                        p = player[1]
                        team_id = p['team']
                        team_name = team_name_map.get(team_id, "Unknown Team")
                        position_id = p['element_type']
                        position_name = position_map.get(position_id, "Unknown Position")
                        print(f"{i}. {p['first_name']} {p['second_name']} ({p['web_name']}) - {team_name} - {position_name}")
                    
                    choice = int(input("\nEnter the number of the player you want to analyze: "))
                    if 1 <= choice <= len(player_entries):
                        player_row = player_entries.iloc[choice-1]
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(player_entries)}")
                except ValueError:
                    print("Please enter a valid number")
        else:
            player_row = player_entries.iloc[0]
        
        player_id = player_row['id']
        player_team_id = player_row['team']
        player_full_name = f"{player_row['first_name']} {player_row['second_name']}"
        player_position = player_row['element_type']
        
        print(f"Found {player_full_name} with ID: {player_id}, Team ID: {player_team_id}")
        
        # Get player's team name (we already have team_name_map from earlier)
        player_team = team_name_map.get(player_team_id, "Unknown")
        print(f"{player_full_name} plays for: {player_team}")
        
        # Get position name
        player_position_name = position_map.get(player_position, "Unknown")
        print(f"Position: {player_position_name}")
    except Exception as e:
        print(f"Error loading or processing player data: {e}")
        return None
    
    # 4. Get fixtures.csv for fixture difficulty ratings
    try:
        fixtures_url = f"{base_url}/fixtures.csv"
        fixtures_df = pd.read_csv(fixtures_url)
        
        # Check if difficulty columns exist
        if 'team_h_difficulty' not in fixtures_df.columns or 'team_a_difficulty' not in fixtures_df.columns:
            print("Warning: Difficulty columns not found in fixtures data")
            # Try to find other difficulty-related columns
            difficulty_cols = [col for col in fixtures_df.columns if 'diff' in col.lower()]
            print("Found these difficulty-related columns:", difficulty_cols)
            
            # If no difficulty columns, add a placeholder
            if not difficulty_cols:
                fixtures_df['team_h_difficulty'] = 3
                fixtures_df['team_a_difficulty'] = 3
                print("Added placeholder difficulty values")
        
        # Filter for player's team's fixtures
        team_fixtures = fixtures_df[(fixtures_df['team_a'] == player_team_id) | 
                                  (fixtures_df['team_h'] == player_team_id)].copy()
        
        # Add home/away indicator and opponent
        team_fixtures['is_home'] = team_fixtures['team_h'] == player_team_id
        team_fixtures['opponent_id'] = team_fixtures.apply(
            lambda row: row['team_a'] if row['is_home'] else row['team_h'], axis=1
        )
        team_fixtures['opponent'] = team_fixtures['opponent_id'].map(team_name_map)
        team_fixtures['opponent_short'] = team_fixtures['opponent_id'].map(team_short_map)
        
        # Get difficulty rating (from perspective of player's team)
        # The difficulty rating is from the opponent's perspective
        team_fixtures['difficulty'] = team_fixtures.apply(
            lambda row: row['team_h_difficulty'] if row['is_home'] else row['team_a_difficulty'], 
            axis=1
        )
        
        print(f"Found {len(team_fixtures)} fixtures for {player_team}")
    except Exception as e:
        print(f"Error loading fixtures data: {e}")
        team_fixtures = pd.DataFrame()
    
    # 5. Get player summary data for PPG and other season stats
    try:
        # Try to get player summary data if available
        summary_url = f"{base_url}/players_summary.csv"
        try:
            summary_df = pd.read_csv(summary_url)
            player_summary = summary_df[summary_df['id'] == player_id]
            
            if len(player_summary) > 0:
                ppg = player_summary['points_per_game'].iloc[0]
                total_points = player_summary['total_points'].iloc[0]
                print(f"Season stats from summary data - PPG: {ppg}, Total Points: {total_points}")
            else:
                print("Player not found in summary data, will calculate PPG from gameweek data")
        except:
            print("Could not find players_summary.csv, will calculate PPG from gameweek data")
    except Exception as e:
        print(f"Error loading player summary data: {e}")
    
    # 6. Get gameweek data for player's performances
    try:
        # Try to get merged gameweeks first
        try:
            gws_url = f"{base_url}/gws/merged_gw.csv"
            gws_df = pd.read_csv(gws_url)
        except:
            print("Could not find merged gameweek data, trying individual gameweeks...")
            # If merged data not available, try to combine individual gameweeks
            gws_df = pd.DataFrame()
            for gw in range(1, 39):  # Assuming 38 gameweeks in a season
                try:
                    gw_url = f"{base_url}/gws/gw{gw}.csv"
                    gw_df = pd.read_csv(gw_url)
                    gws_df = pd.concat([gws_df, gw_df])
                except:
                    # Stop if we can't find a gameweek file (likely reached the end)
                    break
        
        # Filter for player's data
        player_gws = gws_df[gws_df['element'] == player_id].copy()
        
        if len(player_gws) == 0:
            print(f"No gameweek data found for {player_full_name}")
            return None
        
        # Check for duplicate gameweeks (can happen with doubles or data issues)
        gameweek_counts = player_gws['round'].value_counts()
        duplicate_gws = gameweek_counts[gameweek_counts > 1].index.tolist()
        if duplicate_gws:
            print(f"Found duplicate gameweeks: {duplicate_gws}")
            print("This could be due to double gameweeks or data issues.")
            
        print(f"Found data for {len(player_gws)} gameweeks played by {player_full_name}")
    except Exception as e:
        print(f"Error loading gameweek data: {e}")
        return None
    
    # 6. Merge fixture data with gameweek data
    try:
        # Prepare the gameweek data
        player_gws = player_gws.sort_values('round')
        
        # Determine player-specific stats based on position
        if player_position_name.lower() == 'goalkeeper':
            specific_stats = ['goals_conceded', 'clean_sheets', 'saves']
        elif player_position_name.lower() == 'defender':
            specific_stats = ['goals_scored', 'assists', 'clean_sheets', 'goals_conceded']
        elif player_position_name.lower() == 'midfielder':
            specific_stats = ['goals_scored', 'assists', 'clean_sheets']
        else:  # Forward
            specific_stats = ['goals_scored', 'assists']
        
        # Create match data by joining with fixtures
        match_data = []
        
        for _, gw in player_gws.iterrows():
            gw_num = gw['round']
            minutes_played = gw['minutes']
            
            # Skip matches where player didn't play any minutes
            if minutes_played == 0:
                continue
            
            # Find the corresponding fixture
            fixture = team_fixtures[team_fixtures['event'] == gw_num]
            
            if len(fixture) == 0:
                # Fixture not found, create entry with partial data
                match_info = {
                    'gameweek': gw_num,
                    'opponent': 'Unknown',
                    'home_or_away': 'Unknown',
                    'difficulty': None,
                    'points': gw['total_points'],
                    'minutes': gw['minutes'],
                    'bonus': gw['bonus']
                }
                
                # Add position-specific stats
                for stat in specific_stats:
                    if stat in gw:
                        match_info[stat] = gw[stat]
            else:
                fixture = fixture.iloc[0]
                match_info = {
                    'gameweek': gw_num,
                    'opponent': fixture['opponent'],
                    'opponent_short': fixture['opponent_short'],
                    'home_or_away': 'H' if fixture['is_home'] else 'A',
                    'difficulty': fixture['difficulty'],
                    'points': gw['total_points'],
                    'minutes': gw['minutes'],
                    'bonus': gw['bonus']
                }
                
                # Add position-specific stats
                for stat in specific_stats:
                    if stat in gw:
                        match_info[stat] = gw[stat]
            
            match_data.append(match_info)
        
        match_df = pd.DataFrame(match_data)
        
        # Add player info to match_df for later use
        match_df.attrs['player_name'] = player_full_name
        match_df.attrs['player_team'] = player_team
        match_df.attrs['player_position'] = player_position_name
        match_df.attrs['season'] = season
        
        # Try to get PPG from Vaastav's data or calculate it
        try:
            # Try to get PPG from summary data first
            summary_url = f"{base_url}/players_summary.csv"
            summary_df = pd.read_csv(summary_url)
            player_summary = summary_df[summary_df['id'] == player_id]
            
            if len(player_summary) > 0:
                match_df.attrs['official_ppg'] = player_summary['points_per_game'].iloc[0]
                match_df.attrs['total_season_points'] = player_summary['total_points'].iloc[0]
                match_df.attrs['minutes_played'] = player_summary['minutes'].iloc[0]
                match_df.attrs['games_started'] = player_summary['starts'].iloc[0] if 'starts' in player_summary.columns else None
                match_df.attrs['value'] = player_summary['now_cost'].iloc[0] / 10 if 'now_cost' in player_summary.columns else None
        except:
            # If summary data not available, we'll calculate PPG in the display function
            pass
        
        return match_df
        
    except Exception as e:
        print(f"Error creating match data: {e}")
        return None

def display_player_data(match_df):
    """
    Display a player's match data in a formatted table and create a visualization
    """
    if match_df is None or len(match_df) == 0:
        print("No data available to display")
        return
    
    # Get player info from DataFrame attributes
    player_name = match_df.attrs.get('player_name', 'Unknown Player')
    player_team = match_df.attrs.get('player_team', 'Unknown Team')
    player_position = match_df.attrs.get('player_position', 'Unknown Position')
    season = match_df.attrs.get('season', '2024-25')
    
    # 1. Print table of all matches
    print(f"\n=== {player_name.upper()} {season} SEASON MATCH-BY-MATCH DATA ===")
    print(f"Team: {player_team} | Position: {player_position}")
    
    # Format display columns
    display_df = match_df.copy()
    
    # Add home/away indication to opponent
    display_df['fixture'] = display_df.apply(
        lambda row: f"{row['opponent_short']} ({row['home_or_away']})", axis=1
    )
    
    # Check for double gameweeks and format accordingly
    gameweek_counts = display_df['gameweek'].value_counts()
    double_gameweeks = gameweek_counts[gameweek_counts > 1].index.tolist()
    
    if double_gameweeks:
        print(f"\nDouble Gameweeks: {', '.join(map(str, sorted(double_gameweeks)))}")
        
        # Add 'dgw' indicator for double gameweeks
        display_df['is_dgw'] = display_df['gameweek'].isin(double_gameweeks)
        
        # Add indicator to fixture string for double gameweeks
        for gw in double_gameweeks:
            dgw_indices = display_df[display_df['gameweek'] == gw].index
            for i, idx in enumerate(dgw_indices):
                display_df.at[idx, 'fixture'] = f"{display_df.at[idx, 'fixture']} (DGW {i+1})"
    
    # Format difficulty ratings with stars
    def difficulty_stars(difficulty):
        if pd.isna(difficulty):
            return "N/A"
        return "★" * int(difficulty)
    
    display_df['fdr'] = display_df['difficulty'].apply(difficulty_stars)
    
    # Add explanation of FDR
    print("\nFixture Difficulty Rating (FDR):")
    print("★ = Easiest fixture, ★★★★★ = Hardest fixture")
    
    if player_position.lower() == 'goalkeeper':
        print("For goalkeepers, harder fixtures may lead to more save points but fewer clean sheets")
    elif player_position.lower() == 'defender':
        print("For defenders, easier fixtures increase chances of clean sheets and attacking returns")
    elif player_position.lower() == 'midfielder':
        print("For midfielders, easier fixtures typically provide better attacking opportunities")
    else:  # Forward
        print("For forwards, easier fixtures typically provide better scoring opportunities")
    
    # Select and order columns for display based on position
    base_cols = ['gameweek', 'fixture', 'fdr', 'points', 'minutes', 'bonus']
    
    if player_position.lower() == 'goalkeeper':
        display_cols = base_cols + ['clean_sheets', 'goals_conceded', 'saves']
    elif player_position.lower() == 'defender':
        display_cols = base_cols + ['clean_sheets', 'goals_conceded', 'goals_scored', 'assists']
    elif player_position.lower() == 'midfielder':
        display_cols = base_cols + ['goals_scored', 'assists', 'clean_sheets']
    else:  # Forward
        display_cols = base_cols + ['goals_scored', 'assists']
    
    # Only include columns that exist in the DataFrame
    display_cols = [col for col in display_cols if col in display_df.columns]
    
    print(display_df[display_cols].to_string(index=False))
    
    # 2. Print summary statistics
    print(f"\n=== {player_name.upper()} SEASON SUMMARY STATISTICS ===")
    
    # Calculate total points and PPG from our data (only counting games played)
    total_points = match_df['points'].sum()
    games_played = len(match_df)
    calculated_ppg = total_points / games_played if games_played > 0 else 0
    
    # Get official PPG from Vaastav's data if available
    official_ppg = match_df.attrs.get('official_ppg', None)
    official_total_points = match_df.attrs.get('total_season_points', None)
    official_minutes = match_df.attrs.get('minutes_played', None)
    player_value = match_df.attrs.get('value', None)
    
    if official_ppg is not None:
        print(f"Official Points Per Game: {official_ppg}")
    
    print(f"Points Per Game (games with minutes): {calculated_ppg:.2f}")
    
    if official_total_points is not None:
        print(f"Official Total Points: {official_total_points}")
    
    print(f"Total Points (games with minutes): {total_points}")
    
    if official_minutes is not None:
        print(f"Official Minutes Played: {official_minutes}")
    
    print(f"Minutes Played (analyzed games): {match_df['minutes'].sum()}")
    print(f"Games Played (with minutes): {games_played}")
    
    if player_value is not None:
        print(f"Current Value: £{player_value}m")
        print(f"Points Per Million: {calculated_ppg / player_value:.2f}")
    
    total_bonus = match_df['bonus'].sum()
    print(f"Bonus Points: {total_bonus}")
    
    # Position-specific statistics
    if 'clean_sheets' in match_df.columns:
        clean_sheets = match_df['clean_sheets'].sum()
        print(f"Clean Sheets: {clean_sheets}")
    
    if 'goals_conceded' in match_df.columns:
        goals_conceded = match_df['goals_conceded'].sum()
        print(f"Goals Conceded: {goals_conceded}")
    
    if 'saves' in match_df.columns:
        total_saves = match_df['saves'].sum()
        print(f"Total Saves: {total_saves}")
    
    if 'goals_scored' in match_df.columns:
        goals_scored = match_df['goals_scored'].sum()
        print(f"Goals Scored: {goals_scored}")
    
    if 'assists' in match_df.columns:
        assists = match_df['assists'].sum()
        print(f"Assists: {assists}")
    
    # 3. Create visualization
    create_player_visualization(match_df)

def create_player_visualization(match_df):
    """
    Create a visualization of a player's performance vs. fixture difficulty
    """
    # Get player info from DataFrame attributes
    player_name = match_df.attrs.get('player_name', 'Unknown Player')
    player_team = match_df.attrs.get('player_team', 'Unknown Team')
    player_position = match_df.attrs.get('player_position', 'Unknown Position')
    season = match_df.attrs.get('season', '2024-25')
    
    plt.figure(figsize=(14, 8))
    
    # Plot points by gameweek with difficulty color-coding
    ax = plt.gca()
    
    # Difficulty color map
    difficulty_colors = {
        1: '#1e5c35',  # Easy - dark green
        2: '#8bbd94',  # Fairly easy - light green
        3: '#f9e076',  # Medium - yellow
        4: '#f08c66',  # Difficult - orange
        5: '#e84c3d'   # Very difficult - red
    }
    
    # Get default color for missing difficulties
    default_color = '#999999'
    
    # Deduplicate gameweeks for display (take max points for each gameweek)
    gameweek_data = match_df.groupby('gameweek').agg({
        'points': 'sum',  # Sum points for double gameweeks
        'difficulty': 'mean',  # Average difficulty for double gameweeks
        'opponent_short': lambda x: ', '.join(x),  # Join opponent names
        'home_or_away': lambda x: ', '.join(x)  # Join home/away indicators
    }).reset_index()
    
    # Create the scatter plot with colors based on difficulty
    for i, match in gameweek_data.iterrows():
        difficulty = match['difficulty']
        color = difficulty_colors.get(difficulty, default_color) if not pd.isna(difficulty) else default_color
        plt.scatter(match['gameweek'], match['points'], color=color, s=100, zorder=3)
    
    # Connect points with line
    plt.plot(gameweek_data['gameweek'], gameweek_data['points'], color='#37003c', alpha=0.6, linestyle='-', zorder=2)
    
    # Add match labels
    for i, match in gameweek_data.iterrows():
        opponent = match['opponent_short'] if not pd.isna(match['opponent_short']) else 'UNK'
        ha = match['home_or_away'] if not pd.isna(match['home_or_away']) else '?'
        
        # Check if this is a double gameweek
        if ',' in opponent:
            label = "DGW"
        else:
            label = f"{opponent} ({ha})"
            
        plt.annotate(label, 
                    (match['gameweek'], match['points']),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center',
                    fontsize=8)
    
    # Add horizontal line for average points
    avg_points = match_df['points'].mean()
    plt.axhline(y=avg_points, color='#37003c', linestyle='--', alpha=0.5, label=f'Avg: {avg_points:.1f}pts')
    
    # Configure plot
    plt.title(f"{player_name} {season} Season: Points vs Fixture Difficulty", fontsize=14, fontweight='bold')
    plt.suptitle("Games with 0 minutes played are excluded", fontsize=10, style='italic')
    plt.xlabel("Gameweek", fontsize=12)
    plt.ylabel("FPL Points", fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Set x-axis to show all gameweeks
    plt.xticks(sorted(gameweek_data['gameweek'].unique()))
    
    # Create difficulty legend
    legend_elements = []
    for diff, color in difficulty_colors.items():
        label = f'Difficulty {diff}'
        if diff == 1:
            label += ' (Easiest)'
        elif diff == 5:
            label += ' (Hardest)'
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                         markerfacecolor=color, markersize=10,
                                         label=label))
    
    # Add legend
    plt.legend(handles=legend_elements, title="Fixture Difficulty Rating (FDR)", 
              loc='upper right', fontsize=9)
    
    # Add notes
    note_text = f"Note: "
    if player_position.lower() == 'goalkeeper':
        note_text += "For goalkeepers, harder fixtures may lead to more save points but fewer clean sheets."
    elif player_position.lower() == 'defender':
        note_text += "For defenders, easier fixtures increase chances of clean sheets and attacking returns."
    elif player_position.lower() == 'midfielder':
        note_text += "For midfielders, easier fixtures typically provide better attacking opportunities."
    else:  # Forward
        note_text += "For forwards, easier fixtures typically provide better scoring opportunities."
    
    plt.figtext(0.5, 0.02, 
               f"{note_text}\nData source: Vaastav's Fantasy Premier League GitHub Repository",
               ha="center", fontsize=9, style='italic')
    
    plt.tight_layout()
    
    # Save plot as a file
    try:
        filename = f"{player_name.replace(' ', '_').lower()}_season_analysis.png"
        plt.savefig(filename)
        print(f"\nVisualization saved as: {filename}")
    except Exception as e:
        print(f"Warning: Could not save visualization - {e}")
    
    # Use non-blocking plt.show to avoid terminal issues
    plt.show(block=False)
    plt.pause(0.1)  # Small pause to render the plot

def main():
    # Ask for player name
    player_name = input("Enter player name to analyze (e.g., Pickford, Salah, Haaland): ")
    if not player_name:
        player_name = "Pickford"  # Default
        print(f"Using default player: {player_name}")
    
    # Get player's match data
    match_df = get_player_match_data(player_name)
    
    # Display the data
    if match_df is not None:
        display_player_data(match_df)
    else:
        print(f"Could not retrieve {player_name}'s match data")

if __name__ == "__main__":
    main()

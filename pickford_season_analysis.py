"""
Script to retrieve and display Jordan Pickford's game-by-game data for the 2024/25 season
Shows fixture difficulty ratings and points earned for each match
"""
import pandas as pd
import matplotlib.pyplot as plt
import requests
import os
from datetime import datetime

def get_pickford_match_data(season="2024-25"):
    """
    Fetch Jordan Pickford's match-by-match data from Vaastav's repository
    
    Parameters:
    - season: Season to fetch (default: 2024-25)
    
    Returns:
    - DataFrame with Pickford's match data
    """
    print(f"Fetching Jordan Pickford's match data for {season} season...")
    
    # Base URL for Vaastav's data
    base_url = f"https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/{season}"
    
    # 1. Get players_raw.csv to find Pickford's ID
    try:
        players_url = f"{base_url}/players_raw.csv"
        players_df = pd.read_csv(players_url)
        
        # Find Pickford's entry (case-insensitive search)
        pickford_entries = players_df[players_df['web_name'].str.contains('Salah', case=False)]
        
        if len(pickford_entries) == 0:
            print("Error: Could not find Pickford in the players data")
            return None
            
        pickford_id = pickford_entries.iloc[0]['id']
        pickford_team_id = pickford_entries.iloc[0]['team']
        print(f"Found Pickford with ID: {pickford_id}, Team ID: {pickford_team_id}")
        
    except Exception as e:
        print(f"Error loading players data: {e}")
        return None
    
    # 2. Get teams.csv for team names
    try:
        teams_url = f"{base_url}/teams.csv"
        teams_df = pd.read_csv(teams_url)
        # Create mapping dictionaries
        team_name_map = dict(zip(teams_df['id'], teams_df['name']))
        team_short_map = dict(zip(teams_df['id'], teams_df['short_name']))
        pickford_team = team_name_map.get(pickford_team_id, "Unknown")
        print(f"Pickford plays for: {pickford_team}")
    except Exception as e:
        print(f"Error loading teams data: {e}")
        team_name_map = {}
        team_short_map = {}
    
    # 3. Get fixtures.csv for fixture difficulty ratings
    try:
        fixtures_url = f"{base_url}/fixtures.csv"
        fixtures_df = pd.read_csv(fixtures_url)
        
        # Print column names to debug
        print("Fixture data columns:", fixtures_df.columns.tolist())
        
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
        
        # Filter for Pickford's team's fixtures
        team_fixtures = fixtures_df[(fixtures_df['team_a'] == pickford_team_id) | 
                                   (fixtures_df['team_h'] == pickford_team_id)].copy()
        
        # Add home/away indicator and opponent
        team_fixtures['is_home'] = team_fixtures['team_h'] == pickford_team_id
        team_fixtures['opponent_id'] = team_fixtures.apply(
            lambda row: row['team_a'] if row['is_home'] else row['team_h'], axis=1
        )
        team_fixtures['opponent'] = team_fixtures['opponent_id'].map(team_name_map)
        team_fixtures['opponent_short'] = team_fixtures['opponent_id'].map(team_short_map)
        
        # Get difficulty rating (from perspective of Pickford's team)
        # The difficulty rating is from the opponent's perspective
        # For a goalkeeper, higher difficulty for opponent means easier fixture for them
        team_fixtures['difficulty'] = team_fixtures.apply(
            lambda row: row['team_h_difficulty'] if row['is_home'] else row['team_a_difficulty'], 
            axis=1
        )
        
        # Print sample of fixtures to debug
        print("Sample of fixtures data:")
        print(team_fixtures[['event', 'is_home', 'opponent', 'team_h_difficulty', 'team_a_difficulty', 'difficulty']].head())
        
        print(f"Found {len(team_fixtures)} fixtures for {pickford_team}")
    except Exception as e:
        print(f"Error loading fixtures data: {e}")
        team_fixtures = pd.DataFrame()
    
    # 4. Get gameweek data for Pickford's performances
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
        
        # Filter for Pickford's data
        pickford_gws = gws_df[gws_df['element'] == pickford_id].copy()
        
        if len(pickford_gws) == 0:
            print("No gameweek data found for Pickford")
            return None
            
        print(f"Found data for {len(pickford_gws)} gameweeks played by Pickford")
    except Exception as e:
        print(f"Error loading gameweek data: {e}")
        return None
    
    # 5. Merge fixture data with gameweek data
    try:
        # Prepare the gameweek data
        pickford_gws = pickford_gws.sort_values('round')
        
        # Create match data by joining with fixtures
        match_data = []
        
        for _, gw in pickford_gws.iterrows():
            gw_num = gw['round']
            
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
                    'goals_conceded': gw['goals_conceded'],
                    'clean_sheet': gw['clean_sheets'],
                    'saves': gw['saves'],
                    'bonus': gw['bonus']
                }
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
                    'goals_conceded': gw['goals_conceded'],
                    'clean_sheet': gw['clean_sheets'],
                    'saves': gw['saves'],
                    'bonus': gw['bonus']
                }
            
            match_data.append(match_info)
        
        match_df = pd.DataFrame(match_data)
        return match_df
        
    except Exception as e:
        print(f"Error creating match data: {e}")
        return None

def display_pickford_data(match_df):
    """
    Display Pickford's match data in a formatted table and create a visualization
    """
    if match_df is None or len(match_df) == 0:
        print("No data available to display")
        return
    
    # 1. Print table of all matches
    print("\n=== JORDAN PICKFORD 2024/25 SEASON MATCH-BY-MATCH DATA ===")
    
    # Format display columns
    display_df = match_df.copy()
    
    # Add home/away indication to opponent
    display_df['fixture'] = display_df.apply(
        lambda row: f"{row['opponent_short']} ({row['home_or_away']})", axis=1
    )
    
    # Format difficulty ratings with stars
    def difficulty_stars(difficulty):
        if pd.isna(difficulty):
            return "N/A"
        return "★" * int(difficulty)
    
    display_df['fdr'] = display_df['difficulty'].apply(difficulty_stars)
    
    # Add explanation of FDR
    print("\nFixture Difficulty Rating (FDR):")
    print("★ = Easiest fixture, ★★★★★ = Hardest fixture")
    print("For goalkeepers, harder fixtures may lead to more save points but fewer clean sheets")
    
    # Select and order columns for display
    display_cols = ['gameweek', 'fixture', 'fdr', 'points', 'minutes', 
                   'clean_sheet', 'goals_conceded', 'saves', 'bonus']
    
    print(display_df[display_cols].to_string(index=False))
    
    # 2. Print summary statistics
    print("\n=== SEASON SUMMARY STATISTICS ===")
    total_points = match_df['points'].sum()
    avg_points = match_df['points'].mean()
    clean_sheets = match_df['clean_sheet'].sum()
    total_saves = match_df['saves'].sum()
    total_bonus = match_df['bonus'].sum()
    
    print(f"Total Points: {total_points}")
    print(f"Average Points per Game: {avg_points:.2f}")
    print(f"Clean Sheets: {clean_sheets}")
    print(f"Total Saves: {total_saves}")
    print(f"Bonus Points: {total_bonus}")
    
    # 3. Create visualization
    create_pickford_visualization(match_df)

def create_pickford_visualization(match_df):
    """
    Create a visualization of Pickford's performance vs. fixture difficulty
    """
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
    
    # Create the scatter plot with colors based on difficulty
    for i, match in match_df.iterrows():
        difficulty = match['difficulty']
        color = difficulty_colors.get(difficulty, default_color) if not pd.isna(difficulty) else default_color
        plt.scatter(match['gameweek'], match['points'], color=color, s=100, zorder=3)
    
    # Connect points with line
    plt.plot(match_df['gameweek'], match_df['points'], color='#37003c', alpha=0.6, linestyle='-', zorder=2)
    
    # Add match labels
    for i, match in match_df.iterrows():
        opponent = match['opponent_short'] if 'opponent_short' in match else 'UNK'
        ha = match['home_or_away'] if not pd.isna(match['home_or_away']) else '?'
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
    plt.title("Jordan Pickford 2024/25 Season: Points vs Fixture Difficulty", fontsize=14, fontweight='bold')
    plt.xlabel("Gameweek", fontsize=12)
    plt.ylabel("FPL Points", fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Set x-axis to show all gameweeks
    plt.xticks(match_df['gameweek'])
    
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
    plt.figtext(0.5, 0.02, 
               "Note: For goalkeepers, harder fixtures may lead to more save points but fewer clean sheets.\nData source: Vaastav's Fantasy Premier League GitHub Repository",
               ha="center", fontsize=9, style='italic')
    
    plt.tight_layout()
    plt.show()

def main():
    # Get Pickford's match data
    match_df = get_pickford_match_data()
    
    # Display the data
    if match_df is not None:
        display_pickford_data(match_df)
    else:
        print("Could not retrieve Pickford's match data")

if __name__ == "__main__":
    main()

"""
Script to examine the structure of fixtures.csv in Vaastav's FPL repository
Displays team names instead of IDs for better readability
"""
import pandas as pd
import requests

def inspect_fixtures_data():
    """
    Fetch and display a sample of the fixtures.csv data to understand its structure
    """
    print("Fetching fixtures data from Vaastav's repository...")
    
    # Base URL for Vaastav's data
    base_url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2024-25"
    
    try:
        # Load teams data first to map IDs to names
        teams_url = f"{base_url}/teams.csv"
        teams_df = pd.read_csv(teams_url)
        
        # Create ID to name mappings
        team_id_to_name = dict(zip(teams_df['id'], teams_df['name']))
        team_id_to_short = dict(zip(teams_df['id'], teams_df['short_name']))
        
        # Get fixtures data
        fixtures_url = f"{base_url}/fixtures.csv"
        fixtures_df = pd.read_csv(fixtures_url)
        
        # Get basic info about the dataset
        print(f"\nFixtures dataset contains {len(fixtures_df)} rows and {len(fixtures_df.columns)} columns")
        
        # Display column names
        print("\nColumns in fixtures.csv:")
        print(", ".join(fixtures_df.columns.tolist()))
        
        # Create a version of fixtures_df with team names for display
        display_df = fixtures_df.copy()
        if 'team_h' in display_df.columns:
            display_df['team_h_name'] = display_df['team_h'].map(team_id_to_name)
            display_df['team_h'] = display_df['team_h'].map(team_id_to_short)
        if 'team_a' in display_df.columns:
            display_df['team_a_name'] = display_df['team_a'].map(team_id_to_name)
            display_df['team_a'] = display_df['team_a'].map(team_id_to_short)
        
        # Display first 5 rows with compact columns
        print("\nFirst 5 rows of fixtures.csv (with team names):")
        display_columns = ['event', 'team_h', 'team_h_name', 'team_a', 'team_a_name']
        if 'team_h_difficulty' in display_df.columns:
            display_columns.extend(['team_h_difficulty', 'team_a_difficulty'])
        display_df_subset = display_df[display_columns].head()
        print(display_df_subset.to_string())
        
        # Check for difficulty columns
        difficulty_cols = [col for col in fixtures_df.columns if 'difficulty' in col.lower()]
        if difficulty_cols:
            print(f"\nDifficulty-related columns found: {', '.join(difficulty_cols)}")
            
            # Display unique values in difficulty columns
            for col in difficulty_cols:
                unique_values = fixtures_df[col].unique()
                print(f"\nUnique values in {col}: {sorted(unique_values)}")
                
                # Get sample matches with each difficulty level
                print(f"\nSample matches with different {col} values:")
                for value in sorted(unique_values):
                    sample = fixtures_df[fixtures_df[col] == value].head(2)
                    if len(sample) > 0:
                        for _, row in sample.iterrows():
                            if 'team_h' in fixtures_df.columns and 'team_a' in fixtures_df.columns:
                                print(f"  Level {value}: {row['team_h']} vs {row['team_a']} (GW {row.get('event', 'N/A')})")
        else:
            print("\nNo difficulty-related columns found in fixtures.csv")
        
        # Check for teams data to map IDs to names
        print("\nTeam ID to Name mapping:")
        for _, team in teams_df.iterrows():
            print(f"  ID {team['id']}: {team['name']} ({team['short_name']})")
        
        # Check for a few specific fixtures involving popular teams
        popular_teams = [1, 3, 12]  # Arsenal, Bournemouth, Liverpool
        print("\nSample fixtures involving popular teams:")
        for team_id in popular_teams:
            team_name = teams_df[teams_df['id'] == team_id]['name'].values[0]
            home_fixtures = fixtures_df[fixtures_df['team_h'] == team_id].head(2)
            away_fixtures = fixtures_df[fixtures_df['team_a'] == team_id].head(2)
            
            print(f"\n{team_name} home fixtures:")
            for _, fixture in home_fixtures.iterrows():
                away_team = team_id_to_name[fixture['team_a']]
                print(f"  vs {away_team} (GW {fixture.get('event', 'N/A')})")
                if 'team_h_difficulty' in fixtures_df.columns and 'team_a_difficulty' in fixtures_df.columns:
                    print(f"    Home difficulty: {fixture['team_h_difficulty']}, Away difficulty: {fixture['team_a_difficulty']}")
            
            print(f"\n{team_name} away fixtures:")
            for _, fixture in away_fixtures.iterrows():
                home_team = team_id_to_name[fixture['team_h']]
                print(f"  vs {home_team} (GW {fixture.get('event', 'N/A')})")
                if 'team_h_difficulty' in fixtures_df.columns and 'team_a_difficulty' in fixtures_df.columns:
                    print(f"    Home difficulty: {fixture['team_h_difficulty']}, Away difficulty: {fixture['team_a_difficulty']}")
        
        # Focus on the specific Everton vs Brighton GW1 fixture (for Pickford analysis)
        everton_id = teams_df[teams_df['name'] == 'Everton']['id'].values[0]
        brighton_id = teams_df[teams_df['name'] == 'Brighton']['id'].values[0]
        
        pickford_gw1 = fixtures_df[(fixtures_df['team_h'] == everton_id) & 
                                 (fixtures_df['team_a'] == brighton_id) & 
                                 (fixtures_df['event'] == 1)]
        
        if len(pickford_gw1) > 0:
            fixture = pickford_gw1.iloc[0]
            print("\n=== PICKFORD'S GW1 FIXTURE DETAILS ===")
            print(f"Fixture: Everton (H) vs Brighton (A) - GW1")
            print(f"Home team difficulty (Brighton's perspective): {fixture['team_h_difficulty']}")
            print(f"Away team difficulty (Everton's perspective): {fixture['team_a_difficulty']}")
            print(f"Difficulty for Pickford (Everton's GK): {fixture['team_h_difficulty']}")
            print("\nHow FDR 3 was determined for Pickford in GW1:")
            print("1. Pickford plays for Everton (home team in this fixture)")
            print("2. In fixtures.csv, team_h_difficulty = 3 for this match")
            print("3. Since Pickford is on the home team, his fixture difficulty is taken from team_h_difficulty")
            print("4. Therefore, Pickford's FDR for this fixture is 3")
            print("\nNote: FDR is from the perspective of the attacking team facing the defense.")
            print("For Pickford as a goalkeeper, FDR 3 means Brighton's attack vs Everton's defense is rated as medium difficulty.")
        
    except Exception as e:
        print(f"Error loading fixtures data: {e}")

if __name__ == "__main__":
    inspect_fixtures_data()

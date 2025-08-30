# FPL Player Season Analysis

This script allows you to analyze any player's game-by-game Fantasy Premier League (FPL) performance for the 2024/25 season. It provides both a tabular view and visualization of a player's performance in relation to fixture difficulty.

## Features

- Search for any player by name
- Display game-by-game data including points, minutes, and position-specific stats
- View fixture difficulty ratings (FDR) for each match
- Visualization of points vs. fixture difficulty across the season
- Support for double gameweeks
- Summary statistics for the season
- Automatic saving of visualization as PNG file

## How to Use

1. Run the script:
   ```
   python player_season_analysis.py
   ```

2. Enter the player's name when prompted:
   ```
   Enter player name to analyze (e.g., Pickford, Salah, Haaland): Salah
   ```

3. If multiple players match your search, you'll be asked to select one:
   ```
   Found multiple matches for 'Salah':
   1. Mohamed Salah (Salah) - Liverpool - Midfielder
   2. Some Other Salah (Salah) - Some Club - Position
   
   Enter the number of the player you want to analyze: 1
   ```

4. The script will display:
   - Player's match-by-match data with fixture difficulty ratings
   - Season summary statistics
   - A visualization of points vs. fixture difficulty

5. The visualization will be saved as a PNG file (e.g., `mohamed_salah_season_analysis.png`)

## Understanding Fixture Difficulty Ratings (FDR)

Fixture Difficulty Ratings range from 1 (easiest) to 5 (hardest):

- ★ = Easiest fixture
- ★★ = Fairly easy fixture
- ★★★ = Medium difficulty
- ★★★★ = Difficult fixture
- ★★★★★ = Hardest fixture

The impact of fixture difficulty varies by position:
- **Goalkeepers**: Harder fixtures may lead to more save points but fewer clean sheets
- **Defenders**: Easier fixtures increase chances of clean sheets and attacking returns
- **Midfielders**: Easier fixtures typically provide better attacking opportunities
- **Forwards**: Easier fixtures typically provide better scoring opportunities

## Data Source

All data is fetched from Vaastav's Fantasy Premier League GitHub Repository:
https://github.com/vaastav/Fantasy-Premier-League

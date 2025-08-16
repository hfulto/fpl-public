from player_team import FPLTeam
from clean_make_pick import clean_api, start_team_pre_picked

import sys, time, json
from typing import List, Optional
import codecs
import pandas as pd

# Timeout constant (seconds)
TIMEOUT_SECONDS = 10.0

# Main entrypoint for FPL simulation. Parameters can be passed programmatically or via the API.
def run_fpl_api(
    captain_worth: float = 2.0,
    bench_worth: float = 0.5,
    with_status: bool = True,
    prefill_players: Optional[List[str]] = None,
    runs: int = 10000,
    points_minimum: int = 60,
):
    # Static configuration
    best_per_pos = [6, 15, 15, 9]
    cut_exxy = True
    pick_team = True

    # Clean and prepare players data
    players_clean_list, prefill_players_info = clean_api(
        points_minimum=points_minimum,
        prefill_players=prefill_players,
        best_per_pos=best_per_pos,
        with_status=with_status,
        cut_exxy=cut_exxy,
    )

    pre_picked_team = start_team_pre_picked(prefill_players_info)

    max_team = FPLTeam()
    max_squad = FPLTeam()

    start = time.time()
    try:
        for _ in range(runs):
            # enforce constant timeout
            if (time.time() - start) >= TIMEOUT_SECONDS:
                break

            new_team = FPLTeam()
            new_team.make_random_team(players_clean_list, pre_picked_team)

            # Track best overall squad
            if new_team.squad_points > max_squad.squad_points:
                max_squad = new_team

            # If picking a final team, apply bench/captain weights
            if pick_team:
                new_team.pick_best_team(bench_worth, captain_worth)
                if new_team.team_points > max_team.team_points:
                    max_team = new_team
    except (KeyboardInterrupt, SystemExit):
        # Allow graceful stop
        pass
    end = time.time()

    # Helper: convert a Player object to dictionary
    def player_to_dict(player):
        return {
            "name": player.name,
            "cost": player.cost,
            "pts_per_game": player.pts_per_game,
            "pos": player.pos,
        }

    # Helper: convert an FPLTeam to serializable dict
    def team_to_dict(team):
        return {pos: [player_to_dict(p) for p in players] for pos, players in team.items()}

    # Build result payload
    result = {
        "top_team": team_to_dict(max_team.team) if pick_team else None,
        "top_team_points": max_team.team_points if pick_team else None,
        "top_team_cost": round(max_team.squad_cost, 1) if pick_team else None,
        "top_squad": team_to_dict(max_squad.team) if not pick_team else None,
        "player_count": len(players_clean_list),
        "runtime": round(end - start, 2),
        "captain": player_to_dict(max_team.captain) if pick_team else None,
    }
    return result

# If invoked directly via CLI, print JSON to stdout
if __name__ == "__main__":
    # Simple CLI: will ignore passed args and use defaults
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    print(json.dumps(run_fpl_api(), ensure_ascii=False, indent=2))

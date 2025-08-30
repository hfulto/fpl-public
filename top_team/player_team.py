import random
import copy

class Player:
    def __init__(self, id, name, EPL_team, pos, cost, pts_per_game, total_points) -> None:
        self.id = id
        self.name = name
        self.EPL_team = EPL_team
        self.pos = pos
        self.cost = cost
        self.pts_per_game = pts_per_game
        self.total_points = total_points

    def __str__(self):
        return f"{self.name}({self.pts_per_game})"
    
class FPLTeam:

    pos_req = {'GKP':2,'DEF':5,'MID':5,'FWD':3}

    def __init__(self):
        self.squad_cost = 0

        self.squad_points = 0
        self.squad = {'GKP':[],'DEF':[],'MID':[],'FWD':[]}

        self.players_per_team = {}
        self.num_players = 0

        self.team_points = 0
        self.team = {'GKP':[],'DEF':[],'MID':[],'FWD':[],'B':[]}
        self.captain = None


    def make_random_team(self, players_list, prefill_info):
        got_a_team = False

        for _ in range(10000):
            
            if not prefill_info:
                self.squad_cost = 0
                self.squad_points = 0
                self.squad = {'GKP':[],'DEF':[],'MID':[],'FWD':[]}
                self.players_per_team = {}
                self.num_players = 0

            else:
                self.squad_cost = prefill_info[0]
                self.squad_points = prefill_info[1]
                self.squad = copy.deepcopy(prefill_info[2])
                self.players_per_team = prefill_info[3].copy()
                self.num_players = prefill_info[4]

            got_a_team = self.team_maker(players_list)

            if got_a_team:
                return
        
        exit("10000 tries")



    def team_maker(self, players_list):
        temp_list = players_list[:]

        while self.num_players < 15:
            
            if self.squad_cost > 96 or not temp_list:
                return False

            player = random.choice(temp_list)
            temp_list.remove(player)

            if len(self.squad[player.pos]) == FPLTeam.pos_req[player.pos]:
                continue

            if self.squad_cost + player.cost > 100:
                continue

            if player.EPL_team not in self.players_per_team:
                self.players_per_team[player.EPL_team] = 0

            elif self.players_per_team[player.EPL_team] == 3:
                continue

            self.squad[player.pos].append(player)
            self.squad_points += player.pts_per_game
            self.squad_cost += player.cost

            self.players_per_team[player.EPL_team] += 1

            self.num_players += 1

        self.squad_points = round(self.squad_points,1)

        return True
        

    def pick_best_team(self, bench_worth, captain_worth):

        the_rest = []

        # add extra for captain
    
        team_by_ppg =  self.squad['GKP'] +  self.squad['DEF'] + self.squad['MID'] +  self.squad['FWD']
        team_by_ppg = sorted(team_by_ppg, key= lambda x: x.pts_per_game, reverse=True)
        self.team_points += (captain_worth - 1) * team_by_ppg[0].pts_per_game
        self.captain = team_by_ppg[0]

        # 1 goalie

        self.squad['GKP'] = sorted(self.squad['GKP'], key= lambda x: x.pts_per_game, reverse=True)

        self.team['GKP'].append(self.squad['GKP'][0])
        self.team_points += self.squad['GKP'][0].pts_per_game

        self.team['B'].append(self.squad['GKP'][1])
        self.team_points += bench_worth * self.squad['GKP'][1].pts_per_game

        # at least 3 def

        self.squad['DEF'] = sorted(self.squad['DEF'], key= lambda x: x.pts_per_game, reverse=True)

        for i in range(5):

            if i < 3:
                self.team['DEF'].append(self.squad['DEF'][i])
                self.team_points += self.squad['DEF'][i].pts_per_game

            else:
                the_rest.append(self.squad['DEF'][i])
        
        # at least 1 fwd

        self.squad['FWD'] = sorted(self.squad['FWD'], key= lambda x: x.pts_per_game, reverse=True)

        for i in range(3):

            if i == 0:
                self.team['FWD'].append(self.squad['FWD'][0])
                self.team_points += self.squad['FWD'][0].pts_per_game

            else:
                the_rest.append(self.squad['FWD'][i])

        # best players on

        for i in range(5):
            the_rest.append(self.squad['MID'][i])

        the_rest = sorted(the_rest, key= lambda x: x.pts_per_game, reverse=True)

        for _ in range(6):
            player = the_rest.pop(0)

            self.team[player.pos].append(player)
            self.team_points += player.pts_per_game

        for bencher in the_rest:
            self.team['B'].append(bencher)
            self.team_points += bench_worth * bencher.pts_per_game

        self.team_points = round(self.team_points,1)


    def __str__(self):
        if self.team_points:
            retval = f"GKP: {self.team['GKP'][0]}\n"

            retval += "DEF: "
            for d in self.team['DEF']:
                retval += f"{d}, "
            retval = retval[:-2]
            retval += "\n"

            retval += "MID: "
            for m in self.team['MID']:
                retval += f"{m}, "
            retval = retval[:-2]
            retval += "\n"

            retval += "FWD: "
            for f in self.team['FWD']:
                retval += f"{f}, "
            retval = retval[:-2]
            retval += "\n"

            retval += "B: "
            for b in self.team['B']:
                retval += f"{b}, "
            retval = retval[:-2]
            retval += "\n\n"

            retval += f"Team PPG: {self.team_points}\n"
            retval += f"Total Cost: {round(self.squad_cost,1)}\n"

        else:
            retval = f"GKP: {self.squad['GKP'][0]}, {self.squad['GKP'][1]}\n"
            retval += f"DEF: {self.squad['DEF'][0]}, {self.squad['DEF'][1]}, {self.squad['DEF'][2]}, {self.squad['DEF'][3]}, {self.squad['DEF'][4]}\n"
            retval += f"MID: {self.squad['MID'][0]}, {self.squad['MID'][1]}, {self.squad['MID'][2]}, {self.squad['MID'][3]}, {self.squad['MID'][4]}\n"
            retval += f"FWD: {self.squad['FWD'][0]}, {self.squad['FWD'][1]}, {self.squad['FWD'][2]}\n\n"
            retval += f"Squad PPG: {self.squad_points}\n"
            retval += f"Total Cost: {round(self.squad_cost,1)}\n"

        return retval

from player_team import Player
import csv
import random

def clean_api(api_response, points_minimum, best_per_pos, prefill_players, with_status, cut_exxy):

    r = api_response

    best_by_pos = {"GKP":[],"DEF":[],"MID":[],"FWD":[]}

    prefill_players_info = []

    for player in r['elements']:
            
        id = player['id']
        name = player['web_name']
        EPL_team = r['teams'][player['team']-1]['short_name']
        pos = r['element_types'][player['element_type']-1]['plural_name_short']
        cost = round(player['now_cost']/10,1)
        total_points = player['total_points']
        pts_per_game = float(player['points_per_game'])

        if name in prefill_players:
            prefill_players_info.append(Player(id,name,EPL_team,pos,cost,pts_per_game,total_points))
            continue

        if total_points < points_minimum:
            continue
        
        if with_status:
            if player['chance_of_playing_next_round'] not in (None,100):
                continue

        if pos == "MNG":
            continue

        best_by_pos[pos].append(Player(id,name,EPL_team,pos,cost,pts_per_game,total_points))

    players_clean_list = []
    positions = ['GKP','DEF','MID','FWD']

    if best_per_pos:
        for i in range(4):

            best_by_pos[positions[i]] = sorted(best_by_pos[positions[i]], key=lambda x: x.cost)
            best_by_pos[positions[i]] = sorted(best_by_pos[positions[i]], key=lambda x: x.pts_per_game, reverse=True)

            best_by_pos[positions[i]] = best_by_pos[positions[i]][:best_per_pos[i]:]

            for player in best_by_pos[positions[i]]:
                players_clean_list.append(player)

    if cut_exxy:

        pos_req = {'GKP':2,'DEF':5,'MID':5,'FWD':3}

        sorted_players_cost = sorted(players_clean_list, key=lambda x: x.cost, reverse=True)

        for i in range(len(sorted_players_cost)):
            better_player_count = 0

            p1 = sorted_players_cost[i]

            for j in range(len(sorted_players_cost)):

                p2 = sorted_players_cost[j]

                if p2.cost > p1.cost or p2.id == p1.id:
                    continue

                if p2.pos == p1.pos and p2.pts_per_game > p1.pts_per_game:
                    better_player_count += 1

            if better_player_count >= pos_req[p1.pos]:
                players_clean_list.remove(p1)
        
    return (players_clean_list, prefill_players_info)

def start_team_pre_picked(pre_picked):

    squad_cost = 0
    squad_points = 0
    squad = {'GKP':[],'DEF':[],'MID':[],'FWD':[]}
    players_per_team = {}
    num_players = 0

    for pp in pre_picked:
        
        squad_cost += pp.cost
        squad_points += pp.pts_per_game
        squad[pp.pos].append(pp)
        
        if pp.EPL_team not in players_per_team:
            players_per_team[pp.EPL_team] = 1
        
        else:
            players_per_team[pp.EPL_team] += 1

        num_players += 1

    squad_cost = round(squad_cost,1)

    return [squad_cost,squad_points,squad,players_per_team,num_players]


#############################################################################

def clean_data_oop(file_name, points_limit, pts_per_limit, with_status, cut_exxy):
    
    players_list = []

    with open(file_name, 'r') as file:
        reader = csv.reader(file)

        for row in reader:
            players_list.append(row)

    players_list.pop(0)

    #####################################

    id_to_name = []
    
    with open('player_idlist0.csv', 'r',encoding='utf-8') as file:
        reader = csv.reader(file)

        for row in reader:
            id_to_name.append(row[1])

    #######################################


    players_clean_list = []

    for p in range(len(players_list)):

        id = players_list[p][0]

        EPL_team = players_list[p][1]
        name = id_to_name[int(id)] #############
        pos = players_list[p][2]
        cost = float(players_list[p][3])
        total_points = int(players_list[p][6])
        pts_per_game = float(players_list[p][8])

        if total_points < points_limit or pts_per_game < pts_per_limit:
            continue
        
        if with_status:
            if players_list[p][4] != 'Available':
                continue

        players_clean_list.append(Player(id,name,EPL_team,pos,cost,pts_per_game,total_points))


    if cut_exxy:

        pos_req = {'GKP':2,'DEF':5,'MID':5,'FWD':3}

        sorted_players_cost = sorted(players_clean_list, key=lambda x: x.cost, reverse=True)

        for i in range(len(sorted_players_cost)):
            better_player_count = 0

            p1 = sorted_players_cost[i]

            for j in range(len(sorted_players_cost)):

                p2 = sorted_players_cost[j]

                if p2.cost > p1.cost or p2.id == p1.id:
                    continue

                if p2.pos == p1.pos and p2.pts_per_game > p1.pts_per_game:
                    better_player_count += 1

            if better_player_count >= pos_req[p1.pos]:
                players_clean_list.remove(p1)
        
    return players_clean_list

def clean_data_oop_best(file_name, points_limit, best_per_pos, with_status, cut_exxy):
    
    players_list = []

    with open(file_name, 'r') as file:
        reader = csv.reader(file)

        for row in reader:
            players_list.append(row)

    players_list.pop(0)

    ######################################

    id_to_name = []
    
    with open('player_idlist0.csv', 'r',encoding='utf-8') as file:
        reader = csv.reader(file)

        for row in reader:
            id_to_name.append(row[1])

    #####################################

    best_by_pos = {"GKP":[],"DEF":[],"MID":[],"FWD":[]}

    # teams_wanted = ['AVL','BRE','BUR','FUL','LUT','NFO','TOT','WHU']

    for p in range(len(players_list)):

        id = players_list[p][0]
        name = id_to_name[int(id)] #############
        EPL_team = players_list[p][1]
        pos = players_list[p][2]
        cost = float(players_list[p][3])
        total_points = int(players_list[p][6])
        pts_per_game = float(players_list[p][8])

        if total_points < points_limit:
            continue
        
        if with_status:
            if players_list[p][4] != 'Available':
                continue

        # if EPL_team not in teams_wanted:
        #     continue

        best_by_pos[pos].append(Player(id,name,EPL_team,pos,cost,pts_per_game,total_points))


    players_clean_list = []
    positions = ['GKP','DEF','MID','FWD']

    if best_per_pos:
        for i in range(4):

            best_by_pos[positions[i]] = sorted(best_by_pos[positions[i]], key=lambda x: x.cost)
            best_by_pos[positions[i]] = sorted(best_by_pos[positions[i]], key=lambda x: x.pts_per_game, reverse=True)

            best_by_pos[positions[i]] = best_by_pos[positions[i]][:best_per_pos[i]:]

            for player in best_by_pos[positions[i]]:
                players_clean_list.append(player)


    if cut_exxy:

        pos_req = {'GKP':2,'DEF':5,'MID':5,'FWD':3}

        sorted_players_cost = sorted(players_clean_list, key=lambda x: x.cost, reverse=True)

        for i in range(len(sorted_players_cost)):
            better_player_count = 0

            p1 = sorted_players_cost[i]

            for j in range(len(sorted_players_cost)):

                p2 = sorted_players_cost[j]

                if p2.cost > p1.cost or p2.id == p1.id:
                    continue

                if p2.pos == p1.pos and p2.pts_per_game > p1.pts_per_game:
                    better_player_count += 1

            if better_player_count >= pos_req[p1.pos]:
                players_clean_list.remove(p1)
        
    return players_clean_list

#############################################################################

def clean_data(file_name, points_limit, cut_exxy):
    
    players_list = []

    with open(file_name, 'r') as file:
        reader = csv.reader(file)

        for row in reader:
            players_list.append(row)

    players_list.pop(0)

    players_cleaned_dict = {}

    for p in range(len(players_list)):

        id = players_list[p][0]
        points = int(players_list[p][6])
        cost = float(players_list[p][3])
        pos = players_list[p][2]
        EPL_team = players_list[p][1]
        status = players_list[p][4]

        if points < points_limit:
            continue

        if status != 'Available':
            continue

        players_cleaned_dict[id] = [points, cost, pos, EPL_team]

    if cut_exxy:
        pos_req = {'GKP':2,'DEF':5,'MID':5,'FWD':3}

        sorted_players_cost = sorted(players_cleaned_dict.items(), key=lambda x: x[1][1], reverse=True)

        ids_to_remove = []

        for p1 in range(len(sorted_players_cost)):
            better_player_count = 0

            p1_points = sorted_players_cost[p1][1][0]
            p1_cost = sorted_players_cost[p1][1][1]
            p1_pos = sorted_players_cost[p1][1][2]

            for p2 in range(len(sorted_players_cost)):

                p2_points = sorted_players_cost[p2][1][0]
                p2_cost = sorted_players_cost[p2][1][1]
                p2_pos = sorted_players_cost[p2][1][2]

                if p2_cost > p1_cost or p2 == p1:
                    continue

                if p2_pos == p1_pos and p2_points > p1_points:
                    better_player_count += 1

            if better_player_count >= pos_req[p1_pos]:
                ids_to_remove.append(sorted_players_cost[p1][0])

        for id in ids_to_remove:
            players_cleaned_dict.pop(id,None)
        
    return players_cleaned_dict

def make_random_team(players_dict):
    temp_list = list(players_dict.items())

    players_idlist = []
    num_players = 0

    players_per_team = {}

    team_cost = 0
    team_total_points = 0
   
    pos_req = {'GKP':2,'DEF':5,'MID':5,'FWD':3}

    team = {'GKP':[],'DEF':[],'MID':[],'FWD':[]}

    while num_players < 15:

        if team_cost > 96 or not temp_list:
            return make_random_team(players_dict)

        random_player = id, [total_points, cost, pos, EPL_team] = random.choice(temp_list)
        temp_list.remove(random_player)

        if len(team[pos]) == pos_req[pos]:
            continue

        if team_cost + cost > 100:
            continue

        if EPL_team not in players_per_team:
            players_per_team[EPL_team] = 0

        elif players_per_team[EPL_team] == 3:
            continue

        team[pos].append(id)
        team_total_points += total_points
        team_cost += cost

        players_per_team[EPL_team] += 1

        players_idlist.append(id)
        num_players = len(players_idlist)


    return (team,team_total_points,round(team_cost,1))

def pick_best_team(squad, players_dict):

      
    team_points = 0

    team = {'GKP':[],'DEF':[],'MID':[],'FWD':[],'B':[]}

    bench_worth = 0.5

    # 1 goalie

    for i in range(len(squad['GKP'])):
        squad['GKP'][i] = (squad['GKP'][i], players_dict[squad['GKP'][i]][0])

    squad['GKP'] = sorted(squad['GKP'], key= lambda x: x[1], reverse=True)

    team['GKP'].append(squad['GKP'][0][0])
    team_points += squad['GKP'][0][1]

    team['B'].append(squad['GKP'][1][0])
    team_points += bench_worth * squad['GKP'][1][1]

    del squad['GKP']

    # at least 3 def
        
    for i in range(len(squad['DEF'])):
        squad['DEF'][i] = (squad['DEF'][i], players_dict[squad['DEF'][i]][0])

    squad['DEF'] = sorted(squad['DEF'], key= lambda x: x[1], reverse=True)

    for i in range(3):
        team['DEF'].append(squad['DEF'][0][0])
        team_points += squad['DEF'].pop(0)[1]
    
    # at least 1 fwd
        
    for i in range(len(squad['FWD'])):
        squad['FWD'][i] = (squad['FWD'][i], players_dict[squad['FWD'][i]][0])

    squad['FWD'] = sorted(squad['FWD'], key= lambda x: x[1], reverse=True)

    team['FWD'].append(squad['FWD'][0][0])
    team_points += squad['FWD'].pop(0)[1]

    # best players on

    the_rest = []

    for p in squad['DEF']:
        the_rest.append((p[0], p[1], 'DEF'))

    for p in squad['MID']:
        the_rest.append((p, players_dict[p][0], 'MID'))

    for p in squad['FWD']:
        the_rest.append((p[0], p[1], 'FWD'))

    the_rest = sorted(the_rest, key= lambda x: x[1], reverse=True)

    while len(team['GKP']) + len(team['DEF']) + len(team['MID']) + len(team['FWD']) < 11:
        id, points, pos = the_rest.pop(0)

        team[pos].append(id)
        team_points += points

    for bencher in the_rest:
        team['B'].append(bencher[0])
        team_points += bench_worth * bencher[1]

    return (team, round(team_points,1))

def pre_picked_func(players_list, pre_picked):

    squad_cost = 0
    squad_points = 0
    squad = {'GKP':[],'DEF':[],'MID':[],'FWD':[]}
    players_per_team = {}
    num_players = 0

    for pp in pre_picked:
        
        for x in players_list:
            if pp == x.id:
                pp = x
                break

        squad_cost += pp.cost
        squad_points += pp.pts_per_game
        squad[pp.pos].append(pp)
        
        if pp.EPL_team not in players_per_team:
            players_per_team[pp.EPL_team] = 1
        
        else:
            players_per_team[pp.EPL_team] += 1

        num_players += 1

    squad_cost = round(squad_cost,1)

    return [squad_cost,squad_points,squad,players_per_team,num_players]

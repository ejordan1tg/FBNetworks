from statsbombpy import sb
import pandas as pd
import numpy as np
from mplsoccer.pitch import Pitch
# from highlight_text import ax_text, fig_text
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import seaborn as sns
from multiprocessing import freeze_support
import networkx as nx



def main():
    leverkusen_23_24 = sb.matches(competition_id=9, season_id=281)
    leverkusen_23_24 = leverkusen_23_24.sort_values(by='match_date', ascending=True)

    #first match
    latest_match_id = leverkusen_23_24.match_id.iloc[0]

    # get events
    events_df = sb.events(match_id=latest_match_id)
    events_df = events_df.sort_values(by='index', ascending=True)

    # get frames
    frames_df = sb.frames(latest_match_id)
    frames_df.to_csv('C:/Users/Elijah/FBNetworks/frames.csv', index=False)
    frames_df = sb.frames(latest_match_id)



    passing_info = events_df[[
        "type", "possession_team", "player", "position", "player_id", "pass_recipient", "id", "timestamp", "location",
        "pass_end_location", "pass_length", "pass_outcome", 
    ]]
    passing_info.to_csv('C:/Users/Elijah/FBNetworks/passing_info.csv', index=False)
    all_complete_passes_match_01 = getPasses(passing_info)
    buildGraphs(all_complete_passes_match_01, frames_df)
    

# locate pass events
def getPasses(passing_info):
    passing_df = pd.DataFrame(columns=["type", "possession_team", "player", "position", "player_id", "pass_recipient", "id", "timestamp", "location",
        "pass_end_location", "pass_length", "pass_outcome"])
    for i in range(len(passing_info)):
        if(((passing_info['type']).iloc[i] == "Pass") & (pd.notna(passing_info['pass_recipient'].iloc[i])) & (passing_info['possession_team'].iloc[i] == "RB Leipzig")):
            passing_df.loc[len(passing_df)+1] = passing_info.iloc[i]
    passing_df.to_csv('C:/Users/Elijah/FBNetworks/all_passes_match_01.csv', index=False)
    return passing_df


    
def genPitch():
    """
    Fix: Changed to return pitch object and figure, axes
    """
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color='black',
        line_color='white',
        axis=True,
        label=True,
        tick=True
    )
    fig, ax = pitch.draw()
    # plt.show() # Call show() here if needed
    return pitch, fig, ax


def genSlope(y2, y1, x2, x1):
    slope = (y2 - y1)/(x2-x1)
    return slope

def genIntercept(slope, x1, y1):
    if slope is None:
        return None
    intercept = (slope * x1) + y1
    return intercept

def genDistance(x2, x1, y2, y1):
    distance = np.sqrt((x2-x1)**2 + (y2-y1)**2)
    return distance

def is_on_segment(x1, y1, x2, y2, xk, yk, tol=1e-6):
    # Check if (xk, yk) is on the line segment between (x1, y1) and (x2, y2)
    if min(x1, x2) - tol <= xk <= max(x1, x2) + tol and min(y1, y2) - tol <= yk <= max(y1, y2) + tol:
        slope = genSlope(x1, y1, x2, y2)
        if slope is None:
            return abs(xk - x1) < tol
        intercept = genIntercept(slope, x1, y1)
        return abs(yk - (slope * xk + intercept)) < tol
    return False

def buildGraphs(complete_passes, frames):

    for i in range(len(complete_passes)):
        G = nx.Graph()  
        # actor = complete_passes['player'].iloc[i]
        actor_loc = tuple(complete_passes['location'].iloc[i] )
        actorx = actor_loc[0]
        actory = actor_loc[1]

        event_id = str(complete_passes.iloc[i]['id']).strip()

        matching_frames = pd.DataFrame()


        #if frame row id matches event ID, put in smaller dataframe
        matching_frames = frames[frames['id'] == event_id]

        visited = set()
        G = connect_players(G, matching_frames, actor_loc, actorx, actory, visited)       
        plot_network_on_pitch(G,event_id)

def connect_players(G, matching_frames, actor_loc, actorx, actory, visited):
    visited.add(actor_loc)
    for j in range(len(matching_frames)):
        player = tuple(matching_frames['location'].iloc[j])
        if player in visited or matching_frames['teammate'].iloc[j] != True:
            continue
        location_j = matching_frames['location'].iloc[j]
        xj, yj = location_j

        # Check distance
        if genDistance(actorx, actory, xj, yj) < 5:
            continue

        # Check if any other player is on the line segment
        blocked = False
        for k in range(len(matching_frames)):
            if k == j or matching_frames['location'].iloc[k] == actor_loc:
                continue
            xk, yk = matching_frames['location'].iloc[k]
            if is_on_segment(actorx, actory, xj, yj, xk, yk):
                blocked = True
                break
        if blocked:
            continue

        # Add edge and recurse
        G.add_node(player, x=player[0], y=player[1])
        G.add_edge(actor_loc, player)
        print("Added player:")
        print(player)
        connect_players(G, matching_frames, player, xj, yj, visited)

    return G


def plot_network_on_pitch(G,event_id):
    # Generate pitch
    pitch, fig, ax = genPitch()

    # Extract node positions
    pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True) if 'x' in data and 'y' in data}

    # Plot nodes
    nodes_to_plot = [node for node in G.nodes if node in pos]
    pitch.scatter(
        x=[pos[node][0] for node in nodes_to_plot],
        y=[pos[node][1] for node in nodes_to_plot],
        ax=ax,
        s=200,
        color='red',
        edgecolors='white'
    )
    # Plot edges
    for (u, v) in G.edges():
        if u in pos and v in pos:
            pitch.lines(
                xstart=pos[u][0], ystart=pos[u][1],
                xend=pos[v][0], yend=pos[v][1],
                ax=ax,
                lw=2,
                color='cyan',
                comet=True
        )

    
    resultsto = 'C:/Users/Elijah/FBNetworks/PassGraphs/'
    fig.savefig(resultsto + f"{event_id}.png")
    plt.close(fig)
    print("Plot saved")


main()
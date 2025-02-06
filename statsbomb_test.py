

from statsbombpy import sb
import pandas as pd
from mplsoccer import VerticalPitch,Pitch
from highlight_text import ax_text, fig_text
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import seaborn as sns
from multiprocessing import freeze_support
import networkx as nx




def main():
    leverkusen_23_24 = sb.matches(competition_id = 9, season_id=281)
    leverkusen_23_24 = leverkusen_23_24.sort_values(by = 'match_date', ascending = True)

    # print(leverkusen_23_24)

    latest_match_id = leverkusen_23_24.match_id.iloc[0]

    events_df = sb.events(match_id=latest_match_id)
    events_df = events_df.sort_values(by = 'index', ascending=True)
    # events_df.to_csv('C:/Users/Elijah/FBNetworks/events.csv')

    ##grabbing

    frames_df = sb.frames(latest_match_id)
    # frames_df = frames_df.iloc[:,[0, 6, 1, 2, 3, 4, 5]]
    # frames_df.to_csv('C:/Users/Elijah/FBNetworks/frames.csv')
    

    # print(frames_df['id'])
    # print(events_df['id'])
    # merged_df = pd.merge(frames_df, events_df, how='left', on=['match_id','id'])
    # merged_df.to_csv('C:/Users/Elijah/FBNetworks/leverkusen_23_24_23_24_Match1.csv', index=False)

    passing_df = events_df[["type","timestamp","location","pass_end_location","pass_recipient", "pass_outcome", "possession_team"]]
    passing_df = passing_df.to_csv('C:/Users/Elijah/FBNetworks/passing_info.csv')





if __name__ == '__main__':
    freeze_support()
    main()


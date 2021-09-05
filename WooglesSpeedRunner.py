import requests
import json
import PySimpleGUI as sg
import threading, time
from datetime import datetime, timezone, timedelta

URL = 'https://woogles.io/twirp/game_service.GameMetadataService/GetRecentGames'
started = False

def check_every_n_seconds(n=5):
    global run_start_time, started
    game_total_time = 0
    run_total_time = 0
    games = []
    won_games = []
    wins_required = int(values['-WINS-'])
    spread = 0
    while len(won_games) < wins_required:
        print('New check')
        r = client.post(URL, json = headers)
        game_info = json.loads(r.content)['game_info'][0]
        print(game_info)
        game_id = game_info['game_id']
        if game_id in games:
            print('No new game completed')
        else: #new game completed
            start_time = datetime.strptime(game_info['created_at'], "%Y-%m-%dT%H:%M:%S.%f%z")
            end_time = datetime.strptime(game_info['last_update'], "%Y-%m-%dT%H:%M:%S.%f%z")
            if (start_time - run_start_time).total_seconds() >= 0: #make sure game started at same time or after run started
                print('New game completed')
                if game_info['time_control_name'] == str(values['-TIME-']).lower(): #must be playing the right time setting
                    run_old_time = run_total_time
                    run_total_time = (end_time - run_start_time).total_seconds()
                    run_split_time = run_total_time - run_old_time
                    print('Correct time setting')
                    if game_info['players'][0]['nickname'] == str(values['-BOT-']): #if the bot is the first player
                        print('Bot is player 0')
                        game_split_time = (end_time - start_time).total_seconds()
                        game_total_time = game_total_time + game_split_time
                        games.append(game_id)
                        spread += game_info['scores'][1]-game_info['scores'][0]
                        if game_info['winner'] == 1: #player won; write split
                            print('game won')
                            won_games.append(game_id)
                            window['-SPLITS-' + sg.WRITE_ONLY_KEY].print(f"Win {len(won_games)}")
                            sg.cprint(f">Game time: {str(timedelta(seconds=game_split_time))}\n>Total: {str(timedelta(seconds=game_total_time))}\n>Run time: {str(timedelta(seconds=run_split_time))}\n>Total: {str(timedelta(seconds=run_total_time))}", text_color="grey")
                    elif game_info['players'][1]['nickname'] == str(values['-BOT-']): #if the bot is the second player
                        print('Bot is player 1')
                        game_split_time = (end_time - start_time).total_seconds()
                        game_total_time = game_total_time + game_split_time
                        games.append(game_id)
                        spread += game_info['scores'][0]-game_info['scores'][1]
                        if game_info['winner'] == 0: #player won; write split
                            print('game won')
                            won_games.append(game_id)
                            window['-SPLITS-' + sg.WRITE_ONLY_KEY].print(f"Win {len(won_games)}")
                            sg.cprint(f">Game time: {str(timedelta(seconds=game_split_time))}\n>Total: {str(timedelta(seconds=game_total_time))}\n>Run time: {str(timedelta(seconds=run_split_time))}\n>Total: {str(timedelta(seconds=run_total_time))}", text_color="grey")
                    else:
                        window['-SPLITS-' + sg.WRITE_ONLY_KEY].print('Wrong time setting')
                    window['-STATS-'].update(f"Wins: {len(won_games)}/{len(games)} Spread: %s{spread}"%("+" if spread >= 0 else ""))
                else:
                    window['-SPLITS-' + sg.WRITE_ONLY_KEY].print('Wrong opponent')
            else:
                print('No new game completed')
        time.sleep(n - ((datetime.now(timezone.utc) - run_start_time).total_seconds() % n)) #check every 5 seconds
    else: #executes at the end of the run
        started=False
        window['-SPLITS-' + sg.WRITE_ONLY_KEY].print("Run has ended!")
        window['-RUN-'].update('Run has ended!', text_color = 'black')

# Define the window's contents
layout = [[sg.Column([[sg.Text('Woogles Username')], [sg.InputText(key='-ID-', size=(30,1))],
    [sg.Text('Time control'), sg.Combo(['Ultrablitz', 'Blitz', 'Rapid', 'Regular'], default_value='Ultrablitz',key='-TIME-')],
    [sg.Text('Bot'), sg.Combo(['HastyBot', 'STEEBot', 'BetterBot', 'BasicBot', 'BeginnerBot'], default_value='HastyBot', key='-BOT-')],
    [sg.Text('Number of wins'), sg.InputText(key='-WINS-', size=(4,1), enable_events=True, default_text='5')],
    [sg.Button('Start run!')]]), 
    sg.Column([[sg.Image(key='-IMAGE-', filename="macondog.png", size=(200,100))]])],
    [sg.Column([[sg.Text('Run has not started', size=(20,1), key='-RUN-')],
    [sg.Text('Wins: 0/0 Spread: +0', size=(20,1), key='-STATS-')]]),
    sg.Column([[sg.Text('0:00:00.000000', key='-STOPWATCH-', size=(14,1), font=("Helvetica", 25))]])],
    [sg.MLine(size=(60,21), disabled=True, key='-SPLITS-'+ sg.WRITE_ONLY_KEY)]] #height is 11 because there is an empty line at the end

# Create the window
global window
window = sg.Window('Woogles Speed Runner', layout)
sg.cprint_set_output_destination(window, '-SPLITS-'+ sg.WRITE_ONLY_KEY)

# Display and interact with the Window using an Event Loop
while True:
    global event, values
    event, values = window.read(timeout=10)
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'Start run!':
        run_start_time = datetime.now(timezone.utc) #first line so timing is as accurate as possible
        if values['-ID-'] == "":
            sg.popup('Fill in your Woogles username!')
            continue
        if started == True:
            sg.popup('Run already started!')
            continue
        started = True
        client = requests.session()
        headers = {
                     'username' : str(values['-ID-']),
                     'numGames': 1,
                     'offset': 0,
                     'encode' : 'json'
            }
        r = client.post(URL, json = headers)
        loaded = json.loads(r.content)
        try: loaded['game_info']
        except:
            sg.popup('Invalid user!')
            continue
        window['-RUN-'].update('Run has started!', text_color = 'red')
        window['-STATS-'].update('Wins: 0/0 Spread: +0')
        thread = threading.Thread(target=check_every_n_seconds, daemon=True)
        thread.start()
    elif event == '-WINS-' and values['-WINS-'] and (values['-WINS-'][-1] not in ('0123456789') or len(values['-WINS-'])>3):
        window['-WINS-'].update(values['-WINS-'][:-1])
    if started == True:
        stopwatch_time_seconds = (datetime.now(timezone.utc) - run_start_time).total_seconds()
        stopwatch_time = str(timedelta(seconds=stopwatch_time_seconds))
        window['-STOPWATCH-'].update(stopwatch_time)

# Finish up by removing from the screen
window.close()
    

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
    segments = []
    spread = 0
    end_time = run_start_time #baseline
    if values["-CONFIG-"] == True: #using a config file
        #read config.txt file
        config = open("config.txt", "r")
        wins_to_complete = []
        for line in config:
            stripped_line = line.strip()
            wins_to_complete.append(stripped_line.capitalize())
        config.close()
        bot = ', '.join(wins_to_complete).replace('b','B').replace('Stee','STEE')
    else:
        wins_to_complete = [str(values['-BOT-'])] * int(values['-WINS-'])
        bot = str(values['-BOT-'])
    wins_required = str(len(wins_to_complete)) + " win" + "s" if int(values['-WINS-']) > 1 else ""
    window['-RUN-'].update(f"Run to {wins_required} - {str(values['-LEXICON-'])} {bot} {str(values['-TIME-'])} {str(values['-CHALLENGE-'])}", text_color = 'red')
    
    while len(wins_to_complete) > 0:
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
            if (start_time - run_start_time).total_seconds() >= 0: #make sure game started at same time or after run started IMPORTANT FOR TESTING
                print('New game completed')
                if game_info['time_control_name'] == str(values['-TIME-']).lower() and game_info['game_request']['lexicon'] == str(values['-LEXICON-']) and game_info['game_request']['challenge_rule'] == str(values['-CHALLENGE-']): #must be playing the right time setting and lexicon
                    run_old_time = run_total_time
                    run_total_time = (end_time - run_start_time).total_seconds()
                    run_split_time = run_total_time - run_old_time
                    print('Correct time setting')
                    if game_info['players'][0]['nickname'].lower() == wins_to_complete[0].lower(): #if the bot is the first player
                        print('Bot is player 0')
                        game_split_time = (end_time - start_time).total_seconds()
                        game_total_time = game_total_time + game_split_time
                        games.append(game_id)
                        spread += game_info['scores'][1]-game_info['scores'][0]
                        if game_info['winner'] == 1: #player won; write split
                            print('game won')
                            won_games.append(game_id)
                            wins_to_complete.pop(0)
                            segments.append({"name": f"Win {len(won_games)}", "endedAt": {"realtimeMS": run_total_time*1000, "gametimeMS": game_total_time*1000}})
                            window['-SPLITS-' + sg.WRITE_ONLY_KEY].print(f"Win {len(won_games)}")
                            sg.cprint(f">Game time: {str(timedelta(seconds=game_split_time))}\n>Total: {str(timedelta(seconds=game_total_time))}\n>Run time: {str(timedelta(seconds=run_split_time))}\n>Total: {str(timedelta(seconds=run_total_time))}", text_color="grey")
                        else: #player lost; trigger nofail condition
                            print('game lost')
                            if values["-NOFAIL-"] == True: #using a config file
                                break
                    elif game_info['players'][1]['nickname'].lower() == wins_to_complete[0].lower(): #if the bot is the second player
                        print('Bot is player 1')
                        game_split_time = (end_time - start_time).total_seconds()
                        game_total_time = game_total_time + game_split_time
                        games.append(game_id)
                        spread += game_info['scores'][0]-game_info['scores'][1]
                        if game_info['winner'] == 0: #player won; write split
                            print('game won')
                            won_games.append(game_id)
                            wins_to_complete.pop(0)
                            segments.append({"name": f"Win {len(won_games)}", "endedAt": {"realtimeMS": run_split_time*1000, "gametimeMS": game_split_time*1000}})
                            window['-SPLITS-' + sg.WRITE_ONLY_KEY].print(f"Win {len(won_games)}")
                            sg.cprint(f">Game time: {str(timedelta(seconds=game_split_time))}\n>Total: {str(timedelta(seconds=game_total_time))}\n>Run time: {str(timedelta(seconds=run_split_time))}\n>Total: {str(timedelta(seconds=run_total_time))}", text_color="grey")
                        else: #player lost; trigger nofail condition
                            print('game lost')
                            if values["-NOFAIL-"] == True: #using a config file
                                break
                    else:
                        window['-SPLITS-' + sg.WRITE_ONLY_KEY].print('Wrong opponent')
                    window['-STATS-'].update(f"Wins: {len(won_games)}/{len(games)} Spread: %s{spread}"%("+" if spread >= 0 else ""))
                else:
                    window['-SPLITS-' + sg.WRITE_ONLY_KEY].print('Wrong time setting, lexicon or challenge rule')
            else:
                print('No new game completed')
        time.sleep(n - ((datetime.now(timezone.utc) - run_start_time).total_seconds() % n)) #check every 5 seconds
    #executes at the end of the run
    started=False
    window['-SPLITS-' + sg.WRITE_ONLY_KEY].print(f"Run %s! Saved to run_{run_start_time.strftime('%m_%d_%Y_%H_%M_%S')}.json"%('is complete' if len(wins_to_complete) == 0 else 'failed'))
    window['-RUN-'].update(f"Run %s!"%('is complete' if len(wins_to_complete) == 0 else 'failed'), text_color = 'white')
    data = { "_schemaVersion": "v1.0.1", 
        "timer": { "shortname": "woogles", "longname":  "Woogles Speedrunner","version":   "v1.0.0", "website": "https://github.com/nibiew/WooglesSpeedRunner" },
        "videoURL": "",
        "startedAt": run_start_time.isoformat(),
        "endedAt": end_time.isoformat(),
        "game": {"longname": "Woogles.io"},
        "category": {"longname": f"{str(values['-LEXICON-'])} {bot} {str(values['-TIME-'])} {str(values['-CHALLENGE-'])} - Run to {wins_required}"},
        "segments": segments
    }
    with open(f"run_{run_start_time.strftime('%m_%d_%Y_%H_%M_%S')}.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Define the window's contents
layout = [[sg.Column([[sg.Text('Woogles Username')], [sg.InputText(key='-ID-', size=(30,1))],
    [sg.Text('Time control'), sg.Combo(['Ultrablitz', 'Blitz', 'Rapid', 'Regular'], default_value='Ultrablitz',key='-TIME-')],
    [sg.Text('Lexicon'), sg.Combo(['CSW19', 'NWL20', 'ECWL', 'RD28', 'FRA20', 'NSF21'], default_value='CSW19', key='-LEXICON-', size=(8,1))],
    [sg.Text('Challenge Rule'), sg.Combo(['FIVE_POINT', 'TEN_POINT', 'DOUBLE', 'SINGLE', 'VOID', 'TRIPLE'], default_value='FIVE_POINT', key='-CHALLENGE-', size=(12,1))],
    [sg.Text('Bot'), sg.Combo(['HastyBot', 'STEEBot', 'BetterBot', 'BasicBot', 'BeginnerBot'], default_value='HastyBot', key='-BOT-')],
    [sg.Text('Number of wins'), sg.InputText(key='-WINS-', size=(4,1), enable_events=True, default_text='5')],
    [sg.Checkbox('Use config file', key='-CONFIG-'), sg.Checkbox('No fails', key='-NOFAIL-')],
    [sg.Button('Start run!')]]), 
    sg.Column([[sg.Image(key='-IMAGE-', filename="macondog.png", size=(200,100))]])],
    [sg.Column([[sg.Text('Wins: 0/0 Spread: +0', size=(25,1), key='-STATS-')],
    [sg.Text('Run has not started', size=(25,3), key='-RUN-')]]),
    sg.Column([[sg.Text('0:00:00.000000', key='-STOPWATCH-', size=(14,1), font=("Helvetica", 25))]])],
    [sg.MLine(size=(60,11), disabled=True, key='-SPLITS-'+ sg.WRITE_ONLY_KEY)]] #height is 11 because there is an empty line at the end

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
        started = True
        window['-STATS-'].update('Wins: 0/0 Spread: +0')
        thread = threading.Thread(target=check_every_n_seconds, daemon=True)
        thread.start()
    elif event == '-WINS-' and values['-WINS-'] and (values['-WINS-'][-1] not in ('0123456789') or len(values['-WINS-'])>3):
        window['-WINS-'].update(values['-WINS-'][:-1])
    if values["-CONFIG-"] == True:
        window.FindElement('-BOT-').Update(disabled = True)
        window.FindElement('-WINS-').Update(disabled = True)
    elif values['-CONFIG-'] == False:
        window.FindElement('-BOT-').Update(disabled = False)
        window.FindElement('-WINS-').Update(disabled = False)
    if started == True:
        stopwatch_time_seconds = (datetime.now(timezone.utc) - run_start_time).total_seconds()
        stopwatch_time = str(timedelta(seconds=stopwatch_time_seconds))
        window['-STOPWATCH-'].update(stopwatch_time)

# Finish up by removing from the screen
window.close()
    

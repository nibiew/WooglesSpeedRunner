# Woogles Speed Runner
A tool that facilitates Woogles bot "speed runs" - i.e. first to reach x wins against a certain bot. It makes repeated API calls to Woogles to get updated results. You can run the .exe file from the .zip or run the code directly if you have Python installed.

## Instructions

	1. Make sure you have macondog.png downloaded in the same directory as the .py script or .exe file.
	
	2. Key in your Woogles username, select the correct time control, lexicon and challenge rule for the run.
	
	3. You can select a bot and key in the number of wins to achieve. Alternatively, select 'Use config file' if you would like to run multiple bots. If you take this option, config.txt needs to be placed in the same directory and filled with just the bot names, one per line (case-insensitive).
	
	4. Select 'No fails' if this is a no-fail run, i.e. run fails if you lose against the bot at any juncture.
	
	5. Click "Start run!". Do this before you start the game against the bot.
	
	6. When you have completed the run, a .json file will be created in the same directory with the filename "run_<start_time>.json". This follows the Splits.io Exchange Format and can be uploaded to https://splits.io/.

## General Notes

	1. After every win against the correct opponent and time setting, the program will record a split - both the game time and run time.
	
	2. "Game time" refers to the time for the game. "Run time" refers to the time since the "Start run" button is pressed, so it includes any loading times etc.
	
	3. The stopwatch is mainly a display piece - stops in 5 second intervals, rely on the program output for more accuracy.
	
	4. Change the extension to .pyw if you just want to see the GUI, but it might be better to leave the console on for debugging purposes.
	
	5. Suggested speed run rules: no resignations, no passing unless necessary.
	
## Possible future improvements (doable, just laborious)

	1. Allow time controls to be defined specifically, e.g. 15 seconds with increment, rather than just "Ultrablitz".
# Woogles Speed Runner
A tool that facilitates Woogles bot "speed runs" - i.e. first to reach x wins against a certain bot. It makes repeated API calls to Woogles to get updated results. You can run the .exe file from the .zip or run the code directly if you have Python installed.

## Instructions

	1. Make sure you have macondog.png downloaded in the same directory.
	
	2. Key in your Woogles username, select the correct time control and bot for the run, and key in the number of wins to achieve.
	
	3. Click "Start run!"
	
	4. When you have completed the run, a .json file will be created in the same directory with the filename "run_<start_time>.json". This follows the Splits.io Exchange Format and can be uploaded to https://splits.io/.

## General Notes

	1. After every win against the correct opponent and time setting, the program will record a split - both the game time and run time.
	
	2. "Game time" refers to the time for the game. "Run time" refers to the time since the "Start run" button is pressed, so it includes any loading times etc.
	
	3. The stopwatch is mainly a display piece - stops in 5 second intervals, rely on the program output for more accuracy.
	
	4. Change the extension to .pyw if you just want to see the GUI, but it might be better to leave the console on for debugging purposes.
	
	5. Suggested speed run rules: no resignations, no passing unless necessary.
	
## Possible future improvements (all quite doable, just laborious)

	1. Allow people to run against multiple bots.
	
	2. Allow time controls to be defined specifically, e.g. 15 seconds with increment, rather than just "Ultrablitz".
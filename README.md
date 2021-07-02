### Development
1. Install python (add python to system path if on windows)
2. python3 -m venv [virtual_env_name]
3. source [virtual_env_name]/bin/activate if on mac
   venv\Scripts\activate.bat if on windows
4. pip install -r requirements.txt
5. If you pip install and import any new libraries, be sure to run 'pip freeze > requirements.txt' before pushing changes
6. type 'deactivate' to exit virtual environment

### Environment Variables and Credentials
Ask Jeremy for environment variables, then create a .env file if on mac, or an env.bat file if on Windows

Contents of env file:

1. Mac: export [key_name]=[value] -----> type 'source .env' to use environment variables
2. Windows: SET [key_name]=[value] -----> type 'call env.bat' to use environment variables

### Info
This is a discord bot created to organize and manage music posted to the laCreme discord channel.

### Goals
	1. laCreme running monthly playlist
		a. Purge this playlist every month with Python apscheduler library
	2. Archive all songs ever uploaded from laCreme playlist
	3. Keep running playlists of loosie channels as well
	4. Figure out if these playlists will all be kept on my spotify account, or if they can be stored in the laCreme spotify app that was created
	5. Deployment with Heroku (free)
	6. $ see posts jtyson728 --> see all songs uploaded by a certain user
	7. Keep user metrics of # of songs posted admin only
	8. Each song has a genre profile, can have function that returns the genre that each user posts the most
	

### Libraries
TBD

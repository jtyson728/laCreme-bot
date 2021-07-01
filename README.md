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

### Libraries
TBD

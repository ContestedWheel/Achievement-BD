# Achievement-BD
A Achievement system For Ballsdex
Tested on Ballsdex 2.24.0 and discord.py 2.4.0

# How to install 

## Step 1 install the package manually by downloading all the files in the GitHub repositories achievements folder.

Create a new folder in `ballsdex/packages` called achievements.
Copy and paste the `__init__.py, cog.py, models.py and transformers.py` files into the achievements folder.

Open your `config.yml` file and go down to the packages section.
Add ballsdex.packages.achievements as in the packages section. 

## Step 2
open Your `ballsdex/core/__main__.py` 

Edit The 
```py 
TORTOISE_ORM = {
    "connections": {"default": os.environ.get("BALLSDEXBOT_DB_URL")},
    "apps": {
        "models": {
            "models": ["ballsdex.core.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
```
Line to include achievement like this 
  ```py
  TORTOISE_ORM = {
    "connections": {"default": os.environ.get("BALLSDEXBOT_DB_URL")},
    "apps": {
      "models": {
        "models": ["ballsdex.core.models", "balldex.packages.achievements.models", aerich.models"],
        "default_connection": "default",
      },
    },
  }
  ```

# Step 3 

At your `BallsDex-DiscordBot/admin_panel` folder create a folder named `achievement` 
then copy past the files inside the achievement folder in to that achievement folder you made otherwise copy the entire achievement folder from here and past it at your BallsDex-DiscordBot/admin_panel/ 

Now at 
`admin_panel/admin_panel/settings/local.py`
add this line `INSTALLED_APPS.append("achievement")`

Then at 
`BallsDex-DiscordBot/admin_panel`  
Run 
```py
python3 manage.py migrate achievement
```

Now start the bot You should now see achievement list and claim commands 

# FEEL FREE To Edit the code Fix mistakes or use anywhere If you get any issues regarding the code contact me in discord Or create a pull Request in this repository

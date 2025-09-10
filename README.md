# Achievement-BD
An achievement system for Ballsdex.
Tested on Ballsdex 2.24.0 and discord.py 2.4.0 and Ballsdex 2.27.0 with discord py 2.5.0

>[!IMPORTANT]
> If any errors occur while running this package, please contact me directly on Discord (username: noobdog667)




# How to install 

1. Install the package manually by downloading all the files in the GitHub repository.

2. Create a new folder in `ballsdex/packages` called achievements.

3. Copy and paste the `__init__.py, cog.py, models.py` and `transformers.py` from the package folder into your achievements folder.

It should look like this:

<img width="653" height="161" alt="image" src="https://github.com/user-attachments/assets/39c8fc14-1b0e-4cc9-bacf-eec1f3febe2c" />

4. Open your `config.yml` file and scroll down until you see the list of packages. Add `ballsdex.packages.achievements` in that list. It should look like this:

<img width="444" height="227" alt="image" src="https://github.com/user-attachments/assets/eefdacba-44f6-4c6c-a8c9-c92039a1d782" />

Note that if you have multiple packages, it will look different.


5. Open `__main__.py`. located in the `ballsdex` folder.

6. Go to line 33 and add `"ballsdex.packages.achievements.model"`. Make sure to include the quotation marks.

It should look like this after:

<img width="859" height="182" alt="image" src="https://github.com/user-attachments/assets/7cd062fc-6768-44d1-a2f1-99b897e11869" />

7. In the first `admin_panel` (not the second), create a new folder named `achievement`

8. Copy and paste the files from the "achievement" folder (including the migrations folder) into the achievement folder you made.

9. Open the `local.py` file, located in `admin_panel/admin_panel/settings`.  Add this below line 5:

```py
INSTALLED_APPS.append("achievement")
```

It should look like this after:

<img width="466" height="263" alt="image" src="https://github.com/user-attachments/assets/95056964-4bf8-4cde-9cb0-ed5b2e6141fe" />

10. Save the file and close your text editor. Then, go to your terminal and use the migration command.
 
For Docker:
```py
docker compose exec admin-panel python3 manage.py migrate achievement
```

For Poetry (Dockerless):
```py
poetry run python3 manage.py migrate achievement
```

Verify that no errors happened when you did the command.

Once the bot has started, you should see achievements on the admin panel and the bot commands. 

If you don't see the bot commands, refresh your Discord by pressing CTRL + R. If you are on mobile, close and open your Discord app.

# Feel free to edit the code to fix mistakes or use anywhere. If you get any issues regarding the code, contact me in Discord or create a pull request in this repository.

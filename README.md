# Achievement-BD
A Achievement system For Ballsdex Bot

# How to install 

Step 1:Open Your `ballsdex/core/models.py`

And paste this code 

```py
class Achievement(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    description = fields.TextField()
    achievement_emoji_id = fields.BigIntField(
            null=True,
            description="Discord emoji ID for achievement"
        )
    required_balls = fields.ManyToManyField(
        "models.Ball", 
        related_name="achievements",
        through="achievements_required_balls", 
        forward_key="achievement_id",  
        backward_key="ball_id",  
    )

    class Meta:
        table = "achievements"  

    def __str__(self):
        return self.name

class PlayerAchievement(models.Model):
    id = fields.IntField(pk=True)
    player = fields.ForeignKeyField(
        "models.Player", 
        on_delete=fields.CASCADE,
        related_name="player_achievements",
        db_column="player_id"  
    )
    achievement = fields.ForeignKeyField(
        "models.Achievement",
        on_delete=fields.CASCADE,
        related_name="player_achievements",
        db_column="achievement_id"  
    )
    unlocked_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "bd_models_playerachievement"  
        unique_together = (("player", "achievement"),)

    def __str__(self):
        return f"{self.player} → {self.achievement}"


class AchievementRequiredBall(models.Model):
    achievement = fields.ForeignKeyField(
        "models.Achievement",
        related_name="achievement_links",
        on_delete=fields.CASCADE,
        db_column="achievement_id",
    )
    ball = fields.ForeignKeyField(
        "models.Ball",
        related_name="ball_links",
        on_delete=fields.CASCADE,
        db_column="ball_id",
    )

    class Meta:
        table = "achievements_required_balls"
        unique_together = (("achievement", "ball"),)

    def __str__(self) -> str:
        return str(self.pk)
 ```
Step 2: Open Your `admin_panel/bd_models/models.py`

At End of line paste This Code 

```py
class Achievement(models.Model):
    name = models.CharField(max_length=100, unique=True)
    achievement_emoji_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Discord emoji ID for achievement"
    )
    description = models.TextField()
    required_balls = models.ManyToManyField(
        Ball,
        related_name="achievements",
        help_text="Which countryballs you need to collect"
    )

    class Meta:
        managed = False
        db_table = "achievements"

    def __str__(self):
        return self.name


class PlayerAchievement(models.Model):
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="player_achievements"
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name="player_achievements"
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        unique_together = ("player", "achievement")
        verbose_name = "Player Achievement"
        verbose_name_plural = "Player Achievements"

    def __str__(self):
        return f"{self.player} → {self.achievement}"
```
Step 3: At `admin_panel/bd_models/admin`
 create a file named achievement.py Then Paste the Following Code 

```py
from typing import TYPE_CHECKING, Any  

from django.contrib import admin
from django.utils.safestring import mark_safe  
from ..models import Achievement, PlayerAchievement, Ball, Player

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "achievement_emoji_id")
    search_fields = ("name",)
    autocomplete_fields  = ("required_balls",)
    # alternatively, for large Ball sets you can use autocomplete:
    # autocomplete_fields = ("required_balls",)
    @admin.display(description="Emojis")
    def achievement_emoji(self, obj: Achievement):
        return mark_safe(
            f'<img src="https://cdn.discordapp.com/emojis/{obj.achievement_emoji_id}.png?size=40" '             
            f'title="ID: {obj.achievement_emoji_id}" />'
        )
@admin.register(PlayerAchievement)
class PlayerAchievementAdmin(admin.ModelAdmin):
    list_display = ("player", "achievement", "unlocked_at")
    list_filter = ("unlocked_at",)
    search_fields = ("player__discord_id", "achievement__name")
``` 

Step 4: at open your `ballsdex/core/utils/transformer.py` 

edit this line  
`ballsdex.core.models import` and include Achievement, there 

Then Edit The 

```py
  __all__ = (
    "BallTransform",
    "BallInstanceTransform",
    "SpecialTransform",
    "RegimeTransform",
    "EconomyTransform",
)
 ```
To include AchievementTransform 

```py
__all__ = (
    "BallTransform",
    "BallInstanceTransform",
    "SpecialTransform",
    "RegimeTransform",
    "EconomyTransform",
    "AchievementTransform",
)
```
Exact like this 

Then paste this code 

```py
class AchievementTransformer(TTLModelTransformer[Achievement]):
    name = "achievement"
    model = Achievement()

    def key(self, model: Achievement) -> str:
        return model.name  

    async def load_items(self) -> Iterable[Achievement]:
        return await Achievement.all()  

    async def transform(
        self, interaction: discord.Interaction["BallsDexBot"], value: str
    ) -> Optional[Achievement]:
        try:
            achievement = await super().transform(interaction, value)
            if achievement is None:
                raise ValueError("This achievement does not exist.")
            return achievement
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return None
```

> [!IMPORTANT]
> Be careful where you paste — do NOT just drop at the end of the file. Make sure it's after the last transformer class definition, but before the final end of the file.

Then At the End of Line add this 

```py
AchievementTransform = app_commands.Transform[Achievement, AchievementTransformer]
```
Step 6: Migration 
Create migration file by Running  

```py 
python3 manage.py makemigrations`
```

Then just migrate it with 

```py
Python3 manage.py migrate
```

Step 7: Installing The Cog 

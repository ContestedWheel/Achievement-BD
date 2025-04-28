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

from discord.ui import Button, View
from discord.ext import commands
from discord import app_commands
from typing import TYPE_CHECKING
import discord
 
from .models import AchievementRequiredBall
from .models import PlayerAchievement
from .models import Achievement as AchievementModel
from ballsdex.settings import settings 
from ballsdex.packages.countryballs.countryball import CountryBall
from .transformers import AchievementTransform, AchievementEnabledTransform
from ballsdex.core.utils.transformers import BallInstanceTransform
from ballsdex.core.utils.transformers import BallEnabledTransform
from ballsdex.core.utils.transformers import SpecialTransform, BallTransform
from ballsdex.core.utils.transformers import SpecialEnabledTransform
from ballsdex.core.utils.paginator import FieldPageSource, Pages
from ballsdex.core.bot import BallsDexBot

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

from ballsdex.core.models import (
    Ball,
    BallInstance,
    BlacklistedGuild,
    BlacklistedID,
    GuildConfig,
    Player,
    Trade,
    TradeObject,
    balls,
    specials,
)

class Achievement(commands.GroupCog):
    """
    Achievement commands.
    """

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot
        # Intents are automatically inherited from bot.intents
        # No need to redeclare unless doing special checks

    @app_commands.command()
    async def list(self, interaction: discord.Interaction):
        """
        List all available achievements
        """
        achievement = await AchievementModel.filter(enable=True).all()

        player, _ = await Player.get_or_create(discord_id=interaction.user.id)

        claimed_achievements = {
            pa.achievement_id 
            for pa in await PlayerAchievement.filter(player=player)
        }
                          
        if not achievement:
            await interaction.response.send_message(
                "There are no achievements currently registered in the admin panel.", 
                ephemeral=True
            )
            return

        entries = []
            
        for achievement in achievement:
            name = f"{achievement.name}"
            description = f"{achievement.description}" 
            emote = self.bot.get_emoji(achievement.achievement_emoji_id)
            
            if achievement.id in claimed_achievements:
                status = "✅"
            else:
                status = "❌" 
            
            entry = (f"{emote} {name}", f"Requirements: {description} {status}")
            entries.append(entry)
            # Modify this to change number shown in box
        per_page = 5
            
        source = FieldPageSource(entries, per_page=per_page, inline=False, clear_description=False)
        source.embed.description = (
            f"__**{settings.bot_name} achievementlist**__"
        )
        source.embed.colour = discord.Colour.blurple()
        source.embed.set_author(
            name=interaction.user.display_name, 
            icon_url=interaction.user.display_avatar.url
        )
            
        pages = Pages(source=source, interaction=interaction, compact=True)
        await pages.start()
    
        
    @app_commands.command()
    async def claim(
        self,
        interaction: discord.Interaction,
        achievement: AchievementEnabledTransform
    ):
        """
        claim an achievement.
        
        Parameters
        ----------
        achievement: AchievementEnabledTransform
            The the achievment you want to claim
        """
        player, _ = await Player.get_or_create(discord_id=interaction.user.id)  
        
        player_owned_ball_type_ids = await BallInstance.filter(player=player).values_list("ball__id", flat=True)  

        player_owned_ball_type_ids = list(player_owned_ball_type_ids)
        
        required_balls = await AchievementRequiredBall.filter(achievement_id=achievement.id).values_list('ball_id', flat=True)

        missing_ids = [
            ball_id
            for ball_id in required_balls
            if ball_id not in player_owned_ball_type_ids  
         ]  
                  
        if missing_ids:
            missing_balls = await Ball.filter(id__in=missing_ids).all()
            missing_countries = [Ball.country for Ball in missing_balls]
            await interaction.response.send_message(
                 f"❌ Missing required balls: {', '.join(missing_countries)}", ephemeral=True)
            return
                 
        if await PlayerAchievement.filter(player=player, achievement=achievement).exists():
            await interaction.response.send_message(
                f"Aww You Already claimed the achievement **{achievement.name}**!", ephemeral=True)        
            return
            
        await PlayerAchievement.create(player=player, achievement=achievement)
        await interaction.response.send_message(
            f"🎉Congrats, you claimed **{achievement.name}**!", ephemeral=True) 
            

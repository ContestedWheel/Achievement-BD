from discord.ui import Button, View
from discord.ext import commands
from discord import app_commands
from typing import TYPE_CHECKING
import discord
 
from .models import AchievementRequiredBall, AchievementRequiredSpecial
from .models import PlayerAchievement
from .models import Achievement as AchievementModel
from ballsdex.settings import settings 
from .transformers import AchievementTransform, AchievementEnabledTransform
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
    Special
)

class Achievement(commands.GroupCog):
    """
    Achievement commands.
    """

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot    
     
    @app_commands.command()
    async def list(self, interaction: discord.Interaction):
        """
        List all available achievements
        """ 
        await interaction.response.defer(ephemeral=True) 
     
        achievement = await AchievementModel.filter(enable=True).all()
                
        player, _ = await Player.get_or_create(discord_id=interaction.user.id)

        claimed_achievements = {
            pa.achievement_id 
            for pa in await PlayerAchievement.filter(player=player)
        }
                          
        if not achievement:
            await interaction.followup.send(
                "There are no achievements currently registered in the admin panel.", 
                ephemeral=True
            )
            return

        entries = []
            
        for achievement in achievement:
            name = f"{achievement.name}"
            description = f"{achievement.description}" 
            emote = self.bot.get_emoji(achievement.achievement_emoji_id) or ""
            
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
        await interaction.response.defer(ephemeral=True) 
     
        player, _ = await Player.get_or_create(discord_id=interaction.user.id)  

        if await PlayerAchievement.filter(player=player, achievement=achievement).exists():
            await interaction.followup.send(
                f"You Already claimed the achievement **{achievement.name}**!", ephemeral=True)        
            return
        
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
            await interaction.followup.send(
                 f"❌ Missing requirements: {', '.join(missing_countries)}", ephemeral=True)
            return
    
        player_ball_instances = await BallInstance.filter(player=player).prefetch_related("ball", "special")
    
        special_requirements = await AchievementRequiredSpecial.filter(
            achievement_id=achievement.id
        ).prefetch_related('special')
        
        required_pairs = list(zip(
           await AchievementRequiredBall.filter(achievement_id=achievement.id).values_list("ball_id", flat=True),
           await AchievementRequiredSpecial.filter(achievement_id=achievement.id).values_list("special_id", flat=True)
       ))     
       
        for ball_id, special_id in required_pairs:    
            if special_id is None:
                continue
                
            has_special_ball = False
            for instance in player_ball_instances:
                if instance.ball_id == ball_id and instance.special_id == special_id:
                    has_special_ball = True
                    break
        
            if not has_special_ball:
                required_ball = await Ball.get(id=ball_id)
                required_special = await Special.get(id=special_id) 
                await interaction.followup.send(
                    f"❌ Missing requirements: {required_ball.country} with {required_special}",
                    ephemeral=True
                )
                return 
             
        await PlayerAchievement.create(player=player, achievement=achievement)
        await interaction.followup.send(
            f"🎉Congrats, you claimed **{achievement.name}**!", ephemeral=True) 
            

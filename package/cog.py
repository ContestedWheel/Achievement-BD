from discord.ui import Button, View
from discord.ext import commands
from discord import app_commands
from typing import TYPE_CHECKING
import discord
import random

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

            entry_lines = [f"Requirements: {description} {status}"]

            rewards = await achievement.reward.all()
            if rewards:
                reward_names = [ball.country for ball in rewards]
                entry_lines.append(f"Rewards: {', '.join(reward_names)}")

            entry = (f"{emote} {name}", "\n".join(entry_lines))
            entries.append(entry)

        per_page = 10

        source = FieldPageSource(entries, per_page=per_page, inline=False, clear_description=False)
        source.embed.description = f"__**{settings.bot_name} achievementlist**__"
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
        Claim an achievement.

        Parameters
        ----------
        achievement: AchievementEnabledTransform
            The achievement you want to claim.
        """
        await interaction.response.defer(ephemeral=True)
        player, _ = await Player.get_or_create(discord_id=interaction.user.id) 
     
        if await PlayerAchievement.filter(player=player, achievement=achievement).exists():
            await interaction.followup.send( 
                f"You Already claimed the achievement **{achievement.name}**!",)
            return

        required_balls = await AchievementRequiredBall.filter(achievement_id=achievement.id).values_list('ball_id', flat=True)
        required_specials = await AchievementRequiredSpecial.filter(achievement_id=achievement.id).values_list("special_id", flat=True)

        required_pairs = list(zip(
            await AchievementRequiredBall.filter(achievement_id=achievement.id).values_list("ball_id", flat=True),
            await AchievementRequiredSpecial.filter(achievement_id=achievement.id).values_list("special_id", flat=True)
        ))

        player_qs = BallInstance.filter(player=player)
        if achievement.self_catch:
            player_qs = player_qs.filter(trade_player_id__isnull=True)
        player_instances = await player_qs.prefetch_related("ball", "special")

        player_owned_ball_ids = {bi.ball_id for bi in player_instances}
        missing_balls = [
            await Ball.get(id=ball_id)
            for ball_id in required_balls
            if ball_id not in player_owned_ball_ids
        ]

        if missing_balls:
            note = "(must be self-catched)" if achievement.self_catch else ""
            countries = ", ".join(ball.country for ball in missing_balls)
            await interaction.followup.send(
                f"❌ Missing required balls {note}: {countries}",
                ephemeral=True
            )
            return

        for ball_id, special_id in required_pairs:
            if special_id is None:
                continue
            if not any(
                bi.ball_id == ball_id and bi.special_id == special_id
                for bi in player_instances
            ):
                ball = await Ball.get(id=ball_id)
                special = await Special.get(id=special_id)
                await interaction.followup.send(
                    f"❌ Missing special countryball: {ball.country} with {special}",
                    ephemeral=True
                )
                return

        if not required_balls and len(required_specials) > 0:
            qs = player_qs.filter(special_id__in=required_specials)
            if achievement.self_catch:
                qs = qs.filter(trade_player_id__isnull=True)

            count = await qs.count()

            if count < achievement.required_quantity:
                specials = await Special.filter(id__in=required_specials).all()
                special_names = ", ".join(str(special) for special in specials)
                note = " (must be self-catched)" if achievement.self_catch else ""

                await interaction.followup.send(
                    f"❌ You need {achievement.required_quantity} of these specials{note}: {special_names}, but you have {count}.",
                    ephemeral=True
                )
                return

        rewards = await achievement.reward.all()
        for reward_ball in rewards:
            await BallInstance.create(
                player=player,
                ball=reward_ball,
                special=None,
                health_bonus=random.randint(-settings.max_attack_bonus, settings.max_attack_bonus),
                attack_bonus=random.randint(-settings.max_attack_bonus, settings.max_attack_bonus),
            )

        await PlayerAchievement.create(player=player, achievement=achievement)
        await interaction.followup.send(
            f"🎉 Congrats, you claimed **{achievement.name}**!",
            ephemeral=True
        )

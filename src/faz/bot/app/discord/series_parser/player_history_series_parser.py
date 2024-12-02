from typing import Any, Callable, Sequence
from uuid import UUID

import pandas as pd

from faz.bot.app.discord.embed.embed_field import EmbedField
from faz.bot.app.discord.select.player_history_data_options import PlayerHistoryDataOptions
from faz.bot.app.discord.series_parser._base_series_parser import BaseSeriesParser


class PlayerHistorySeriesParser(BaseSeriesParser):
    def __init__(self, character_labels: dict[str, str]) -> None:
        self._character_labels = character_labels
        self._categorical_parsers: dict[
            PlayerHistoryDataOptions,
            Callable[[pd.DataFrame], Sequence[EmbedField]],
        ] = {}
        self._numerical_parsers: dict[
            PlayerHistoryDataOptions,
            Callable[[pd.DataFrame, pd.DataFrame], Sequence[EmbedField]],
        ] = {}

        cat_prsr = self._categorical_parsers
        cat_prsr[PlayerHistoryDataOptions.GUILD] = self._parser_categorical_guild
        cat_prsr[PlayerHistoryDataOptions.USERNAME] = self._parser_categorical_username

        num_prsr = self._numerical_parsers
        num_prsr[PlayerHistoryDataOptions.ALL] = self._parser_numerical_all
        num_prsr[PlayerHistoryDataOptions.LEVEL] = self._parser_numerical_level
        num_prsr[PlayerHistoryDataOptions.WARS] = self._parser_numerical_wars
        num_prsr[PlayerHistoryDataOptions.PLAYTIME] = self._parser_numerical_playtime
        num_prsr[PlayerHistoryDataOptions.MOBS_KILLED] = self._parser_numerical_mobs_killed
        num_prsr[PlayerHistoryDataOptions.CHESTS_FOUND] = self._parser_numerical_chests_found
        num_prsr[PlayerHistoryDataOptions.LOGINS] = self._parser_numerical_logins
        num_prsr[PlayerHistoryDataOptions.DEATHS] = self._parser_numerical_deaths
        num_prsr[PlayerHistoryDataOptions.CHALLENGES] = self._parser_numerical_challenges
        num_prsr[PlayerHistoryDataOptions.PROFESSIONS] = self._parser_numerical_professions
        num_prsr[PlayerHistoryDataOptions.COMPLETIONS] = self._parser_numerical_completions

    def get_categorical_parser(
        self, id: PlayerHistoryDataOptions
    ) -> Callable[[pd.DataFrame], Sequence[EmbedField]]:
        ret = self._categorical_parsers.get(id, None)
        if ret is None:
            raise ValueError(f"Invalid mode: {id}")
        return ret

    def get_numerical_parser(
        self, id: PlayerHistoryDataOptions
    ) -> Callable[[pd.DataFrame, pd.DataFrame], Sequence[EmbedField]]:
        ret = self._numerical_parsers.get(id, None)
        if ret is None:
            raise ValueError(f"Invalid mode: {id}")
        return ret

    def _parser_numerical_all(
        self, player_df: pd.DataFrame, char_df: pd.DataFrame
    ) -> Sequence[EmbedField]:
        lines = {}
        if len(player_df) == 0:
            return []
        idxmin = player_df.iloc[player_df["datetime"].idxmin()]  # type: ignore
        idxmax = player_df.iloc[player_df["datetime"].idxmax()]  # type: ignore

        username1 = idxmin["username"]
        username2 = idxmax["username"]
        guildname1 = idxmin["guild_name"]
        guildname2 = idxmax["guild_name"]
        guildrank1 = idxmin["guild_rank"]
        guildrank2 = idxmax["guild_rank"]

        if not username1 == username2:
            lines["Username"] = f"{username1} -> {username2}"
        if not guildname1 == guildname2:
            lines["Guild"] = f"{guildname1} -> {guildname2}"
        if not guildrank1 == guildrank2:
            lines["Guild Rank"] = f"{guildrank1} -> {guildrank2}"

        for chuuid in pd.unique(char_df["character_uuid"]):
            char = char_df[char_df["character_uuid"] == chuuid]
            idxmin = char["datetime"].idxmin()  # type: ignore
            idxmax = char["datetime"].idxmax()  # type: ignore

            for name, col in char.items():  # type: ignore
                if name in ["character_uuid", "datetime", "unique_id"]:
                    continue
                before = col.iloc[idxmin]
                after = col.iloc[idxmax]

                if before == after:
                    continue

                diff = after - before
                line = self._format_number(diff)
                if diff > 0:
                    name: str
                    name = name.replace("_", " ").title()
                    lines[name] = f"+{line}"

        label_space = self._get_max_key_length(lines)
        desc = "\n".join(
            [self._diff_str_or_blank(value, label, label_space) for label, value in lines.items()]
        )
        ret = []
        self._add_embed_field(ret, "", desc)
        return ret

    def _parser_categorical_guild(self, df: pd.DataFrame) -> Sequence[EmbedField]:
        lines = []
        prev_value = None
        for _, row in df.iterrows():
            val = f"{row['guild_name']} ({row['guild_rank']})"
            if prev_value == val:
                continue
            prev_value = val
            formatted_ts = self._get_formatted_timestamp(row)
            line = f"{formatted_ts}: {val}"
            lines.append(line)
        desc = "\n".join(lines)
        ret = []
        self._add_embed_field(ret, "Guild", desc)
        return ret

    def _parser_categorical_username(self, df: pd.DataFrame) -> Sequence[EmbedField]:
        """username"""
        lines = []
        prev_value = None
        for _, row in df.iterrows():
            val = str(row["username"])
            if prev_value == val:
                continue
            prev_value = val
            formatted_ts = self._get_formatted_timestamp(row)
            line = f"{formatted_ts}: {val}"
            lines.append(line)
        desc = "\n".join(lines)
        ret = []
        self._add_embed_field(ret, "Username", desc)
        return ret

    def _common_numerical_parser(
        self,
        player_df: pd.DataFrame,
        char_df: pd.DataFrame,
        value_parser: Callable[[pd.Series], str],
        string_parser: Callable[[str, Any], str],
    ) -> Sequence[EmbedField]:
        ret: Sequence[EmbedField] = []
        for chuuid, chlabel in self._character_labels.items():
            char = char_df[char_df["character_uuid"] == UUID(chuuid).bytes]
            lines: list[str] = []
            prev_value = None
            for _, row in char.iterrows():
                value = value_parser(row)
                if prev_value == value:
                    continue
                prev_value = value
                timestamp = self._get_formatted_timestamp(row)
                line = string_parser(timestamp, value)
                lines.append(line)
            if prev_value is None:
                continue
            desc = "\n".join(lines)
            self._add_embed_field(ret, chlabel, desc)
        return ret

    def _parser_numerical_level(
        self,
        player_df: pd.DataFrame,
        char_df: pd.DataFrame,
    ) -> Sequence[EmbedField]:
        """level + (xp/100)"""
        # value_parser = lambda row: row["level"] + row["xp"] / 100
        value_parser = lambda row: row["level"]
        ret = self._common_numerical_parser(
            player_df, char_df, value_parser, self._common_numerical_float_string_parser
        )
        return ret

    def _parser_numerical_wars(
        self,
        player_df: pd.DataFrame,
        char_df: pd.DataFrame,
    ) -> Sequence[EmbedField]:
        """wars"""
        value_parser = lambda row: row["wars"]
        ret = self._common_numerical_parser(
            player_df, char_df, value_parser, self._common_numerical_int_string_parser
        )
        return ret

    def _parser_numerical_playtime(
        self,
        player_df: pd.DataFrame,
        char_df: pd.DataFrame,
    ) -> Sequence[EmbedField]:
        """playtime"""
        value_parser = lambda row: row["playtime"]
        ret = self._common_numerical_parser(
            player_df, char_df, value_parser, self._common_numerical_float_string_parser
        )
        return ret

    def _parser_numerical_mobs_killed(
        self,
        player_df: pd.DataFrame,
        char_df: pd.DataFrame,
    ) -> Sequence[EmbedField]:
        """mobs_killed"""
        value_parser = lambda row: row["mobs_killed"]
        ret = self._common_numerical_parser(
            player_df, char_df, value_parser, self._common_numerical_int_string_parser
        )
        return ret

    def _parser_numerical_chests_found(
        self,
        player_df: pd.DataFrame,
        char_df: pd.DataFrame,
    ) -> Sequence[EmbedField]:
        """chests_found"""
        value_parser = lambda row: row["chests_found"]
        ret = self._common_numerical_parser(
            player_df, char_df, value_parser, self._common_numerical_int_string_parser
        )
        return ret

    def _parser_numerical_logins(
        self,
        player_df: pd.DataFrame,
        char_df: pd.DataFrame,
    ) -> Sequence[EmbedField]:
        """logins"""
        value_parser = lambda row: row["logins"]
        ret = self._common_numerical_parser(
            player_df, char_df, value_parser, self._common_numerical_int_string_parser
        )
        return ret

    def _parser_numerical_deaths(
        self,
        player_df: pd.DataFrame,
        char_df: pd.DataFrame,
    ) -> Sequence[EmbedField]:
        """deaths"""
        value_parser = lambda row: row["deaths"]
        ret = self._common_numerical_parser(
            player_df, char_df, value_parser, self._common_numerical_int_string_parser
        )
        return ret

    def _parser_numerical_challenges(
        self,
        player_df: pd.DataFrame,
        char_df: pd.DataFrame,
    ) -> Sequence[EmbedField]:
        """hardcord, ultimate_ironman, ironman, craftsman, hunted"""
        return [EmbedField("", value="UNIMPLEMENTED")]

    def _parser_numerical_professions(
        self,
        player_df: pd.DataFrame,
        char_df: pd.DataFrame,
    ) -> Sequence[EmbedField]:
        """alchemism, armouring, cooking, jeweling, scribing, tailoring, weaponsmithing, woodworking, mining, woodcutting, farming, fishing"""
        return [EmbedField("", value="UNIMPLEMENTED")]

    def _parser_numerical_completions(
        self,
        player_df: pd.DataFrame,
        char_df: pd.DataFrame,
    ) -> Sequence[EmbedField]:
        """dungeon_completions, quest_completions, raid_completions"""
        return [EmbedField("", value="UNIMPLEMENTED")]

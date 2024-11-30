from typing import Any, Callable, Sequence
from uuid import UUID

import pandas as pd

from faz.bot.app.discord.embed_factory.embed_field import EmbedField
from faz.bot.app.discord.parser._base_field_parser import BaseFieldParser
from faz.bot.app.discord.select.player_history_data_option import PlayerHistoryDataOption
from faz.bot.app.discord.select.player_history_data_option import PlayerHistoryDataOptionType


class PlayerHistoryFieldParser(BaseFieldParser):
    def __init__(
        self,
        data_option: PlayerHistoryDataOption,
        player_df: pd.DataFrame,
        char_df: pd.DataFrame,
        character_labels: dict[str, str],
    ) -> None:
        self._data_option = data_option
        self._player_df = player_df
        self._char_df = char_df
        self._character_labels = character_labels

        self._categorical_parsers: dict[
            PlayerHistoryDataOption,
            Callable[[], Sequence[EmbedField]],
        ] = {}
        self._numerical_parsers: dict[
            PlayerHistoryDataOption,
            Callable[[], Sequence[EmbedField]],
        ] = {}

        cat_prsr = self._categorical_parsers
        cat_prsr[PlayerHistoryDataOption.GUILD] = self._parser_categorical_guild
        cat_prsr[PlayerHistoryDataOption.USERNAME] = self._parser_categorical_username

        num_prsr = self._numerical_parsers
        num_prsr[PlayerHistoryDataOption.ALL] = self._parser_numerical_all
        num_prsr[PlayerHistoryDataOption.LEVEL] = self._parser_numerical_level
        num_prsr[PlayerHistoryDataOption.WARS] = self._parser_numerical_wars
        num_prsr[PlayerHistoryDataOption.PLAYTIME] = self._parser_numerical_playtime
        num_prsr[PlayerHistoryDataOption.MOBS_KILLED] = self._parser_numerical_mobs_killed
        num_prsr[PlayerHistoryDataOption.CHESTS_FOUND] = self._parser_numerical_chests_found
        num_prsr[PlayerHistoryDataOption.LOGINS] = self._parser_numerical_logins
        num_prsr[PlayerHistoryDataOption.DEATHS] = self._parser_numerical_deaths
        num_prsr[PlayerHistoryDataOption.CHALLENGES] = self._parser_numerical_challenges
        num_prsr[PlayerHistoryDataOption.PROFESSIONS] = self._parser_numerical_professions
        num_prsr[PlayerHistoryDataOption.COMPLETIONS] = self._parser_numerical_completions

    def get_fields(self) -> Sequence[EmbedField]:
        if self._data_option.type == PlayerHistoryDataOptionType.CATEGORICAL:
            parser = self._get_categorical_parser(self._data_option)
        else:
            parser = self._get_numerical_parser(self._data_option)
        return parser()

    def _get_categorical_parser(
        self, data: PlayerHistoryDataOption
    ) -> Callable[[], Sequence[EmbedField]]:
        ret = self._categorical_parsers.get(data, None)
        if ret is None:
            raise ValueError(f"Invalid mode: {data}")
        return ret

    def _get_numerical_parser(
        self, data: PlayerHistoryDataOption
    ) -> Callable[[], Sequence[EmbedField]]:
        ret = self._numerical_parsers.get(data, None)
        if ret is None:
            raise ValueError(f"Invalid data: {data}")
        return ret

    def _parser_numerical_all(
        self,
    ) -> Sequence[EmbedField]:
        lines = {}
        if len(self._player_df) == 0:
            return []
        idxmin = self._player_df.iloc[self._player_df["datetime"].idxmin()]  # type: ignore
        idxmax = self._player_df.iloc[self._player_df["datetime"].idxmax()]  # type: ignore

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

        for chuuid in pd.unique(self._char_df["character_uuid"]):
            char = self._char_df[self._char_df["character_uuid"] == chuuid]
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

    def _parser_categorical_guild(self) -> Sequence[EmbedField]:
        lines = []
        prev_value = None
        for _, row in self._player_df.iterrows():
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

    def _parser_categorical_username(self) -> Sequence[EmbedField]:
        """username"""
        lines = []
        prev_value = None
        for _, row in self._player_df.iterrows():
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
        value_parser: Callable[[pd.Series], str],
        string_parser: Callable[[str, Any], str],
    ) -> Sequence[EmbedField]:
        ret: Sequence[EmbedField] = []
        for chuuid, chlabel in self._character_labels.items():
            char = self._char_df[self._char_df["character_uuid"] == UUID(chuuid).bytes]
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
    ) -> Sequence[EmbedField]:
        """level + (xp/100)"""
        # value_parser = lambda row: row["level"] + row["xp"] / 100
        value_parser = lambda row: row["level"]
        ret = self._common_numerical_parser(
            value_parser, self._common_numerical_float_string_parser
        )
        return ret

    def _parser_numerical_wars(
        self,
    ) -> Sequence[EmbedField]:
        """wars"""
        value_parser = lambda row: row["wars"]
        ret = self._common_numerical_parser(value_parser, self._common_numerical_int_string_parser)
        return ret

    def _parser_numerical_playtime(
        self,
    ) -> Sequence[EmbedField]:
        """playtime"""
        value_parser = lambda row: row["playtime"]
        ret = self._common_numerical_parser(
            value_parser, self._common_numerical_float_string_parser
        )
        return ret

    def _parser_numerical_mobs_killed(
        self,
    ) -> Sequence[EmbedField]:
        """mobs_killed"""
        value_parser = lambda row: row["mobs_killed"]
        ret = self._common_numerical_parser(value_parser, self._common_numerical_int_string_parser)
        return ret

    def _parser_numerical_chests_found(
        self,
    ) -> Sequence[EmbedField]:
        """chests_found"""
        value_parser = lambda row: row["chests_found"]
        ret = self._common_numerical_parser(value_parser, self._common_numerical_int_string_parser)
        return ret

    def _parser_numerical_logins(
        self,
    ) -> Sequence[EmbedField]:
        """logins"""
        value_parser = lambda row: row["logins"]
        ret = self._common_numerical_parser(value_parser, self._common_numerical_int_string_parser)
        return ret

    def _parser_numerical_deaths(
        self,
    ) -> Sequence[EmbedField]:
        """deaths"""
        value_parser = lambda row: row["deaths"]
        ret = self._common_numerical_parser(value_parser, self._common_numerical_int_string_parser)
        return ret

    def _parser_numerical_challenges(
        self,
    ) -> Sequence[EmbedField]:
        """hardcord, ultimate_ironman, ironman, craftsman, hunted"""
        return [EmbedField("", value="UNIMPLEMENTED")]

    def _parser_numerical_professions(
        self,
    ) -> Sequence[EmbedField]:
        """alchemism, armouring, cooking, jeweling, scribing, tailoring, weaponsmithing, woodworking, mining, woodcutting, farming, fishing"""
        return [EmbedField("", value="UNIMPLEMENTED")]

    def _parser_numerical_completions(
        self,
    ) -> Sequence[EmbedField]:
        """dungeon_completions, quest_completions, raid_completions"""
        return [EmbedField("", value="UNIMPLEMENTED")]

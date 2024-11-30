from typing import Callable, Sequence
from uuid import UUID

import pandas as pd

from faz.bot.app.discord.embed_factory.embed_field import EmbedField
from faz.bot.app.discord.parser._base_field_parser import BaseFieldParser
from faz.bot.app.discord.select.member_history_data_option import MemberHistoryDataOption
from faz.bot.app.discord.select.member_history_mode_option import MemberHistoryModeOption


class MemberHistoryFieldParser(BaseFieldParser):
    def __init__(
        self,
        data: MemberHistoryDataOption,
        mode: MemberHistoryModeOption,
        char_df: pd.DataFrame,
        member_df: pd.DataFrame,
        character_labels: dict[str, str],
    ) -> None:
        self._data = data
        self._mode = mode
        self._char_df = char_df
        self._member_df = member_df
        self._character_labels = character_labels

        self._historical_parsers: dict[
            MemberHistoryDataOption,
            Callable[[], Sequence[EmbedField]],
        ] = {}

        hist_prsr = self._historical_parsers
        hist_prsr[MemberHistoryDataOption.WARS] = self._parser_historical_wars
        hist_prsr[MemberHistoryDataOption.XP_CONTRIBUTION] = self._parser_historical_contributed

    def get_fields(
        self,
    ) -> Sequence[EmbedField]:
        if self._mode == MemberHistoryModeOption.OVERALL:
            parser = self._parser_overall
        elif self._mode == MemberHistoryModeOption.HISTORICAL:
            parser = self._historical_parsers[self._data]
        return parser()

    def _parser_overall(
        self,
    ) -> Sequence[EmbedField]:
        ret: Sequence[EmbedField] = []

        lines = {}

        self._char_df.replace("", "None", inplace=True)
        self._member_df.replace("", "None", inplace=True)

        if len(self._char_df) == 0 and len(self._member_df) == 0:
            return ret

        earliest_char: pd.Series = self._char_df.iloc[self._char_df["datetime"].idxmin()]  # type: ignore
        latest_char: pd.Series = self._char_df.iloc[self._char_df["datetime"].idxmax()]  # type: ignore

        wars1 = earliest_char["wars"]
        wars2 = latest_char["wars"]

        if wars1 != wars2:
            lines["Wars"] = f"{wars1} -> {wars2}"

        earliest_member: pd.Series = self._member_df.iloc[self._member_df["datetime"].idxmin()]  # type: ignore
        latest_member: pd.Series = self._member_df.iloc[self._member_df["datetime"].idxmax()]  # type: ignore

        xp1 = earliest_member["contributed"]
        xp2 = latest_member["contributed"]

        if xp1 != xp2:
            lines["XP Contributed"] = f"{xp1} -> {xp2}"

        label_space = self._get_max_key_length(lines)
        desc = "\n".join(
            [self._diff_str_or_blank(value, label, label_space) for label, value in lines.items()]
        )
        ret = []
        self._add_embed_field(ret, "", desc)
        return ret

    def _parser_historical_wars(
        self,
    ) -> Sequence[EmbedField]:
        ret: Sequence[EmbedField] = []
        for chuuid, chlabel in self._character_labels.items():
            char = self._char_df[self._char_df["character_uuid"] == UUID(chuuid).bytes]
            lines: list[str] = []
            prev_value = None
            for _, row in char.iterrows():
                value = row["wars"]
                if prev_value == value:
                    continue
                prev_value = value
                timestamp = self._get_formatted_timestamp(row)
                line = f"{timestamp}: {value}"
                lines.append(line)
            if prev_value is None:
                continue
            desc = "\n".join(lines)
            self._add_embed_field(ret, chlabel, desc)
        return ret

    def _parser_historical_contributed(
        self,
    ) -> Sequence[EmbedField]:
        ret: Sequence[EmbedField] = []
        lines: list[str] = []
        prev_value = None
        for _, row in self._member_df.iterrows():
            value = row["contributed"]
            if prev_value == value:
                continue
            prev_value = value
            timestamp = self._get_formatted_timestamp(row)
            line = f"{timestamp}: {value}"
            lines.append(line)
            if prev_value is None:
                continue
        desc = "\n".join(lines)
        self._add_embed_field(ret, "XP Contributed", desc)
        return ret

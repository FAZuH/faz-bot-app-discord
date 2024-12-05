from __future__ import annotations

from typing import Any, Iterable, Self, TYPE_CHECKING

from nextcord import Embed

if TYPE_CHECKING:
    from nextcord import Colour
    from nextcord import Interaction

    from faz.bot.app.discord.embed.embed_field import EmbedField


class EmbedBuilder:
    def __init__(
        self, interaction: Interaction[Any] | None = None, initial_embed: Embed | None = None
    ) -> None:
        """
        Initialize the EmbedBuilder.

        Args:
            interaction (Interaction[Any], optional): The interaction associated with the embed. Defaults to None.
            initial_embed (Embed, optional): An initial embed to start with. If None, creates a new Embed. Defaults to None.
        """
        self._initial_embed = initial_embed or Embed()
        self._embed = self._initial_embed.copy()
        self._interaction = interaction

    def add_embed_field(self, field: EmbedField) -> Self:
        """
        Adds a field to the embed.

        Args:
            name (str): The name of the field.
            value (str): The value of the field.
            inline (bool, optional): Whether the field should be displayed inline. Defaults to False.

        Returns:
            Self: The instance of the embed builder to allow method chaining.
        """
        self._embed.add_field(name=field.name, value=field.value, inline=field.inline)
        return self

    def add_field(self, name: str, value: str, inline: bool = False) -> Self:
        """
        Adds a field to the embed.

        Args:
            name (str): The name of the field.
            value (str): The value of the field.
            inline (bool, optional): Whether the field should be displayed inline. Defaults to False.

        Returns:
            Self: The instance of the embed builder to allow method chaining.
        """
        self._embed.add_field(name=name, value=value, inline=inline)
        return self

    def add_fields(self, fields: Iterable[EmbedField]) -> Self:
        """
        Adds multiple fields to the embed.

        Args:
            fields (list[EmbedField]): A list of fields to add to the embed.

        Returns:
            Self: The instance of the embed builder to allow method chaining.
        """
        for field in fields:
            self.add_embed_field(field)
        return self

    def set_colour(self, colour: Colour | int) -> Self:
        """
        Sets the color of the embed.

        Args:
            colour (Colour | int): The color to set for the embed.

        Returns:
            Self: The instance of the embed builder to allow method chaining.
        """
        self._embed.colour = colour
        return self

    def set_footer(self, text: str | None = None, icon_url: str | None = None) -> Self:
        """
        Sets the footer of the embed.

        Args:
            text (str, optional): The footer text. Defaults to None.
            icon_url (str, optional): The URL of the footer icon. Defaults to None.

        Returns:
            Self: The instance of the embed builder to allow method chaining.
        """
        self._embed.set_footer(text=text, icon_url=icon_url)
        return self

    def set_thumbnail(self, url: str) -> Self:
        """
        Sets the thumbnail of the embed.

        Args:
            url (str): The URL of the thumbnail image.

        Returns:
            Self: The instance of the embed builder to allow method chaining.
        """
        self._embed.set_thumbnail(url)
        return self

    def set_title(self, title: str) -> Self:
        """
        Sets the title of the embed.

        Args:
            title (str): The title to set for the embed.

        Returns:
            Self: The instance of the embed builder to allow method chaining.
        """
        self._embed.title = title
        return self

    def set_description(self, description: str) -> Self:
        """
        Sets the description of the embed.

        Args:
            description (str): The description to set for the embed.

        Returns:
            Self: The instance of the embed builder to allow method chaining.
        """
        self._embed.description = description
        return self

    def build(self) -> Embed:
        """
        Finalize the embed construction, and return the finished product.

        Returns:
            Embed: The fully constructed embed object.
        """
        self._add_author()
        return self._embed

    def reset(self) -> Self:
        """
        Resets the embed to its initial state.

        Returns:
            Self: The instance of the embed builder to allow method chaining.
        """
        self._embed = self._initial_embed.copy()
        return self

    def get_embed(self) -> Embed:
        """
        Get the embed without finalizing it.

        Returns:
            Embed: The current embed object.
        """
        return self._embed

    def set_builder_initial_embed(self, embed: Embed) -> Self:
        """
        Sets the initial embed state for this builder.

        Args:
            embed (Embed): The embed to set as the initial state.

        Returns:
            Self: The instance of the embed builder to allow method chaining.
        """
        self._initial_embed = embed
        return self

    def _add_author(self) -> Self:
        """
        Adds author information to the embed.

        Adds the user's display name and avatar to the embed, along with the interaction's timestamp.

        Returns:
            Self: The instance of the embed builder to allow method chaining.

        Raises:
            AssertionError: If the user is None.
        """
        user = self.interaction.user
        assert user, "User is None. Who is calling this command?"
        self._embed.set_author(
            name=user.display_name,
            icon_url=user.display_avatar.url,
        )
        self._embed.timestamp = self.interaction.created_at
        return self

    @property
    def interaction(self) -> Interaction[Any]:
        """
        Returns the interaction associated with this embed.

        Returns:
            Interaction[Any]: The interaction object.

        Raises:
            ValueError: If interaction is not set.
        """
        ret = self._interaction
        if ret is None:
            raise ValueError("Interaction is not set.")
        return ret

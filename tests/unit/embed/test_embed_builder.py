import datetime

from nextcord import Colour
from nextcord import Embed
import pytest

from faz.bot.app.discord.embed.builder.embed_builder import EmbedBuilder


@pytest.fixture
def mock_interaction():
    class MockUser:
        display_name = "TestUser"
        display_avatar = type("Avatar", (), {"url": "http://example.com/avatar.png"})

    class MockInteraction:
        user = MockUser()
        created_at = datetime.datetime.fromtimestamp(10).replace(tzinfo=datetime.timezone.utc)

    return MockInteraction()


@pytest.fixture
def mock_embed_field():
    class MockEmbedField:
        name = "Field1"
        value = "Value1"
        inline = True

    return MockEmbedField()


@pytest.fixture
def embed_builder(mock_interaction):
    return EmbedBuilder(interaction=mock_interaction)


def test_add_field(embed_builder, mock_embed_field):
    embed_builder.add_field(mock_embed_field)
    embed = embed_builder.get_embed()
    assert embed.fields[0].name == "Field1"
    assert embed.fields[0].value == "Value1"
    assert embed.fields[0].inline is True


def test_set_colour(embed_builder):
    embed_builder.set_colour(Colour.blue())
    embed = embed_builder.get_embed()
    assert embed.colour == Colour.blue()


def test_set_footer(embed_builder):
    embed_builder.set_footer(text="Footer text", icon_url="http://example.com/icon.png")
    embed = embed_builder.get_embed()
    assert embed.footer.text == "Footer text"
    assert embed.footer.icon_url == "http://example.com/icon.png"


def test_set_thumbnail(embed_builder):
    embed_builder.set_thumbnail(url="http://example.com/thumbnail.png")
    embed = embed_builder.get_embed()
    assert embed.thumbnail.url == "http://example.com/thumbnail.png"


def test_set_title(embed_builder):
    embed_builder.set_title(title="Test Title")
    embed = embed_builder.get_embed()
    assert embed.title == "Test Title"


def test_set_description(embed_builder):
    embed_builder.set_description(description="Test Description")
    embed = embed_builder.get_embed()
    assert embed.description == "Test Description"


def test_build(embed_builder, mock_embed_field):
    embed_builder.set_title("Title").set_description("Description").add_field(mock_embed_field)
    embed = embed_builder.build()
    assert embed.title == "Title"
    assert embed.description == "Description"
    assert embed.fields[0].name == "Field1"
    assert embed.fields[0].value == "Value1"
    assert embed.fields[0].inline is True
    assert embed.timestamp == datetime.datetime.fromtimestamp(10).replace(
        tzinfo=datetime.timezone.utc
    )


def test_reset_embed(embed_builder):
    embed_builder.set_title("Title")
    embed_builder.reset()
    embed = embed_builder.get_embed()
    assert embed.title is None


def test_set_builder_initial_embed(embed_builder):
    initial_embed = Embed(title="Initial Title")
    embed_builder.set_builder_initial_embed(initial_embed)
    embed_builder.reset()
    embed = embed_builder.get_embed()
    assert embed.title == "Initial Title"


def test_add_author(embed_builder):
    embed_builder._add_author()
    embed = embed_builder.get_embed()
    assert embed.author.name == "TestUser"
    assert embed.author.icon_url == "http://example.com/avatar.png"


def test_interaction_property(embed_builder, mock_interaction):
    assert embed_builder.interaction == mock_interaction
    embed_builder._interaction = None
    with pytest.raises(ValueError):
        _ = embed_builder.interaction

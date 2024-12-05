from unittest.mock import Mock

from nextcord import Embed
import pytest

from faz.bot.app.discord.embed.builder.embed_builder import EmbedBuilder
from faz.bot.app.discord.embed.director._base_pagination_embed_director import (
    BasePaginationEmbedDirector,
)


class MockTestPaginationEmbedDirector(BasePaginationEmbedDirector[str]):
    async def setup(self):
        pass

    def _process_page_items(self, items):
        for item in items:
            self.embed_builder.add_field(Mock(name=item, value=item))


@pytest.fixture
def embed_builder():
    builder = Mock(spec_set=EmbedBuilder)
    builder.build.return_value = Embed()
    return builder


@pytest.fixture
def pagination_embed_director(embed_builder):
    return MockTestPaginationEmbedDirector(embed_builder, items_per_page=3)


def test_set_items(pagination_embed_director):
    items = ["item1", "item2", "item3"]
    pagination_embed_director.set_items(items)
    assert pagination_embed_director.items == items


def test_set_page(pagination_embed_director):
    pagination_embed_director.set_items(["item1", "item2", "item3"])
    pagination_embed_director.set_page(1)
    assert pagination_embed_director.current_page == 1

    with pytest.raises(ValueError):
        pagination_embed_director.set_page(0)


def test_get_items(pagination_embed_director):
    items = ["item1", "item2", "item3", "item4", "item5"]
    pagination_embed_director.set_items(items)
    pagination_embed_director.set_page(1)
    assert (
        pagination_embed_director.get_items() == items[: pagination_embed_director.items_per_page]
    )

    pagination_embed_director.set_page(2)
    assert (
        pagination_embed_director.get_items() == items[pagination_embed_director.items_per_page :]
    )


def test_construct_page(pagination_embed_director):
    items = ["item1", "item2", "item3"]
    pagination_embed_director.set_items(items)
    embed = pagination_embed_director.construct_page(1)
    assert isinstance(embed, Embed)
    assert pagination_embed_director.embed_builder.reset.called
    assert pagination_embed_director.embed_builder.build.called


def test_add_empty_field(pagination_embed_director):
    pagination_embed_director._add_empty_field("Empty")
    assert pagination_embed_director.embed_builder.add_field.called


def test_add_page_field(pagination_embed_director):
    pagination_embed_director._add_page_field()
    assert pagination_embed_director.embed_builder.add_field.called


def test_check_page(pagination_embed_director):
    pagination_embed_director.set_items(["item1", "item2", "item3"])
    assert pagination_embed_director._check_page(1)
    assert not pagination_embed_director._check_page(0)
    assert not pagination_embed_director._check_page(2)


def test_page_count(pagination_embed_director):
    pagination_embed_director.set_items(["item1", "item2", "item3"])
    assert pagination_embed_director.page_count == 1
    pagination_embed_director.set_items(["item1"] * 21)
    assert pagination_embed_director.page_count == 7

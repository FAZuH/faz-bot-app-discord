from faz.bot.app.discord.embed.builder.description_builder import DescriptionBuilder


def test_add_line():
    builder = DescriptionBuilder()
    builder.add_line("key1", "value1")
    assert builder.build() == "`key1 :` value1"


def test_insert_line():
    builder = DescriptionBuilder()
    builder.add_line("key1", "value1")
    builder.insert_line(0, "key0", "value0")
    assert builder.build() == "`key0 :` value0\n`key1 :` value1"


def test_remove_line():
    builder = DescriptionBuilder([("key1", "value1"), ("key2", "value2")])
    builder.remove_line(0)
    assert builder.build() == "`key2 :` value2"


def test_remove_line_by_key():
    builder = DescriptionBuilder([("key1", "value1"), ("key2", "value2")])
    builder.remove_line_by_key("key1")
    assert builder.build() == "`key2 :` value2"


def test_reset():
    builder = DescriptionBuilder([("key1", "value1")])
    builder.add_line("key2", "value2")
    builder.reset()
    assert builder.build() == "`key1 :` value1"


def test_set_builder_initial_lines():
    builder = DescriptionBuilder()
    builder.set_builder_initial_lines([("key1", "value1")])
    builder.reset()
    assert builder.build() == "`key1 :` value1"


def test_build():
    builder = DescriptionBuilder([("key1", "value1"), ("key2", "value2")])
    assert builder.build() == "`key1 :` value1\n`key2 :` value2"

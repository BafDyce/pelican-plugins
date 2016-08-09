import os

from pelican import signals
from pelican.readers import Markdown, MarkdownReader
from pelican.utils import pelican_open
from jinja2 import Environment, FileSystemLoader, ChoiceLoader


class JinjaMarkdownReader(MarkdownReader):

    def __init__(self, *args, **kwargs):
        super(JinjaMarkdownReader, self).__init__(*args, **kwargs)

        # will look first in 'JINJA2CONTENT_TEMPLATES', by default the
        # content root path, then in the theme's templates
        local_templates_dir = self.settings.get('JINJA2CONTENT_TEMPLATES', '.')
        local_templates_dir = os.path.join(self.settings['PATH'], local_templates_dir)
        theme_templates_dir = os.path.join(self.settings['THEME'], 'templates')
        loader = ChoiceLoader([
            FileSystemLoader(local_templates_dir),
            FileSystemLoader(theme_templates_dir)])

        self.env = Environment(trim_blocks=True, lstrip_blocks=True,
                               extensions=self.settings['JINJA_EXTENSIONS'],
                               loader=loader)


    def read(self, source_path):
        """Parse content and metadata of markdown files.

        Rendering them as jinja templates first.

        """
        self._source_path = source_path
        self._md = Markdown(extensions=self.extensions)

        with pelican_open(source_path) as text:
            text = self.env.from_string(text).render()
            content = self._md.convert(text)

        metadata = self._parse_metadata(self._md.Meta)
        return content, metadata


def add_reader(readers):
    for ext in MarkdownReader.file_extensions:
        readers.reader_classes[ext] = JinjaMarkdownReader


def register():
    signals.readers_init.connect(add_reader)

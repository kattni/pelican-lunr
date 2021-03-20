import json
import os

from pelican import generators, writers, logger
from pelican.contents import Article
from pelican.plugins import signals
from bs4 import BeautifulSoup
from pelican.utils import is_selected_for_writing, sanitised_join

from webassets.filter import register_filter
from dukpy.webassets import BabelJSX


class LunrGenerator(generators.ArticlesGenerator):

    def generate_context(self):
        super(LunrGenerator, self).generate_context()
        index_data = []
        article: Article
        for n, article in enumerate(self.articles):
            index_data.append({
                "title": article.title,
                "summary": BeautifulSoup(article.summary, features='html.parser').get_text(),
                "url": os.path.join(self.context['SITEURL'], article.url),
                "date": article.date.strftime("%A %Y %B %d %H:%M"),
                "slug": article.slug,
                "ref": n,
                "tags": [{"name": tag.name, "url": tag.url} for tag in article.tags]
            })
        self.context['index_data'] = index_data

    def generate_output(self, writer):
        writer.write_js(self.settings['LUNR_INDEX_FILE'],
                        self.context,
                        self.context)


def get_generators(pelican_object):
    return LunrGenerator


class LunrWriter(writers.Writer):

    def write_js(self, name, context, override_output=False):
        """Render the template and write the file.

        :param name: name of the index file to output
        :param context: dict to pass to the templates.
        :param override_output: boolean telling if we can override previous
            output with the same name (and if next files written with the same
            name should be skipped to keep that one)
        """

        if name is False or \
           name == "" or \
           not is_selected_for_writing(self.settings,
                                       os.path.join(self.output_path, name)):
            return
        elif not name:
            # other stuff, just return for now
            return

        def _write_file(output_path, name, override):
            """Write the js file."""
            output = 'var documents = ' + json.dumps(context['index_data'], indent=2) + ";"
            path = sanitised_join(output_path, name)

            try:
                os.makedirs(os.path.dirname(path))
            except Exception:
                pass

            with self._open_w(path, 'utf-8', override=override) as f:
                f.write(output)
            logger.info('Writing %s', path)

            # Send a signal to say we're writing a file with some specific
            # local context.
            signals.content_written.send(path, context=context)

        _write_file(self.output_path, name, override_output)


def get_writers(pelican_object):
    register_filter(BabelJSX)
    return LunrWriter



def register():
    signals.get_generators.connect(get_generators)
    signals.get_writer.connect(get_writers)

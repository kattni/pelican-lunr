"""
Pelican Lunr search plugin.
"""
import json
import os

from bs4 import BeautifulSoup
from lunr import lunr
from pelican import generators, logger, writers
from pelican.contents import Article
from pelican.plugins import signals
from pelican.utils import is_selected_for_writing, sanitised_join


class LunrGenerator(generators.ArticlesGenerator):
    """
    Lunr Index generator.
    """

    def generate_context(self):
        """
        Adds document and index data to the context.
        """
        super().generate_context()
        index_data = []
        article: Article
        for num, article in enumerate(self.articles):
            index_data.append(
                {
                    "title": article.title,
                    "summary": BeautifulSoup(
                        article.summary, features="html.parser"
                    ).get_text(),
                    "url": os.path.join(self.context["SITEURL"], article.url),
                    "date": article.date.strftime("%A %Y %B %d %H:%M"),
                    "slug": article.slug,
                    "body": BeautifulSoup(
                        article.content, features="html.parser"
                    ).get_text(),
                    "ref": num,
                    "tags": [
                        {"name": tag.name, "url": tag.url} for tag in article.tags
                    ],
                }
            )
        self.context["index_data"] = index_data

    def generate_output(self, writer):
        """
        Calls the Lunr index generator.
        """
        writer.write_js(self.settings["LUNR_INDEX_FILE"], self.context, self.context)


class LunrWriter(writers.Writer):
    """
    Generate a serialized Lunr index and document hit metadata.
    """

    def write_js(self, name, context, override_output=False):
        """Render the template and write the file.

        :param name: name of the index file to output
        :param context: dict to pass to the templates.
        :param override_output: boolean telling if we can override previous
            output with the same name (and if next files written with the same
            name should be skipped to keep that one)
        """

        if (
            name is False
            or name == ""
            or not is_selected_for_writing(
                self.settings, os.path.join(self.output_path, name)
            )
        ):
            return

        if not name:
            return

        def _write_file(output_path, name, override):
            """Write the js file."""

            # output = 'var documents = ' + json.dumps(context['index_data'], indent=2) + ";"
            path = sanitised_join(output_path, name)

            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path))

            idx = lunr(
                ref="ref",
                fields=[
                    {"field_name": "title", "boost": 10},
                    {"field_name": "summary", "boost": 2},
                    "body",
                    "tags",
                ],
                documents=context["index_data"],
            )

            with self._open_w(path, "utf-8", override=override) as handle:
                handle.write("const lunrSerializedIdx = ")
                handle.write(json.dumps(idx.serialize()))
                handle.write(";\n")
                handle.write("const lunrDocuments = ")

                def remove_body():
                    for doc in context["index_data"]:
                        cleaned_doc = dict(doc)
                        del cleaned_doc["body"]
                        yield cleaned_doc

                handle.write(json.dumps(doc for doc in remove_body()))
                handle.write(";\n")
            logger.info("Writing %s", path)

            # Send a signal to say we're writing a file with some specific
            # local context.
            signals.content_written.send(path, context=context)

        if not context["index_data"]:
            return
        _write_file(self.output_path, name, override_output)


def register():
    """
    Registers signals with Pelican.
    """
    signals.get_generators.connect(lambda: LunrGenerator)
    signals.get_writer.connect(lambda: LunrWriter)

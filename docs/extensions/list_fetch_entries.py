from __future__ import annotations

import importlib
import importlib.util
import sys, os
from yarl import URL
from pathlib import Path
from typing import List

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

class ListEntriesPlaceholder(nodes.General, nodes.Element):
    pass


class ListEntryNode(nodes.General, nodes.Element):
    pass


class EntryNode(nodes.TextElement):
    pass


class LinkNode(nodes.TextElement):
    pass

class PlainTextNode(nodes.TextElement):
    pass

class PyListentrys(SphinxDirective):
    required_arguments = 1

    def run(self) -> List[ListEntriesPlaceholder]:
        node = ListEntriesPlaceholder("", loader_path=self.arguments[0])
        return [node]


def visit_entry_node(self, node: EntryNode) -> None:
    self.body.append(self.starttag(node, "li"))


def depart_entry_node(self, node: EntryNode) -> None:
    self.body.append("</li>")


def visit_list_entry_node(self, node: ListEntryNode) -> None:
    self.body.append(self.starttag(node, "ul"))


def depart_list_entry_node(self, node: ListEntryNode) -> None:
    self.body.append("</ul>")


def visit_link_node(self, node: LinkNode) -> None:
    self.body.append(self.starttag(node, "a", href=node.rawsource))


def depart_link_node(self, node: LinkNode) -> None:
    self.body.append("</a>")

def visit_plain_text_node(self, node: PlainTextNode) -> None:
    self.body.append(self.starttag(node, "span"))

def depart_plain_text_node(self, node: PlainTextNode) -> None:
    self.body.append("</span>")


def process_list_entrys(app: Sphinx, doctree: nodes.Node, fromdocname: str) -> None:
    ext_dir = Path(os.path.dirname(__file__))
    root_dir = Path(*ext_dir.parts[0:-2])
    sys.path.append(str(root_dir.resolve()))
    
    for node in doctree.traverse(ListEntriesPlaceholder):
        relative_raw_loader_path = node.attributes['loader_path']
        loader_path = root_dir / relative_raw_loader_path

        spec = importlib.util.spec_from_file_location(
            relative_raw_loader_path, str(loader_path)
        )
        assert spec
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)

        entry_classes = module.fetch()
        parser_url_format: str | None = getattr(module, "parser_url_format", None)
    
        container = ListEntryNode()
        for entry in entry_classes:
            entry_url = getattr(entry, "base_url", None)
            entry_node = EntryNode()
            if entry_url:
                entry_node.append(LinkNode(entry_url, entry_url))
            else:
                entry_node.append(PlainTextNode(entry.typename, entry.typename))
            
            if parser_url_format:
                entry_node.append(PlainTextNode(" - ", " - "))
                entry_node.append(LinkNode(parser_url_format.format(entry=entry), "Parser"))

            container.append(entry_node)
        node.replace_self([container])


def setup(app: Sphinx):
    app.add_directive("list-entries", PyListentrys)
    app.add_node(EntryNode, html=(visit_entry_node, depart_entry_node))
    app.add_node(
        ListEntryNode, html=(visit_list_entry_node, depart_list_entry_node)
    )
    app.add_node(LinkNode, html=(visit_link_node, depart_link_node))
    app.add_node(PlainTextNode, html=(visit_plain_text_node, depart_plain_text_node))
    app.add_node(ListEntriesPlaceholder)
    app.connect("doctree-resolved", process_list_entrys)
    return {"parallel_read_safe": True}

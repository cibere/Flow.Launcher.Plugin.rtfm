from __future__ import annotations

import importlib
import inspect
import re, sys, os
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple
from pathlib import Path
from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec
import importlib.util

class ListPresetsPlaceholder(nodes.General, nodes.Element):
    pass

class ListPresetsNode(nodes.General, nodes.Element):
    pass

class PresetNode(nodes.TextElement):
    pass

class LinkNode(nodes.TextElement):
    pass

class SeperatorNode(nodes.TextElement):
    pass

class PyListPresets(SphinxDirective):
    def run(self) -> List[ListPresetsPlaceholder]:
        node = ListPresetsPlaceholder("")
        return [node]

def visit_preset_node(self, node: PresetNode) -> None:
    self.body.append(self.starttag(node, "li"))

def depart_preset_node(self, node: PresetNode) -> None:
    self.body.append("</li>")

def visit_list_preset_node(self, node: ListPresetsNode) -> None:
    self.body.append(self.starttag(node, "ul"))

def depart_list_preset_node(self, node: ListPresetsNode) -> None:
    self.body.append("</ul>")

def visit_link_node(self, node: LinkNode) -> None:
    self.body.append(self.starttag(node, "a", href=node.rawsource))

def depart_link_node(self, node: LinkNode) -> None:
    self.body.append("</a>")

def visit_seperator_node(self, node: SeperatorNode) -> None:
    self.body.append(self.starttag(node, "span"))

def depart_seperator_node(self, node: SeperatorNode) -> None:
    self.body.append("</span>")



def process_list_presets(app: Sphinx, doctree: nodes.Node, fromdocname: str) -> None:
    root_dir = Path(__file__) / ".." / ".." / ".."
    sys.path.append(str(root_dir))
    presets_loader_path = root_dir / "plugin" / "libraries" / "presets" / "_loader.py"

    spec = importlib.util.spec_from_file_location("presets._loader", str(presets_loader_path))
    assert spec
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)

    preset_classes = module.built_presets()

    for node in doctree.traverse(ListPresetsPlaceholder):
        container = ListPresetsNode()
        for preset in preset_classes:
            preset_url = str(preset.base_url)
            preset_node = PresetNode()
            preset_node.append(LinkNode(preset_url, preset_url))

            preset_node.append(SeperatorNode(" - ", " - "))

            parser_url = f"https://github.com/cibere/Flow.Launcher.Plugin.rtfm/tree/main/plugin/libraries/presets/{preset.__module__}.py"
            preset_node.append(LinkNode(parser_url, "Parser"))
            container.append(
                preset_node
            )
        node.replace_self([container])

def setup(app: Sphinx):
    app.add_directive("list-presets", PyListPresets)
    app.add_node(PresetNode, html=(visit_preset_node, depart_preset_node))
    app.add_node(ListPresetsNode, html=(visit_list_preset_node, depart_list_preset_node))
    app.add_node(LinkNode, html=(visit_link_node, depart_link_node))
    app.add_node(SeperatorNode, html=(visit_seperator_node, depart_seperator_node))
    app.add_node(ListPresetsPlaceholder)
    app.connect("doctree-resolved", process_list_presets)
    return {}
    return {"parallel_read_safe": True}

from __future__ import annotations

import msgspec

TYPE_REPLACEMENTS = {
    "record": "struct",
    "constant": "const",
    "domain": "error",
    "bitfield": "flags",
    "function_macro": "func",
    "function": "func",
    "interface": "iface",
}


class DocEntry(msgspec.Struct):
    name: str
    summary: str
    ident: str | None = None
    ctype: str | None = None
    type_name: str | None = None
    type: str | None = None
    href: str | None = None
    deprecated: str | None = None
    struct_for: str | None = None

    @property
    def type_or_struct(self):
        return self.struct_for or self.type_name

    def build_label(self):
        parts = []
        if self.type and (entry_type := TYPE_REPLACEMENTS.get(self.type, self.type)):
            parts.append(entry_type)
        if self.type_or_struct:
            parts.append(self.type_or_struct)
        parts.append(self.name)

        return ".".join(parts)


class GiDocGenIndex(msgspec.Struct):
    symbols: list[DocEntry]

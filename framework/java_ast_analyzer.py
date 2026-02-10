"""Java AST analysis utilities using javalang."""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Set

try:
    import javalang
except ImportError:
    javalang = None


@dataclass
class FieldInfo:
    name: str
    type_name: str
    modifiers: Set[str] = field(default_factory=set)


@dataclass
class MethodInfo:
    name: str
    return_type: str
    param_types: List[str] = field(default_factory=list)
    modifiers: Set[str] = field(default_factory=set)


@dataclass
class ConstructorInfo:
    param_types: List[str] = field(default_factory=list)
    modifiers: Set[str] = field(default_factory=set)


class JavaASTAnalyzer:
    """Wraps javalang for convenient Java source analysis."""

    def __init__(self, source_code: str):
        self.source = source_code
        self.all_source = source_code  # Can be set to combined source of all files
        self.tree = None
        self.parse_error = None
        self._try_parse()

    def _try_parse(self):
        if javalang is None:
            self.parse_error = "javalang not installed"
            return
        try:
            self.tree = javalang.parse.parse(self.source)
        except Exception as e:
            self.parse_error = str(e)

    @property
    def parsed(self) -> bool:
        return self.tree is not None

    def get_class_names(self) -> List[str]:
        if not self.parsed:
            return self._regex_class_names()
        names = []
        for _, node in self.tree:
            if isinstance(node, javalang.tree.ClassDeclaration):
                names.append(node.name)
        return names

    def get_fields(self, class_name: str = None) -> List[FieldInfo]:
        if not self.parsed:
            return self._regex_fields()
        fields = []
        for _, node in self.tree:
            if isinstance(node, javalang.tree.FieldDeclaration):
                modifiers = set(node.modifiers) if node.modifiers else set()
                type_name = node.type.name if node.type else ""
                for decl in node.declarators:
                    fields.append(FieldInfo(
                        name=decl.name,
                        type_name=type_name,
                        modifiers=modifiers
                    ))
        return fields

    def get_methods(self, class_name: str = None) -> List[MethodInfo]:
        if not self.parsed:
            return self._regex_methods()
        methods = []
        for _, node in self.tree:
            if isinstance(node, javalang.tree.MethodDeclaration):
                modifiers = set(node.modifiers) if node.modifiers else set()
                ret_type = node.return_type.name if node.return_type else "void"
                param_types = []
                if node.parameters:
                    for p in node.parameters:
                        param_types.append(p.type.name if p.type else "")
                methods.append(MethodInfo(
                    name=node.name,
                    return_type=ret_type,
                    param_types=param_types,
                    modifiers=modifiers
                ))
        return methods

    def get_constructors(self, class_name: str = None) -> List[ConstructorInfo]:
        if not self.parsed:
            return self._regex_constructors()
        constructors = []
        for _, node in self.tree:
            if isinstance(node, javalang.tree.ConstructorDeclaration):
                modifiers = set(node.modifiers) if node.modifiers else set()
                param_types = []
                if node.parameters:
                    for p in node.parameters:
                        param_types.append(p.type.name if p.type else "")
                constructors.append(ConstructorInfo(
                    param_types=param_types,
                    modifiers=modifiers
                ))
        return constructors

    def has_main_method(self) -> bool:
        for m in self.get_methods():
            if m.name == "main" and "static" in m.modifiers and "public" in m.modifiers:
                return True
        return bool(re.search(r'public\s+static\s+void\s+main\s*\(', self.source))

    def source_contains(self, pattern: str, flags=0) -> bool:
        """Search all source files (if set) for the given pattern."""
        return bool(re.search(pattern, self.all_source, flags))

    def get_package(self) -> str:
        if self.parsed and self.tree.package:
            return self.tree.package.name
        match = re.search(r'package\s+([\w.]+)\s*;', self.source)
        return match.group(1) if match else ""

    # --- Regex fallbacks ---

    def _regex_class_names(self) -> List[str]:
        return re.findall(r'(?:public\s+)?class\s+(\w+)', self.source)

    def _regex_fields(self) -> List[FieldInfo]:
        fields = []
        pattern = r'((?:private|public|protected|static|final)\s+)*(\w+)\s+(\w+)\s*[;=]'
        for match in re.finditer(pattern, self.source):
            modifiers_str = match.group(1) or ""
            modifiers = set(modifiers_str.split())
            fields.append(FieldInfo(
                name=match.group(3),
                type_name=match.group(2),
                modifiers=modifiers
            ))
        return fields

    def _regex_methods(self) -> List[MethodInfo]:
        methods = []
        pattern = r'((?:public|private|protected|static|final)\s+)*([\w<>\[\]]+)\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(pattern, self.source):
            modifiers_str = match.group(1) or ""
            modifiers = set(modifiers_str.split())
            ret_type = match.group(2)
            name = match.group(3)
            params_str = match.group(4).strip()
            param_types = []
            if params_str:
                for param in params_str.split(','):
                    parts = param.strip().split()
                    if len(parts) >= 2:
                        param_types.append(parts[-2])
            if name not in ('if', 'while', 'for', 'switch', 'catch'):
                methods.append(MethodInfo(
                    name=name,
                    return_type=ret_type,
                    param_types=param_types,
                    modifiers=modifiers
                ))
        return methods

    def _regex_constructors(self) -> List[ConstructorInfo]:
        constructors = []
        class_names = self._regex_class_names()
        for cn in class_names:
            pattern = rf'(?:public|private|protected)\s+{cn}\s*\(([^)]*)\)'
            for match in re.finditer(pattern, self.source):
                params_str = match.group(1).strip()
                param_types = []
                if params_str:
                    for param in params_str.split(','):
                        parts = param.strip().split()
                        if len(parts) >= 2:
                            param_types.append(parts[-2])
                constructors.append(ConstructorInfo(param_types=param_types))
        return constructors

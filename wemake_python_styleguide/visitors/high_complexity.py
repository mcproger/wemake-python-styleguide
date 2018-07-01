# -*- coding: utf-8 -*-

import ast
from collections import defaultdict
from typing import DefaultDict

from wemake_python_styleguide.errors import (
    TooManyArgumentsViolation,
    TooManyExpressionsViolation,
    TooManyLocalsViolation,
    TooManyReturnsViolation,
)
from wemake_python_styleguide.options.config import ConfigFileParser
from wemake_python_styleguide.visitors.base.visitor import BaseNodeVisitor

# TODO: implement TooDeepNestingViolation, TooManyBranchesViolation


class ComplexityVisitor(BaseNodeVisitor):
    """This class checks for code with high complexity."""

    def __init__(self) -> None:
        """
        Creates instance of config file parser
        and counters for tracked metrics.
        """
        super().__init__()

        self.config_parser = ConfigFileParser()

        self.expressions: DefaultDict[str, int] = defaultdict(int)
        self.variables: DefaultDict[str, int] = defaultdict(int)
        self.returns: DefaultDict[str, int] = defaultdict(int)

    def _check_arguments_count(self, node: ast.FunctionDef):
        counter = 0
        has_extra_self_or_cls = 0
        max_arguments_count = self.config_parser.get_option('max-arguments')
        if getattr(node, 'function_type', None) in ['method', 'classmethod']:
            has_extra_self_or_cls = 1

        counter += len(node.args.args)
        counter += len(node.args.kwonlyargs)

        if node.args.vararg:
            counter += 1

        if node.args.kwarg:
            counter += 1

        if counter > max_arguments_count + has_extra_self_or_cls:
            self.add_error(
                TooManyArgumentsViolation(node, text=node.name),
            )

    def _update_variables(self, function: ast.FunctionDef):
        max_local_variables_count = self.config_parser.get_option(
            'max-local-variables',
        )
        self.variables[function.name] += 1
        if self.variables[function.name] == max_local_variables_count:
            self.add_error(
                TooManyLocalsViolation(function, text=function.name),
            )

    def _update_returns(self, function: ast.FunctionDef):
        max_returns_count = self.config_parser.get_option('max-returns')
        self.returns[function.name] += 1
        if self.returns[function.name] == max_returns_count:
            self.add_error(
                TooManyReturnsViolation(function, text=function.name),
            )

    def _update_expression(self, function: ast.FunctionDef):
        max_expressions_count = self.config_parser.get_option('max-expressions')
        self.expressions[function.name] += 1
        if self.expressions[function.name] == max_expressions_count:
            self.add_error(
                TooManyExpressionsViolation(function, text=function.name),
            )

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Checks function internal complexity."""
        self._check_arguments_count(node)

        for body_item in node.body:
            for sub_node in ast.walk(body_item):  # TODO: iter_child
                is_variable = isinstance(sub_node, ast.Name)
                context = getattr(sub_node, 'ctx', None)

                if is_variable and isinstance(context, ast.Store):
                    self._update_variables(node)

                if isinstance(sub_node, ast.Return):
                    self._update_returns(node)

                if isinstance(sub_node, ast.Expr):
                    self._update_expression(node)

        self.generic_visit(node)


# class _BranchesVisitor(BaseNodeVisitor):
#     branches = frozenset((
#         ast.For,
#         ast.If,
#         ast.While,
#         ast.
#     ))

#     def visit_FunctionDef(self, node: ast.FunctionDef):
#         for body_item in node.body:
#             for sub_node in ast.walk(body_item):

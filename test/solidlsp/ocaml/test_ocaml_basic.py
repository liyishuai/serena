"""
Basic integration tests for the OCaml language server functionality.

These tests validate the functionality of the language server APIs
like request_document_symbols using the test repository.
"""

import pytest

from solidlsp import SolidLanguageServer
from solidlsp.ls_config import Language

from . import OCAML_LSP_UNAVAILABLE, OCAML_LSP_UNAVAILABLE_REASON


@pytest.mark.ocaml
@pytest.mark.skipif(OCAML_LSP_UNAVAILABLE, reason=f"OCaml LSP not available: {OCAML_LSP_UNAVAILABLE_REASON}")
class TestOcamlLanguageServerBasics:
    """Test basic functionality of the OCaml language server."""

    @pytest.mark.parametrize("language_server", [Language.OCAML], indirect=True)
    def test_language_server_initialization(self, language_server: SolidLanguageServer) -> None:
        """Test that the OCaml language server initializes properly."""
        assert language_server is not None
        assert language_server.language == Language.OCAML

    @pytest.mark.parametrize("language_server", [Language.OCAML], indirect=True)
    def test_document_symbols_calculator(self, language_server: SolidLanguageServer) -> None:
        """Test document symbols retrieval for OCaml files."""
        file_path = "calculator.ml"
        symbols_tuple = language_server.request_document_symbols(file_path).get_all_symbols_and_roots()
        assert isinstance(symbols_tuple, tuple)
        assert len(symbols_tuple) == 2

        all_symbols, root_symbols = symbols_tuple
        assert isinstance(all_symbols, list)
        assert isinstance(root_symbols, list)

        # Verify expected symbols are present
        symbol_names = {s["name"] for s in all_symbols}

        # Check for expected function names
        expected_functions = {"add", "subtract", "multiply", "divide"}
        found_functions = expected_functions.intersection(symbol_names)
        assert len(found_functions) > 0, f"Expected to find some of {expected_functions}, got {symbol_names}"

    @pytest.mark.parametrize("language_server", [Language.OCAML], indirect=True)
    def test_document_symbols_helper(self, language_server: SolidLanguageServer) -> None:
        """Test document symbols retrieval for helper module."""
        file_path = "helper.ml"
        symbols_tuple = language_server.request_document_symbols(file_path).get_all_symbols_and_roots()
        assert isinstance(symbols_tuple, tuple)
        assert len(symbols_tuple) == 2

        all_symbols, root_symbols = symbols_tuple
        assert isinstance(all_symbols, list)
        assert isinstance(root_symbols, list)

        # Verify expected symbols are present
        symbol_names = {s["name"] for s in all_symbols}

        # Check for expected function names
        expected_functions = {"validate_number", "is_positive", "is_negative", "absolute"}
        found_functions = expected_functions.intersection(symbol_names)
        assert len(found_functions) > 0, f"Expected to find some of {expected_functions}, got {symbol_names}"

import shutil


def _test_ocaml_lsp_available() -> str:
    """Test if OCaml LSP is available and return error reason if not."""
    # Check if ocamllsp is available
    if not shutil.which("ocamllsp"):
        return "ocamllsp is not installed or not in PATH"

    return ""  # No error, OCaml LSP should be available


OCAML_LSP_UNAVAILABLE_REASON = _test_ocaml_lsp_available()
OCAML_LSP_UNAVAILABLE = bool(OCAML_LSP_UNAVAILABLE_REASON)

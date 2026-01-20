"""
Provides OCaml specific instantiation of the LanguageServer class using ocaml-lsp-server.
"""

import logging
import os
import pathlib
import shutil
import threading

from overrides import override

from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig
from solidlsp.lsp_protocol_handler.lsp_types import InitializeParams
from solidlsp.lsp_protocol_handler.server import ProcessLaunchInfo
from solidlsp.settings import SolidLSPSettings

log = logging.getLogger(__name__)


class OcamlLanguageServer(SolidLanguageServer):
    """
    Provides OCaml specific instantiation of the LanguageServer class using ocaml-lsp-server.
    """

    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        # For OCaml projects, we should ignore:
        # - _build: dune/ocamlbuild build artifacts
        # - _opam: local opam switch
        # - _esy: esy package manager artifacts
        # - .merlin: merlin configuration (usually single file, but could be a directory)
        # - node_modules: if the project has JavaScript components
        return super().is_ignored_dirname(dirname) or dirname in ["_build", "_opam", "_esy", ".merlin", "node_modules", "_obuild"]

    @staticmethod
    def _get_ocamllsp_path() -> str | None:
        """Get the path to ocamllsp executable."""
        # First check if it's in PATH
        ocamllsp = shutil.which("ocamllsp")
        if ocamllsp:
            return ocamllsp

        return None

    @staticmethod
    def _setup_runtime_dependency() -> str:
        """
        Check if required OCaml runtime dependencies are available.
        Raises RuntimeError with helpful message if dependencies are missing.
        """
        ocamllsp_path = OcamlLanguageServer._get_ocamllsp_path()

        if not ocamllsp_path:
            raise RuntimeError(
                "ocamllsp (OCaml LSP server) is not installed or not in PATH.\n"
                "Please install it via opam:\n"
                "  opam install ocaml-lsp-server\n\n"
                "Or if using esy:\n"
                "  esy add ocaml-lsp-server\n\n"
                "After installation, make sure 'ocamllsp' is added to your PATH.\n"
                "You may need to run 'eval $(opam env)' to update your environment."
            )

        return ocamllsp_path

    def __init__(self, config: LanguageServerConfig, repository_root_path: str, solidlsp_settings: SolidLSPSettings):
        ocamllsp_path = self._setup_runtime_dependency()

        super().__init__(
            config, repository_root_path, ProcessLaunchInfo(cmd=ocamllsp_path, cwd=repository_root_path), "ocaml", solidlsp_settings
        )
        self.server_ready = threading.Event()
        self.request_id = 0

    @staticmethod
    def _get_initialize_params(repository_absolute_path: str) -> InitializeParams:
        """
        Returns the initialize params for the OCaml Language Server.
        """
        root_uri = pathlib.Path(repository_absolute_path).as_uri()
        initialize_params = {
            "locale": "en",
            "capabilities": {
                "textDocument": {
                    "synchronization": {"didSave": True, "dynamicRegistration": True},
                    "definition": {"dynamicRegistration": True, "linkSupport": True},
                    "typeDefinition": {"dynamicRegistration": True, "linkSupport": True},
                    "references": {"dynamicRegistration": True},
                    "documentSymbol": {
                        "dynamicRegistration": True,
                        "hierarchicalDocumentSymbolSupport": True,
                        "symbolKind": {"valueSet": list(range(1, 27))},
                    },
                    "completion": {
                        "dynamicRegistration": True,
                        "completionItem": {
                            "snippetSupport": True,
                            "commitCharactersSupport": True,
                            "documentationFormat": ["markdown", "plaintext"],
                            "deprecatedSupport": True,
                            "preselectSupport": True,
                        },
                    },
                    "hover": {
                        "dynamicRegistration": True,
                        "contentFormat": ["markdown", "plaintext"],
                    },
                    "signatureHelp": {
                        "dynamicRegistration": True,
                        "signatureInformation": {
                            "documentationFormat": ["markdown", "plaintext"],
                            "parameterInformation": {"labelOffsetSupport": True},
                        },
                    },
                    "codeAction": {
                        "dynamicRegistration": True,
                        "codeActionLiteralSupport": {
                            "codeActionKind": {
                                "valueSet": [
                                    "",
                                    "quickfix",
                                    "refactor",
                                    "refactor.extract",
                                    "refactor.inline",
                                    "refactor.rewrite",
                                    "source",
                                    "source.organizeImports",
                                ]
                            }
                        },
                    },
                    "formatting": {"dynamicRegistration": True},
                    "rangeFormatting": {"dynamicRegistration": True},
                    "rename": {"dynamicRegistration": True, "prepareSupport": True},
                },
                "workspace": {
                    "workspaceFolders": True,
                    "didChangeConfiguration": {"dynamicRegistration": True},
                    "configuration": True,
                    "symbol": {
                        "dynamicRegistration": True,
                        "symbolKind": {"valueSet": list(range(1, 27))},
                    },
                },
            },
            "processId": os.getpid(),
            "rootPath": repository_absolute_path,
            "rootUri": root_uri,
            "workspaceFolders": [
                {
                    "uri": root_uri,
                    "name": os.path.basename(repository_absolute_path),
                }
            ],
        }
        return initialize_params  # type: ignore[return-value]

    def _start_server(self) -> None:
        """Start OCaml Language Server process"""

        def register_capability_handler(params: dict) -> None:
            return

        def window_log_message(msg: dict) -> None:
            log.info(f"LSP: window/logMessage: {msg}")

        def do_nothing(params: dict) -> None:
            return

        self.server.on_request("client/registerCapability", register_capability_handler)
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_notification("$/progress", do_nothing)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)

        log.info("Starting OCaml Language Server process")
        self.server.start()
        initialize_params = self._get_initialize_params(self.repository_root_path)

        log.info("Sending initialize request from LSP client to LSP server and awaiting response")
        init_response = self.server.send.initialize(initialize_params)

        # Verify server capabilities
        capabilities = init_response.get("capabilities", {})
        log.info(f"OCaml LSP capabilities: {list(capabilities.keys())}")

        # OCaml LSP should provide these core capabilities
        assert "textDocumentSync" in capabilities, "OCaml LSP should support text document sync"

        self.server.notify.initialized({})
        self.completions_available.set()

        # OCaml Language Server is ready after initialization
        self.server_ready.set()

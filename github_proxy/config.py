import os
import re
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Mapping
from typing import Optional
from typing import Sequence

import yaml
from dacite.config import Config as DaciteConfig
from dacite.core import from_dict
from jinja2 import Environment
from jinja2 import FileSystemLoader

from github_proxy.cache.backend import CacheBackendConfig
from github_proxy.github_tokens import GitHubAppConfig
from github_proxy.github_tokens import GitHubTokenConfig
from github_proxy.proxy import ProxyClient
from github_proxy.proxy import validate_clients

_DESERIALIZATION_CONFIG = DaciteConfig(type_hooks={re.Pattern: re.compile})


@dataclass
class ClientRegistry:
    version: int = 1
    clients: Sequence[ProxyClient] = field(default_factory=list)

    def __post_init__(self) -> None:
        validate_clients(self.clients)

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "ClientRegistry":
        return from_dict(cls, data, config=_DESERIALIZATION_CONFIG)


class Config(GitHubTokenConfig, CacheBackendConfig):
    def __init__(self, config_dict: Optional[Mapping[str, str]] = None):
        # NOTE: When adding new config items, do not forget to update the
        # Configuration table in the README docs.

        if config_dict is None:
            config_dict = os.environ

        self.github_api_url = config_dict.get(
            "GITHUB_API_URL", "https://api.github.com"
        )

        # Configuring the cache that persists GitHub responses:
        self.cache_ttl = int(config_dict.get("CACHE_TTL", "3600"))
        self.cache_backend_url = config_dict.get("CACHE_BACKEND_URL", "inmemory://")

        # Collecting GitHub creds:
        self.github_pats = Config._collect_github_pats(config_dict)
        self.github_apps = Config._collect_github_apps(config_dict)

        # Configuring the inmemory cache that persists GitHub creds:
        self.github_creds_cache_maxsize = int(
            config_dict.get("GITHUB_CREDS_CACHE_MAXSIZE", "256")
        )
        self.github_creds_cache_ttl_padding = int(
            config_dict.get("GITHUB_CREDS_CACHE_TTL_PADDING", "10")
        )

        # Collecting proxy client configuration
        self.clients = Config._collect_clients(config_dict)

        # Configuring the telemetry collector
        self.tel_collector_type = os.environ.get(
            "TELEMETRY_COLLECTOR_TYPE", "NOOP"
        ).lower()

    @staticmethod
    def _collect_clients(
        config_dict: Mapping[str, str], j2_env: Optional[Environment] = None
    ) -> Sequence[ProxyClient]:
        fp = Path(config_dict["CLIENT_REGISTRY_FILE_PATH"])

        def read_file_content(fp: Path, j2_env: Optional[Environment] = None) -> str:
            if fp.suffix == ".j2":
                environment = j2_env or Environment(
                    loader=FileSystemLoader(searchpath=fp.parent)
                )
                template = environment.get_template(name=fp.name)
                return template.render(env=config_dict)

            with fp.open() as f:
                return f.read()

        client_registry = ClientRegistry.deserialize(
            yaml.safe_load(read_file_content(fp, j2_env))
        )

        return client_registry.clients

    @staticmethod
    def _collect_github_pats(config_dict: Mapping[str, str]) -> Mapping[str, str]:
        return {
            env[len("GITHUB_PAT_") :].lower(): pat
            for env, pat in config_dict.items()
            if env.startswith("GITHUB_PAT_")
        }

    @staticmethod
    def _collect_github_apps(
        config_dict: Mapping[str, str]
    ) -> Mapping[str, GitHubAppConfig]:
        app_names = [
            env[len("GITHUB_APP_") : -len("_ID")].lower()
            for env in config_dict
            if env.startswith("GITHUB_APP_")
            and env.endswith("_ID")
            and not env.endswith("_INSTALLATION_ID")
        ]
        return {
            name: GitHubAppConfig(
                id_=config_dict[f"GITHUB_APP_{name.upper()}_ID"],
                private_key=config_dict[f"GITHUB_APP_{name.upper()}_PEM"],
                installation_id=int(
                    config_dict[f"GITHUB_APP_{name.upper()}_INSTALLATION_ID"]
                ),
            )
            for name in app_names
        }

    def __hash__(self) -> int:  # to satisfy mypy
        return super().__hash__()

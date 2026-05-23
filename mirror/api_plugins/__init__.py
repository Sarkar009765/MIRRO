import os
from pathlib import Path
from importlib import import_module
from ..utils.logger import get_logger

logger = get_logger("api_aggregator")


class APIAggregator:
    def __init__(self):
        self.plugins = []
        self._plugin_map = {}
        self._load_builtin_plugins()

    def _load_builtin_plugins(self):
        builtins = ["gemini", "groq", "cerebras", "openrouter", "cloudflare",
                     "github_models", "mistral", "template"]
        for name in builtins:
            try:
                module = import_module(f"..api_plugins.{name}", package=__package__)
                for attr in dir(module):
                    cls = getattr(module, attr)
                    if (isinstance(cls, type) and hasattr(cls, "name")
                            and getattr(cls, "__module__", None) == module.__name__):
                        instance = cls()
                        self.plugins.append(instance)
                        self._plugin_map[instance.name] = instance
                        break
            except Exception as e:
                logger.warning(f"Failed to load plugin '{name}': {e}")

    def discover_plugins(self, directory=None):
        directory = directory or Path(__file__).parent
        for f in directory.glob("*.py"):
            if f.stem.startswith("_") or f.stem in self._plugin_map:
                continue
            try:
                module = import_module(f"..api_plugins.{f.stem}", package=__package__)
                for attr in dir(module):
                    cls = getattr(module, attr)
                    if (isinstance(cls, type) and hasattr(cls, "name")
                            and hasattr(cls, "generate")
                            and getattr(cls, "__module__", None) == module.__name__):
                        instance = cls()
                        self.plugins.append(instance)
                        self._plugin_map[instance.name] = instance
                        logger.info(f"Discovered API plugin: {instance.name}")
            except Exception as e:
                logger.warning(f"Failed to load {f.name}: {e}")

    async def generate(self, prompt, context=None, system_instruction=None):
        last_error = None
        for plugin in self.plugins:
            if plugin.requires_key and not self._has_key(plugin):
                continue
            try:
                result = await plugin.generate(prompt, context, system_instruction)
                if result:
                    return result
            except Exception as e:
                last_error = e
                continue
        logger.warning("All API plugins exhausted, using template engine")
        template = self._plugin_map.get("template")
        if template:
            return await template.generate(prompt, context, system_instruction)
        return None

    def _has_key(self, plugin):
        key_map = {
            "gemini": "GEMINI_API_KEY",
            "groq": "GROQ_API_KEY",
            "cerebras": "CEREBRAS_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "cloudflare": "CLOUDFLARE_API_TOKEN",
            "github_models": "GITHUB_TOKEN",
            "mistral": "MISTRAL_API_KEY",
        }
        env_var = key_map.get(plugin.name)
        if env_var and os.getenv(env_var):
            return True
        return not plugin.requires_key

    def status_report(self):
        return {p.name: {"quota": p.quota_used, "free_tier": p.free_tier}
                for p in self.plugins}

    def get_plugin(self, name):
        return self._plugin_map.get(name)

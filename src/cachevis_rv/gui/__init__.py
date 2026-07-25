"""V3 platform GUI package with lazy public imports."""

__all__ = ["CacheVisMainWindow", "LabDefinition", "LAB_REGISTRY"]


def __getattr__(name: str):
    if name == "CacheVisMainWindow":
        from .main_window import CacheVisMainWindow

        return CacheVisMainWindow
    if name in {"LabDefinition", "LAB_REGISTRY"}:
        from .lab_registry import LAB_REGISTRY, LabDefinition

        return {
            "LabDefinition": LabDefinition,
            "LAB_REGISTRY": LAB_REGISTRY,
        }[name]
    raise AttributeError(name)

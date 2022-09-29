from pathlib import Path

import toml


class DependenciesService(object):
    @staticmethod
    async def get_dependencies():
        base_dir = Path(__file__).parent.parent.parent
        data = toml.load(base_dir / "pyproject.toml")
        dependencies = data.get("project").get("dependencies")
        result = {}
        for i in dependencies:
            dep = i.replace(">=", ",>=").split(",")
            result[dep[0]] = dep[1]
        return result

import ansible_runner
from ansible_runner import Runner
from ansible_runner.streaming import Transmitter, Worker, Processor
from common.make import run_async
from utils.abstract import RemoteExecutor


class AnsibleExecutor(RemoteExecutor):
    @classmethod
    async def _run(cls, **kwargs):  # type: ignore
        def run_for_result() -> Transmitter | Worker | Processor | Runner:
            ret = ansible_runner.run(**kwargs)
            return ret

        r = await run_async(run_for_result)

        return r.stdout.read()

    @classmethod
    async def exec_module(cls, **kwargs) -> str:  # type: ignore
        result = await cls._run(
            private_data_dir=kwargs.get("data_dir", "/tmp"),
            inventory=kwargs.get("inventory", "/etc/ansible/hosts"),
            host_pattern=kwargs.get("host_pattern", "*"),
            module=kwargs.get("module", "shell"),
            module_args=kwargs.get("module_args", ""),
            extravars=kwargs.get("extra_vars", {}),
            forks=kwargs.get("forks", 10),
            quiet=True,
        )
        return result

    @classmethod
    async def exec_task(cls, **kwargs) -> str:  # type: ignore
        result = await cls._run(
            private_data_dir=kwargs.get("data_dir", "/tmp"),
            inventory=kwargs.get("inventory", "/etc/ansible/hosts"),
            playbook=kwargs.get("playbook", ""),
            extravars=kwargs.get("extra_vars", {}),
            forks=kwargs.get("forks", 10),
            quiet=True,
        )
        return result

#!/usr/bin/env python
import os, sys
from fabric2 import Connection
from app.builds.service.code import Code
from invoke import Result
from invoke import Responder
import traceback


def say_yes():
    return Responder(
        pattern=r'yes/no',
        response='yes\n',
    )


class SshConnection(Connection):
    run_mode_sudo = 'sudo'
    run_mode_remote = 'remote'
    run_mode_local = 'local'

    connections, success, errors = {}, {}, {}
    release_version_tar, release_version = None, None

    custom_global_env = {}

    def init_env(self, env):
        self.custom_global_env = env

    def run(self, command, wenv=None, run_mode=run_mode_local, pty=False, exception=True, **kwargs):
        """
        :return Result,  返回为invoke.Result对象可以使用 ret.stdout ret.exited读取属性。 非字典类型
         stdout控制台输出， command执行的命令， exited:0成功其他额为错误码, 因为pty=True错误信息也在stdout中
        {'stdout': '/bin/bash: fseo: command not found\r\n', 'stderr': '', 'encoding': 'UTF-8', 'command': 'fseo',
        'shell': '/bin/bash', 'env': {}, 'exited': 127, 'pty': True, 'hide': ()}
        """
        # todo:
        # pty 为True时 celery中执行fabric任务报错
        # / invoke / runners.py line 1136, in start fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSWINSZ, winsize)
        # AttributeError: 'LoggingProxy' object has no attribute 'fileno'
        pty = False
        try:
            if run_mode == self.run_mode_sudo:
                result = super(SshConnection, self).sudo(command, pty=pty, env=self.custom_global_env, **kwargs)
            elif run_mode == self.run_mode_local:
                result = super(SshConnection, self).local(command, pty=pty, warn=True, watchers=[say_yes()],
                                                          env=self.custom_global_env, **kwargs)
            else:
                result = super(SshConnection, self).run(command, pty=pty, warn=True, watchers=[say_yes()],
                                                        env=self.custom_global_env, **kwargs)
            return result
        except Exception as e:
            traceback.print_exc()
            if hasattr(e, 'message'):
                msg = e.message
            elif hasattr(e, 'result'):
                msg = e.result
            else:
                msg = str(e)
            result = Result(exited=-1, stderr="", stdout=msg)
            return result

    def sudo(self, command, wenv=None, **kwargs):
        return self.run(command, wenv=wenv, run_mode=self.run_mode_sudo, **kwargs)

    def get(self, remote, local=None, wenv=None):
        return self.sync(wtype='get', remote=remote, local=local, wenv=wenv)

    def put(self, local, remote=None, wenv=None, *args, **kwargs):
        return self.sync(wtype='put', local=local, remote=remote, wenv=wenv, *args, **kwargs)

    def local(self, command, wenv=None, **kwargs):
        return self.run(command, wenv=wenv, run_mode=self.run_mode_local, **kwargs)

    def sync(self, wtype, remote=None, local=None, wenv=None):
        command = 'scp %s %s@%s:%s' % (local, self.user, self.host, remote) if wtype == 'put' \
            else 'scp %s@%s:%s %s' % (self.user, self.host, remote, local)
        message = 'deploying task_id=%s [%s@%s]$ %s ' % (wenv['task_id'], self.user, self.host, command)
        print(message)


if __name__ == '__main__':
    ssh_client = SshConnection(host='127.0.0.1', inline_ssh_env=True)
    ret = ssh_client.local("ls -al /opt")
    print(ret.exited, ret.stdout, ret.env)

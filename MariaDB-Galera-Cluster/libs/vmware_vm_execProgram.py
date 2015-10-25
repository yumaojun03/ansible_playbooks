#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# (c) 2015, zhi chuanxiu
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible. If not, see <http://www.gnu.org/licenses/>.


from ansible.module_utils.basic import *

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import requests
import atexit


class Main(object):
    """
    this is the main module for executing a process 
    in the VM without the network requirement to actually access it.
    """
    def __init__(self):
        global module
        module = AnsibleModule(
            argument_spec=dict(
                vcenter_hostname = dict(required=True),
                vcenter_username = dict(required=True),
                vcenter_password = dict(required=True),
                vcenter_port     = dict(required=False, default=443),

                vm_uuid          = dict(required=True),
                vm_username      = dict(required=True),
                vm_password      = dict(required=True),
                vm_pathProgram   = dict(required=False, default=None),
                vm_arguProgram   = dict(required=False, default=None),
            ),
            supports_check_mode=True
        )
        self.vcenter_hostname    = module.params['vcenter_hostname']
        self.vcenter_username    = module.params['vcenter_username']
        self.vcenter_password    = module.params['vcenter_password']
        self.vcenter_port        = module.params['vcenter_port']

        self.vm_uuid             = module.params['vm_uuid']
        self.vm_username         = module.params['vm_username']
        self.vm_password         = module.params['vm_password']
        self.vm_pathProgram      = module.params['vm_pathProgram']
        self.vm_arguProgram      = module.params['vm_arguProgram']


    def execute_program(self):
        try:
            service_instance = SmartConnect(host=self.vcenter_hostname,
                                            user=self.vcenter_username,
                                            pwd=self.vcenter_password,
                                            port=int(self.vcenter_port))
            atexit.register(Disconnect, service_instance)
            si = service_instance.RetrieveContent()

            search_index = si.searchIndex
            vm = search_index.FindByUuid(None, self.vm_uuid, True, True)
            tools_status = vm.guest.toolsStatus
            if (tools_status == 'toolsNotInstalled' or tools_status == 'toolsNotRunning'):
                raise SystemExit(
                    "VMwareTools is either not running or not installed. "
                    "Rerun the script after verifying that VMwareTools "
                    "is running")

            creds = vim.vm.guest.NamePasswordAuthentication(
                username=self.vm_username, password=self.vm_password
            )

            try:
                pm = si.guestOperationsManager.processManager
                ps = vim.vm.guest.ProcessManager.ProgramSpec(
                    programPath=self.vm_pathProgram,
                    arguments=self.vm_arguProgram,
                )
                res = pm.StartProgramInGuest(vm, creds, ps)

                if res > 0:
                    module.exit_json(change=True, result="Program executed, PID is %d" % res)
            except IOError, e:
                module.fail_json(change=False, msg=str(e))
        except vmodl.MethodFault as error:
            module.fail_json(change=True, msg="Caught vmodl fault : %s" % error.msg)

    def __call__(self):
        self.execute_program()

if __name__ == "__main__":
    main = Main()
    main()

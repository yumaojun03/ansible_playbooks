#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
(c) 2015, zhi chuanxiu(yumaojun03@gmail.com)

This file is part of Ansible

Ansible is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Ansible is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Ansible. If not, see <http://www.gnu.org/licenses/>.
"""

from ansible.module_utils.basic import *

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import requests
import atexit


class Main(object):
    """
    this is main module
    """

    def __init__(self):
        global module
        module = AnsibleModule(
            argument_spec=dict(
                vcenter_hostname = dict(required=True),
                vcenter_port     = dict(required=False, default=443),
                vcenter_username = dict(required=True),
                vcenter_password = dict(required=True),

                vm_name          = dict(required=True),
                vm_folder        = dict(required=True),
                ),
            supports_check_mode=True
        )
        self.vcenter_hostname    = module.params['vcenter_hostname']
        self.vcenter_port        = module.params['vcenter_port']
        self.vcenter_username    = module.params['vcenter_username']
        self.vcenter_password    = module.params['vcenter_password']
        self.vm_name             = module.params['vm_name']
        self.vm_folder           = module.params['vm_folder'] 
        self.vm_uuid_info        = []


    def get_all_vm_uuid(self, virtual_machine, depth=1):
        """
        Print information for a particular virtual machine or recurse into a
        folder with depth protection

        if this is a group it will have children. if it does, recurse into them
        and then return
        """
        maxdepth = 10

        if hasattr(virtual_machine, 'childEntity'):
            if depth > maxdepth:
                return
            vmList = virtual_machine.childEntity
            for c in vmList:
                self.get_all_vm_uuid(c, depth + 1)
            return

        summary = virtual_machine.summary
        self.vm_uuid_info.append((summary.config.name, summary.config.instanceUuid))
       
    def get_vm_uuid(self):
        try:
            service_instance = SmartConnect(host=self.vcenter_hostname,
                                            user=self.vcenter_username,
                                            pwd=self.vcenter_password,
                                            port=int(self.vcenter_port))

            atexit.register(Disconnect, service_instance)

            content = service_instance.RetrieveContent()
            children = content.rootFolder.childEntity
            for child in children:
                if hasattr(child, 'vmFolder'):
                    datacenter = child
                else:
                    # some other non-datacenter type object
                    continue

                vm_folder = datacenter.vmFolder
                vm_list = vm_folder.childEntity
                for virtual_machine in vm_list:
                    if virtual_machine.name == self.vm_folder:
                        self.get_all_vm_uuid(virtual_machine, 10)

        except vmodl.MethodFault as error:
            module.fail_json(changed=True, msg="Caught vmodl fault : %s" % error.msg)
    
        res_uuid = dict(self.vm_uuid_info)[self.vm_name]
        module.exit_json(changed=True, result="%s" % (res_uuid))

    def __call__(self):
        """
        execute module
        Listing the virtual machines on a system.
        """
        self.get_vm_uuid()


if __name__ == "__main__":
    main = Main()
    main()


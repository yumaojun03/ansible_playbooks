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
    this is the main module
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
                vm_template      = dict(required=True),
                vm_dataCenter    = dict(required=False,default=None),
                vm_folder        = dict(required=False, default=None),
                vm_dataStore     = dict(required=False,default=None),
                vm_cluster       = dict(required=False,default=None),
                vm_resourcePool  = dict(required=False,default=None),
                ),
            supports_check_mode=True
        )
        self.vcenter_hostname = module.params['vcenter_hostname']
        self.vcenter_port     = module.params['vcenter_port']
        self.vcenter_username = module.params['vcenter_username']
        self.vcenter_password = module.params['vcenter_password']
        self.vm_name          = module.params['vm_name']
        self.vm_folder        = module.params['vm_folder']
        self.vm_template      = module.params['vm_template']
        self.vm_dataCenter    = module.params['vm_dataCenter']
        self.vm_dataStore     = module.params['vm_dataStore']
        self.vm_cluster       = module.params['vm_cluster']
        self.vm_resourcePool  = module.params['vm_resourcePool']

    @staticmethod
    def get_obj(content, vimtype, name):
        """
        return an object by name, if name is None the
        first found object is returned
        """
        obj = None
        container = content.viewManager.CreateContainerView(
            content.rootFolder, vimtype, True)
        for c in container.view:
            if name:
                if c.name == name:
                    obj = c
                    break
            else:
                obj = c
                break
        return obj

    def do_clone_vm(self, content, si, template, power_on):
        """
        传入一个模板对象，使用以下参数作为模板的Clone参数
            如果没传入dataCenter，则获取第一个作为默认值
            如果没传入vm_folder， 则获取第一个作为默认值
            如果没传入vm_dataStore, 则获取第一个作为默认值
            如果没有传入vm_cluster, 则后面第一个作为默认值
            如果没有传入vm_resourcePool, 则后面第一个作为默认值
        """
        datacenter = self.get_obj(content, [vim.Datacenter], self.vm_dataCenter)
        
        if self.vm_folder:
            destfolder = self.get_obj(content, [vim.Folder], self.vm_folder)
        else:
            destfolder = datacenter.vmFolder
        
        if self.vm_dataStore:
            datastore = self.get_obj(content, [vim.Datastore], self.vm_dataStore)
        else:
            datastore = self.get_obj(content, [vim.Datastore], template.datastore[0].info.name)
        
        cluster = self.get_obj(content, [vim.ClusterComputeResource], self.vm_cluster)
        
        if self.vm_resourcePool:
            resource_pool = self.get_obj(content, [vim.ResourcePool], self.vm_resourcePool)
        else:
            resource_pool = cluster.resourcePool

        # set relospec
        relospec = vim.vm.RelocateSpec()
        relospec.datastore = datastore
        relospec.pool = resource_pool
        # set clonespec
        clonespec = vim.vm.CloneSpec()
        clonespec.location = relospec
        clonespec.powerOn = power_on

        task = template.Clone(folder=destfolder, name=self.vm_name, spec=clonespec)
        # wait for a vCenter task to finish
        task_done = False
        while not task_done:
            print task.info
            if task.info.state == 'success':
                task_done = True
                return {'success': task.info.result}

            if task.info.state == 'error':
                task_done = True
                return {'failed': task.info.error.msg}

    def __call__(self):
        """
        run module
        """
        # connect to the server
        si = SmartConnect(
            host=self.vcenter_hostname,
            user=self.vcenter_username,
            pwd=self.vcenter_password,
            port=self.vcenter_port)
        # doing this means you don't need to
        # remember to disconnect your script/objects
        atexit.register(Disconnect, si)

        content = si.RetrieveContent()
        template = None
        template = self.get_obj(content, [vim.VirtualMachine], self.vm_template)

        if template:
            print "Cloning VM..."
            result = self.do_clone_vm(content, si, template, True)
        else:
            module.fail_json(changed=False, msg="template not found")

        # print result
        if result:
            if result.get('success'):
                module.exit_json(changed=True, result="SUCCESS: %s" % result['success'])
            if result.get('failed'):
                module.fail_json(changed=False, msg="FAILED: %s" % result['failed'])


if __name__ == "__main__":
    main = Main()
    main()


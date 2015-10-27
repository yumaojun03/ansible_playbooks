#!/usr/bin/env python

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
import atexit



def wait_for_tasks(service_instance, tasks):
    """
    Given the service instance si and tasks, it returns after all the
    tasks are complete
    """
    property_collector = service_instance.content.propertyCollector
    task_list = [str(task) for task in tasks]
    # Create filter
    obj_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                 for task in tasks]
    property_spec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                               pathSet=[],
                                                               all=True)
    filter_spec = vmodl.query.PropertyCollector.FilterSpec()
    filter_spec.objectSet = obj_specs
    filter_spec.propSet = [property_spec]
    pcfilter = property_collector.CreateFilter(filter_spec, True)
    try:
        version, state = None, None
        # Loop looking for updates till the state moves to a completed state.
        while len(task_list):
            update = property_collector.WaitForUpdates(version)
            for filter_set in update.filterSet:
                for obj_set in filter_set.objectSet:
                    task = obj_set.obj
                    for change in obj_set.changeSet:
                        if change.name == 'info':
                            state = change.val.state
                        elif change.name == 'info.state':
                            state = change.val
                        else:
                            continue

                        if not str(task) in task_list:
                            continue

                        if state == vim.TaskInfo.State.success:
                            # Remove task from taskList
                            task_list.remove(str(task))
                        elif state == vim.TaskInfo.State.error:
                            raise task.info.error
            # Move to next version
            version = update.version
    finally:
        if pcfilter:
            pcfilter.Destroy()



class Main(object):
    """
    this is the main module for 
    Uploading a file from host to guest
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
                vm_IP            = dict(required=False, default=None),
                vm_DNS           = dict(required=False, default=None),
            ),
            supports_check_mode=True
        )
        self.vcenter_hostname    = module.params['vcenter_hostname']
        self.vcenter_username    = module.params['vcenter_username']
        self.vcenter_password    = module.params['vcenter_password']
        self.vcenter_port        = module.params['vcenter_port']

        self.vm_uuid             = module.params['vm_uuid']
        self.vm_IP               = module.params['vm_IP']
        self.vm_DNS              = module.params['vm_DNS']

    def reboot(self):
        """
        reboot the vm
        """
        try:
            service_instance = SmartConnect(host=self.vcenter_hostname,
                                            user=self.vcenter_username,
                                            pwd=self.vcenter_password,
                                            port=int(self.vcenter_port))

            atexit.register(Disconnect, service_instance)
            si = service_instance.RetrieveContent()

            search_index = si.searchIndex
            vm = search_index.FindByUuid(None, self.vm_uuid, True, True)
            if not vm:
                module.fail_json(msg="Unable to locate VirtualMachine.")
            task = vm.ResetVM_Task()
            wait_for_tasks(si, [task])
            module.exit_json(change=True, result="Successfully uploaded file")
        except vmodl.MethodFault, e:
            module.fail_json(change=False, msg="Caught vmodl fault : %s" % str(e))

    def __call__(self):
        """
        run this module
        """
        self.reboot()

if __name__ == "__main__":
    main = Main()
    main()

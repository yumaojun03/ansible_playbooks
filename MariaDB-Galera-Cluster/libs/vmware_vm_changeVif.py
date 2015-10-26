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

import atexit

from pyVim import connect
from pyVmomi import vim, vmodl

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
    this is the main module
    for changing network virtual machines NIC
    """
    def __init__(self):
        global module
        module = AnsibleModule(
            argument_spec=dict(
                vcenter_hostname = dict(required=True),
                vcenter_port     = dict(required=False, default=443),
                vcenter_username = dict(required=True),
                vcenter_password = dict(required=True),

                vm_uuid          = dict(required=True),
                vm_networkName   = dict(required=True),
                vm_networkType   = dict(required=True, choices=["VSS", "VDS"]),
                ),
            supports_check_mode=True
        )
        self.vcenter_hostname = module.params['vcenter_hostname']
        self.vcenter_port     = module.params['vcenter_port']
        self.vcenter_username = module.params['vcenter_username']
        self.vcenter_password = module.params['vcenter_password']
        self.vm_uuid          = module.params['vm_uuid']
        self.vm_networkName   = module.params['vm_networkName']
        self.vm_networkType   = module.params['vm_networkType']
         

    def get_obj(self, content, vimtype, name):
        """
        get the vsphere object associated with a given text name
        """
        obj = None
        container = content.viewManager.CreateContainerView(content.rootFolder,
                                                            vimtype, True)
        for view in container.view:
            if view.name == name:
                obj = view
                break
        return obj

    def change_vif(self):
        """
        changing network virtual machines NIC
        """
        try:
            service_instance = connect.SmartConnect(host=self.vcenter_hostname,
                                                    user=self.vcenter_username,
                                                    pwd=self.vcenter_password,
                                                    port=int(self.vcenter_port))

            atexit.register(connect.Disconnect, service_instance)
            content = service_instance.RetrieveContent()
            vm = content.searchIndex.FindByUuid(None, self.vm_uuid, True, True)
            # This code is for changing only one Interface. For multiple Interface
            # Iterate through a loop of network names.
            device_change = []
            for device in vm.config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualEthernetCard):
                    nicspec = vim.vm.device.VirtualDeviceSpec()
                    nicspec.operation = \
                        vim.vm.device.VirtualDeviceSpec.Operation.edit
                    nicspec.device = device
                    nicspec.device.wakeOnLanEnabled = True

                    if self.vm_networkType == "VSS":
                        nicspec.device.backing = \
                            vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                        nicspec.device.backing.network = \
                            self.get_obj(content, [vim.Network], self.vm_networkName)
                        nicspec.device.backing.deviceName = self.vm_networkName
                    elif self.vm_networkType == "VDS":
                        network = self.get_obj(content,
                                          [vim.dvs.DistributedVirtualPortgroup],
                                          self.vm_networkName)
                        dvs_port_connection = vim.dvs.PortConnection()
                        dvs_port_connection.portgroupKey = network.key
                        dvs_port_connection.switchUuid = \
                            network.config.distributedVirtualSwitch.uuid
                        nicspec.device.backing = \
                            vim.vm.device.VirtualEthernetCard. \
                            DistributedVirtualPortBackingInfo()
                        nicspec.device.backing.port = dvs_port_connection

                    nicspec.device.connectable = \
                        vim.vm.device.VirtualDevice.ConnectInfo()
                    nicspec.device.connectable.startConnected = True
                    nicspec.device.connectable.allowGuestControl = True
                    device_change.append(nicspec)
                    break

            config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
            task = vm.ReconfigVM_Task(config_spec)
            wait_for_tasks(service_instance, [task])
            module.exit_json(change=False, result="Successfully changed network")

        except vmodl.MethodFault as error:
            module.fail_json(change=False, msg="Caught vmodl fault : %s" % error.msg)

    def __call__(self):
        """
        execute module
        """
        self.change_vif()


if __name__ == "__main__":
    main = Main()
    main()

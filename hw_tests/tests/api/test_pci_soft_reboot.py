# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from hw_tests.tests.common import pci
from tempest.api.compute import base
from tempest import config
from tempest import test
from tempest.common import waiters

CONF = config.CONF

class ServersWithSpecificFlavorTestJSON(base.BaseV2ComputeAdminTest):
    run_ssh = CONF.validation.run_validation
    disk_config = 'AUTO'

    @classmethod
    def setup_credentials(cls):
        cls.prepare_instance_network()
        super(ServersWithSpecificFlavorTestJSON, cls).setup_credentials()

    @classmethod
    def setup_clients(cls):
        super(ServersWithSpecificFlavorTestJSON, cls).setup_clients()
        cls.flavor_client = cls.os_adm.flavors_client
        cls.client = cls.servers_client

    @classmethod
    def resource_setup(cls):
        cls.set_validation_resources()

        super(ServersWithSpecificFlavorTestJSON, cls).resource_setup()


    #@testtools.skipIf(not run_ssh, 'Instance validation tests are disabled.')
    @test.attr(type='gate')
    def test_assign_pci_soft_reboot_instance(self):
        #Get PCI related parameter and ready to test
        pci.get_pci_config(self)
        for info in self.infoList:
            info = info.split(':')
            name = info[0]
            pciid = info[1]
            flavor_with_pci_id = pci.create_flavor_with_extra_specs(self,name)

            admin_pass = self.image_ssh_password

            cont = pci.gen_rc_local_dict(pci.RC_LSPCI)
            print cont
            personality = [
                {'path': "/etc/rc.local",
                 'contents': cont}]

            user_data = pci.gen_user_data("\n".join(pci.CONSOLE_DATA))
            server_with_pci = (self.create_test_server(
                                      wait_until='ACTIVE',
                                      user_data=user_data,
                                      personality=personality,
                                      adminPass=admin_pass,
                                      flavor=flavor_with_pci_id))


            addresses = self.client.show_server(server_with_pci['id'])['server']
            self.server_id = server_with_pci['id']
            print self.server_id
            pci_info = pci.retry_get_pci_output(
                self.client.get_console_output, self.server_id)

            expect_pci = filter(lambda x: pciid in x, pci_info)
            self.assertTrue(not not expect_pci)

            pci_count = len(expect_pci)
            self.assertEqual(1, pci_count)
 
            #server = self.client.show_server(self.server_id)
            #linux_client = remote_client.RemoteClient(addresses,
            #                                self.ssh_user, password)
            #pci_flag = linux_client.get_pci(pciid)
            #self.assertTrue(pci_flag is not None)

            #pci_count = linux_client.get_pci_count(pciid)
            #pci_count = pci_count.strip()
            #self.assertEqual('1',pci_count)
            
            #self.client.reboot_server(self.server_id, 'SOFT')
            #self.assertEqual(202, resp.status)
            #waiters.wait_for_server_status(self.client, self.server_id, 'ACTIVE')



            self.servers_client.reboot_server(self.server_id, type='SOFT')
            waiters.wait_for_server_status(self.client, self.server_id, 'ACTIVE')
            print self.server_id

            pci_info = pci.retry_get_pci_output(
                self.client.get_console_output, self.server_id,
                DELIMITER="RC LSPCI")

            expect_pci = filter(lambda x: pciid in x, pci_info)
            self.assertTrue(not not expect_pci)

            pci_count = len(expect_pci)
            self.assertEqual(1, pci_count)

            #if self.run_ssh:
            # Log in and verify the boot time has changed
            #    linux_client = remote_client.RemoteClient(server, 
            #						self.ssh_user,password)

            #pci_recover_flag = linux_client.get_pci(pciid)
            #self.assertTrue(pci_recover_flag is not None)

            #pci_count = linux_client.get_pci_count(pciid)
            #pci_count = pci_count.strip()
            #self.assertEqual('1',pci_count)

class ServersWithSpecificFlavorTestXML(ServersWithSpecificFlavorTestJSON):
    _interface = 'xml'
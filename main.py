"""Main module of kytos/topology Kytos Network Application.

Manage the network topology
"""
import json

from kytos.core import KytosEvent, KytosNApp, log, rest
from kytos.core.helpers import listen_to

from napps.kytos.topology.models import Device, Interface, Port, Topology
from napps.kytos.topology import settings


class Main(KytosNApp):
    """Main class of kytos/topology NApp.

    This class is the entry point for this napp.
    """

    def setup(self):
        """Replace the '__init__' method for the KytosNApp subclass.

        The setup method is automatically called by the controller when your
        application is loaded.

        So, if you have any setup routine, insert it here.
        """
        self.topology = Topology()

    def execute(self):
        """Execute right after the setup method execution.

        You can also use this method in loop mode if you add to the above setup
        method a line like the following example:

            self.execute_as_loop(30)  # 30-second interval.
        """
        pass

    def shutdown(self):
        """Execute when your napp is unloaded.

        If you have some cleanup procedure, insert it here.
        """
        log.info('NApp kytos/topology shutting down.')

    @rest('devices')
    def get_device(self):
        """Return a json with all the devices in the topology.

        Responsible for the /api/kytos/topology/devices endpoint.

        e.g. [<list of devices>]

        Returns:
            string: json with all the devices in the topology

        """
        return json.dumps([device.to_json()
                           for device in self.topology.devices])

    @rest('links')
    def get_links(self):
        """Return a json with all the links in the topology.

        Responsible for the /api/kytos/topology/links endpoint.

        Returns:
            string: json with all the links in the topology.

        """
        return json.dumps([link.to_json() for link in self.topology.links])

    @rest('')
    def get_topology(self):
        """Return full topology.

        Responsible for the /api/kytos/topology endpoint.

        Returns:
            string: json with the full topology.

        """
        return json.dumps(self.topology.to_json())

    @listen_to('.*.switch(es)?.new')
    def handle_new_switch(self, event):
        """Create a new Device on the Topology.

        Handle the event of a new created switch and instantiate a new Device
        on the topology.

        """
        switch = event.content['switch']
        device = Device(switch.id)
        self.topology.add_device(device)
        self.log.debug('Switch %s added to the Topology.', device.id_)
        self.notify_topology_update()

    def notify_topology_update(self):
        """Send an event to notify about updates on the Topology."""
        name = 'kytos.topology.updated'
        content = self.topology.to_json()
        event = KytosEvent(name=name, content=content)
        self.controller.buffer.app.put(event)

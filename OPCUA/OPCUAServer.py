import os
import yaml
from threading import Thread
import time
import logging
from opcua import ua, uamethod, Server

from Database.Queries import DeviceQueries


class OPCUAServer:
    def __init__(self):
        directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file_name = os.path.join(directory, 'conf', 'prod.yaml')
        if not os.path.exists(config_file_name):
            config_file_name = os.path.join(directory, 'conf', 'dev.yaml')
        with open(config_file_name, 'r') as ymlfile:
            config = yaml.load(ymlfile)

        self._logger = logging.getLogger(__name__)
        self._port = config['opcuaserver']['port']
        self._ip_address = config['opcuaserver']['ip_address']
        self.thread_run_ok = True
        self.thread = Thread(target=self.server, args=())

    def server(self):
        # Now setup our server
        server = Server()
        server.set_endpoint("opc.tcp://" + self._ip_address + ":" + str(self._port) + "/")
        server.set_server_name("Service discovery OPCUA-Server")

        # Setup namespaces
        carriage_ns = server.register_namespace("carriage")
        artnet_ns = server.register_namespace("artnet")
        servicediscovery_ns = server.register_namespace("servicediscovery")

        # Setup namespavce servicediscovery
        sd_obj = server.nodes.objects.add_object(servicediscovery_ns, "service_discovery")
        # Input: name, hostname, device_class
        sd_obj.add_method(servicediscovery_ns, "update-device", self.update_device, [ua.VariantType.String,
                                                                                     ua.VariantType.String,
                                                                                     ua.VariantType.String,
                                                                                     ua.VariantType.String],
                          [ua.VariantType.String])

        sd_obj.add_method(servicediscovery_ns, "online-devices", self.get_online_devices, [ua.VariantType.UInt64],
                          [ua.VariantType.String])

        # Start server
        try:
            server.start()
            self._logger.info("OPCUA-Server started")

            while self.thread_run_ok:
                time.sleep(2)

            server.stop()
            self._logger.info("OPCUA-Server stopped")
        except OSError as e:
            self.thread_run_ok = False
            self._logger.critical("OS error: {0}".format(e))

    def start_server(self):
        self.thread_run_ok = True
        self.thread.start()

    def stop_server(self):
        self.thread_run_ok = False

    @uamethod
    def update_device(self, parent, name, hostname, device_class, location):
        device_queries = DeviceQueries()
        updated_device = device_queries.update_device({"name": name, "hostname": hostname,
                                                       "device_class": device_class, "location": location})
        if updated_device:
            return str(updated_device.to_dict())
        else:
            return "Something went wrong"

    @uamethod
    def get_online_devices(self, parent, last_updated_min_ago):
        device_queries = DeviceQueries()
        updated_devices = device_queries.get_online_devices(last_updated_min_ago)
        jsonified_devices = []
        for device in updated_devices:
            jsonified_devices.append(device.to_dict())

        return str(jsonified_devices)

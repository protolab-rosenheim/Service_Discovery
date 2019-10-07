import os
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from Webservice.ConnectionString import ConnectionString
from Database.DbModels import *


class DefaultQuery:
    __abstract__ = True

    def __init__(self):
        directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file_name = os.path.join(directory, 'conf', 'prod.yaml')
        if not os.path.exists(config_file_name):
            config_file_name = os.path.join(directory, 'conf', 'dev.yaml')
        with open(config_file_name, 'r') as ymlfile:
            self.config = yaml.load(ymlfile)

        # Create db session for sql alchemy queries
        engine = create_engine(ConnectionString.from_config(self.config['database']))
        self._Session = sessionmaker()
        self._Session.configure(bind=engine)


class DeviceQueries(DefaultQuery):
    def update_device(self, device_json):
        # Create a Session and make a query
        session = self._Session()
        device = session.query(Device).get(device_json['name'])

        # If device exists update, otherwise create new
        if device and device.name == device_json['name']:
            device.name = device_json['name']
            device.hostname = device_json['hostname']
            device.device_class = device_json['device_class']
            device.location = device_json['location']
            device.last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            device = Device(name=device_json['name'], hostname=device_json['hostname'],
                            device_class=device_json['device_class'],
                            location=device_json['location'],
                            last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            session.add(device)

        # Save device, on error make a rollback
        try:
            session.commit()
            device = session.query(Device).get(device_json['name'])
        except:
            session.rollback()
        finally:
            session.close_all()
            if device:
                return device
            else:
                return ''

    def get_online_devices(self, last_updated_min_ago):
        if not last_updated_min_ago:
            last_updated_min_ago = 5
        # Get datetime with timedelate from last_update_x_minutes_ago
        last_update = datetime.now() - timedelta(minutes=last_updated_min_ago)

        # Create a Session and make a query -> get all devices updated before xx
        session = self._Session()
        devices = session.query(Device).filter(Device.last_update >= last_update.strftime('%Y-%m-%d %H:%M:%S')).all()
        return devices

    def get_selected_devices(self, short_interval, long_interval):
        if not long_interval:
            long_interval = 5
        if not short_interval:
            short_interval = 1

        session = self._Session()
        devices = session.query(Device).all()

        datetime_now = datetime.now()  # using the same datetime_now
        # Get datetime with timedelate from last_updates_x_minutes_ago

        last_update_long = datetime_now - timedelta(minutes=long_interval)
        last_update_short = datetime_now - timedelta(minutes=short_interval)

        result_dic = {"short": [], "middle": [], "long": []}
        for device in devices:
            if device.last_update >= last_update_short:
                result_dic["short"].append(device.to_dict())
            elif device.last_update >= last_update_long:
                result_dic["middle"].append(device.to_dict())
            else:
                result_dic["long"].append(device.to_dict())

        return [result_dic]

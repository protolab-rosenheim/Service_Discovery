import os
import flask
import logging
import flask_restless
from flask_cors import CORS
from flask import request, abort, jsonify
import yaml
from opcua import Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .ConnectionString import ConnectionString
from .WebserviceResultBuilder import WebserviceResultBuilder
from Database.DbModels import *
from Database.Queries import DeviceQueries


class Webservice:
    @staticmethod
    def start_webservice():
        directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file_name = os.path.join(directory, 'conf', 'prod.yaml')
        if not os.path.exists(config_file_name):
            config_file_name = os.path.join(directory, 'conf', 'dev.yaml')
        with open(config_file_name, 'r') as ymlfile:
            config = yaml.load(ymlfile)

        app = flask.Flask(__name__)
        app.config['DEBUG'] = config['webservice']['debug']

        logger = logging.getLogger(__name__)

        app.config['SQLALCHEMY_DATABASE_URI'] = ConnectionString.from_config(config['database'])
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.app = app
        db.init_app(app)

        # Create the database tables.
        db.create_all()

        # Create db session for sql alchemy queries
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        _Session = sessionmaker()
        _Session.configure(bind=engine)

        # Create the Flask-Restless API manager.
        manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

        # Create API endpoints, which will be available at <api_version_string>/<tablename> by
        # default. Allowed HTTP methods can be specified as well.
        manager.create_api(Device, results_per_page=0, methods=['GET', 'DELETE'],
                           url_prefix=config['webservice']['api_version_string'])

        @app.route(config['webservice']['api_version_string'] + '/update-device', methods=['POST'])
        def update_device():
            api_call_params = request.get_json()
            device_queries = DeviceQueries()
            device = device_queries.update_device(api_call_params)
            return WebserviceResultBuilder.build_json_no_pagination(device.to_dict()), 201

        @app.route(config['webservice']['api_version_string'] + '/online-devices', methods=['GET'])
        def get_online_devices():
            # Get lastUpdatedMinAgo from URL params
            last_updated_min_ago = request.args.get('lastUpdatedMinAgo')

            # If lastUpdatedMinAgo was not in parameters, set default
            if last_updated_min_ago:
                # Try converting lastUpdatedMinAgo to int, if it fails raise 406 http error
                try:
                    last_updated_min_ago = int(last_updated_min_ago)
                except ValueError:
                    return 'lastUpdatedMinAgo cant be converted to an integer!', 406

            # Make database query for devices and return them
            device_queries = DeviceQueries()
            device = device_queries.get_online_devices(last_updated_min_ago)
            return WebserviceResultBuilder.build_json_from_db_models(device)

        @app.route(config['webservice']['api_version_string'] + '/selected-devices', methods=['GET'])
        def get_selected_devices():

            long_interval = request.args.get('long_interval')
            short_interval = request.args.get('short_interval')

            # If lastUpdatedMinAgo was not in parameters, set default
            if long_interval:
                # Try converting lastUpdatedMinAgo to int, if it fails raise 406 http error
                try:
                    long_interval = int(long_interval)
                except ValueError:
                    return 'long_interval cant be converted to an integer!', 406

            if short_interval:
                # Try converting lastUpdatedMinAgo to int, if it fails raise 406 http error
                try:
                    short_interval = int(short_interval)
                except ValueError:
                    return 'short_interval cant be converted to an integer!', 406

            # Make database query for devices and return them
            device_queries = DeviceQueries()
            # result is a dictionary packed into an array
            result = device_queries.get_selected_devices(short_interval, long_interval)
            return WebserviceResultBuilder.build_json(result)

        @app.route(config['webservice']['api_version_string'] + '/call', methods=['POST'])
        def call():
            api_call_params = request.get_json()

            if any(param not in api_call_params for param in ('serverUrl', 'methodPath')):
                abort(400)

            opcua_server_url = api_call_params['serverUrl']
            method_path = api_call_params['methodPath']

            if 'params' in api_call_params:
                method_parameter = api_call_params['params']
            else:
                method_parameter = None

            opcua_client = Client(opcua_server_url)

            try:
                opcua_client.connect()
                root_node = opcua_client.get_root_node()
                method = root_node.get_child(method_path)
                if method:
                    if type(method_parameter) == list:
                        root_node.call_method(method, *method_parameter)
                    if method_parameter:
                        root_node.call_method(method, method_parameter)
                    else:
                        root_node.call_method(method)
                else:
                    abort(400)
            except Exception as e:
                abort(500)
            finally:
                opcua_client.disconnect()
                return jsonify(
                    method=str(method_path),
                    status=200
                )

        cors = CORS(app)

        # start the flask loop
        app.run(host=config['webservice']['host'], port=config['webservice']['port'], threaded=True)

from flask import jsonify


class WebserviceResultBuilder:
    @staticmethod
    def build_json(objects):
        """Creates a JSON from a serializable objects list just like the Flask-Restless response:
        {"num_results": 21, "objects": [...], "page": 1, "total_pages": 1}"""
        return jsonify(
            num_results=len(objects),
            objects=objects,
            page=1,
            total_pages=1
        )

    @staticmethod
    def build_json_no_pagination(object):
        """Creates a JSON from a serializable object:
        {"entry1": "test", "entry2": "bla"}"""
        return jsonify(object)

    @staticmethod
    def build_json_from_db_models(objects):
        """Creates a JSON from a serializable objects list just like the Flask-Restless response:
        {"num_results": 21, "objects": [...], "page": 1, "total_pages": 1}"""
        jsonified_objects = []
        for object in objects:
            jsonified_objects.append(object.to_dict())

        return jsonify(
            num_results=len(objects),
            objects=jsonified_objects,
            page=1,
            total_pages=1
        )

    @staticmethod
    def get_results_with_description(cursor):
        """Takes a cursor, gets his results and joins it with the corresponding column description"""
        column_name = [column[0] for column in cursor.description]
        results = []
        # Join results with column description into a dict to serialize
        # see https://stackoverflow.com/a/16523148/5730444
        for row in cursor.fetchall():
            results.append(dict(zip(column_name, row)))
        return results

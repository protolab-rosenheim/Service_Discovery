class ConnectionString:
    @staticmethod
    def from_config(db_config):
        """Creates a SQL-Alchemy connection string from a config element containing a dialect, username, password,
        ip address, port and database name like so dialect://user:password@ip:port/database
        See also http://docs.sqlalchemy.org/en/latest/core/engines.html"""
        return db_config['dialect'] + '://' + db_config['user'] + ':' + \
               db_config['password'] + '@' + db_config['ip_address'] + ':' + \
               str(db_config['port']) + '/' + db_config['database']

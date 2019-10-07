from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class DbModelExtension(db.Model):
    __abstract__ = True

    def to_dict(self):
        tmp_dict = self.__dict__
        ret_dict = {}
        for key in self.__table__.columns.keys():
            if key in tmp_dict:
                if tmp_dict[key].__class__.__name__ == 'datetime':
                    ret_dict[key] = tmp_dict[key].isoformat()
                else:
                    ret_dict[key] = tmp_dict[key]
        return ret_dict

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.to_dict() == other.to_dict():
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Device(DbModelExtension):
    name = db.Column(db.Unicode, primary_key=True)
    hostname = db.Column(db.Unicode, nullable=False)
    device_class = db.Column(db.Unicode, nullable=False)
    location= db.Column(db.Unicode, nullable=True)
    last_update = db.Column(db.DateTime, nullable=False)

import uuid
import datetime

class ModelMixin:
    
    def to_dict(self):
        items={c.name: getattr(self, c.name) for c in self.__table__.columns}
        for key,value in items.items():
            if isinstance(value,(datetime.datetime, datetime.date)):
                items[key]=value.strftime('%Y-%m-%dT%H:%M:%SZ')
            elif isinstance(value, uuid.UUID):
                items[key]=str(value)
        return items
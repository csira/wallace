from wallace.db.base import KeyValueModel
from wallace.db.base import DoesNotExist, ValidationError


class MongoDocument(KeyValueModel):

    collection = None

    @classmethod
    def find_one(cls, **kwargs):
        data = cls.collection.fetchall(**kwargs)
        if not data:
            raise DoesNotExist
        if len(data) != 1:
            raise ValidationError('expected a unique result')
        return cls.construct(new=False, **data[0])

    @classmethod
    def find_all(cls, **kwargs):
        docs = cls.collection.fetchall(**kwargs)
        return map(lambda doc: cls.construct(new=False, **doc), docs)


    @classmethod
    def construct(cls, _id=None, **kwargs):
        f = super(MongoDocument, cls).construct
        if _id:
            return f(ident=_id, **kwargs)
        return f(**kwargs)


    def _read_data(self):
        data = self.collection.fetchone(_id=self.ident)
        if data:
            data.pop('_id', None)
        return data

    def _write_data(self, state, _):
        f = self.collection.add if self.is_new else self.collection.update
        f(_id=self.ident, **state)


    def delete(self):
        self.collection.delete(self.ident)

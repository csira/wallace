from wallace.db.base.nosql.model import NoSqlModel
from wallace.errors import DoesNotExist, ValidationError


class MongoDocument(NoSqlModel):

    collection = None

    @classmethod
    def find_one(cls, **kwargs):
        data = cls.collection.fetchall(**kwargs)
        if not data:
            raise DoesNotExist(701)
        if len(data) != 1:
            raise ValidationError(702, 'expected a unique result')
        return cls.construct(new=False, **data[0])

    @classmethod
    def find_all(cls, **kwargs):
        docs = cls.collection.fetchall(**kwargs)
        return [cls.construct(new=False, **doc) for doc in docs]


    @classmethod
    def construct(cls, _id=None, **kwargs):
        f = super(MongoDocument, cls).construct
        if _id:
            return f(key=_id, **kwargs)
        return f(**kwargs)

    @classmethod
    def exists(cls, **kw):
        raise NotImplementedError


    def read_from_db(self):
        data = self.collection.fetchone(_id=self.key)
        if data:
            data.pop('_id', None)
        return data

    def write_to_db(self, state, _):
        f = self.collection.add if self.is_new else self.collection.update
        f(_id=self.key, **state)


    def delete(self):
        self.collection.delete(self.key)

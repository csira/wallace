from wallace.db.base.attrs import DataType
from wallace.db.base.errors import DoesNotExist, ValidationError
from wallace.db.base.model import Base, Model


class _PKBase(Base):
    def __new__(cls, name, bases, dct):
        the_class = super(_PKBase, cls).__new__(cls, name, bases, dct)
        the_class._cbs_primary_key_fields = cls._get_pk_fields(bases, dct)

        if cls._is_proper_model(bases):
            if not the_class._cbs_primary_key_fields:
                raise TypeError('no primary keys set')

        return the_class

    @staticmethod
    def _get_pk_fields(bases, dct):
        pk_fields = set()

        for base in bases:  # support model inheritance
            for key in getattr(base, '_cbs_primary_key_fields', []):
                pk_fields.add(key)

        for key, val in dct.iteritems():
            if isinstance(val, DataType) and val.is_pk:
                pk_fields.add(key)
            elif key in pk_fields:      # catch any superclass pk fields
                pk_fields.remove(key)   # overridden here by a non-pk one

        return tuple(pk_fields)

    @staticmethod
    def _is_proper_model(bases):
        # Model hierarchy:
        #     <model> -> <DB model wrapper (eg PostgresModel)> ->
        #     RelationalModel -> Model -> object
        # ergo, the hierarchy cardinality for any proper model subclass
        # will be at least 4

        base_tree = []
        while bases:
            base_tree.append(bases)
            bases = map(lambda b: list(b.__bases__), bases)
            bases = sum(bases, [])

        return len(base_tree) > 3


def throw_null_pk_field_error(attr):
    msg = 'primary key field "%s" cannot be null' % attr
    raise ValidationError(msg)


class RelationalModel(Model):

    __metaclass__ = _PKBase

    @classmethod
    def fetch(cls, **kwargs):
        inst = cls.construct(new=False, **kwargs)
        inst.pull()
        return inst


    def pull(self):
        self._validate_pk()
        super(RelationalModel, self).pull()

    def push(self, *a, **kw):
        self._validate_pk()
        super(RelationalModel, self).push(*a, **kw)

    def _validate_pk(self, silent=False):
        for attr in self._cbs_primary_key_fields:
            if getattr(self, attr, None) is None:
                if silent:
                    return False
                throw_null_pk_field_error(attr)
        return True


    @property
    def primary_key(self):
        # The primary key CURRENTLY stored in the db.
        # If a pk field is changed, this will continue to return the old
        # value so updates can find the row.

        if self.is_new:
            raise DoesNotExist('new model')

        pk = {}
        for attr in self._cbs_primary_key_fields:
            try:
                pk[attr] = self._cbs_db_data[attr]
            except KeyError:
                throw_null_pk_field_error(attr)
        return pk

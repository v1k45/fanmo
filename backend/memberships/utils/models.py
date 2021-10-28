from django.db import models
from inflection import underscore, pluralize


class BaseModelMeta(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        defined_meta = attrs.get("Meta")

        # custom db table name
        if defined_meta and hasattr(defined_meta, "db_table"):
            custom_db_table = defined_meta.db_table
        else:
            custom_db_table = pluralize(underscore(name))

        # custom realted name
        if defined_meta and hasattr(defined_meta, "default_related_name"):
            custom_related_name = defined_meta.default_realted_name
        else:
            custom_related_name = pluralize(underscore(name))

        # custom ordering
        if defined_meta and hasattr(defined_meta, "ordering"):
            custom_ordering = defined_meta.ordering
        else:
            custom_ordering = ("-created_at",)

        super_class = super(BaseModelMeta, cls).__new__(cls, name, bases, attrs)

        # Proxy models should keep their existing db_table
        if not hasattr(defined_meta, "proxy") or not defined_meta.proxy:
            super_class._meta.db_table = custom_db_table
            super_class._meta.original_attrs["db_table"] = custom_db_table

            super_class._meta.default_related_name = custom_related_name
            super_class._meta.original_attrs[
                "default_related_name"
            ] = custom_related_name

            super_class._meta.ordering = custom_ordering
            super_class._meta.original_attrs["ordering"] = custom_ordering

        return super_class


class BaseModel(models.Model, metaclass=BaseModelMeta):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

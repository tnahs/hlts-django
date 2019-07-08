class UpdateFieldsMixin:
    @staticmethod
    def update_fields(instance, data: dict, fields: list):
        """ Sets instance fields to new value if new value exists. Runs:
        instance.field = data.get(field, instance.field) on each field. """

        for field_name in fields:

            field_data = data.get(field_name, None)

            if field_data is not None:
                setattr(instance, field_name, field_data)

        instance.save()

        return instance

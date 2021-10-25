from model_utils.fields import StatusField as ModelUtilsStatusField
from django_fsm import FSMFieldMixin


class StateField(FSMFieldMixin, ModelUtilsStatusField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("choices_name", "")
        super().__init__(*args, **kwargs)

from rest_framework import mixins


class CreateDeleteMixin(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin):
    pass

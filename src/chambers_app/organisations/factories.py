# import factory

# from django.contrib.auth import get_user_model

# from .models import ChamberOfCommerce


# class OrgFactory(factory.DjangoModelFactory):
#     class Meta:
#         model = ChamberOfCommerce

#     name = factory.Sequence(lambda n: 'Chamber %d of Commerce' % n)
#     descr = "Test organisation"

#     @factory.post_generation
#     def users(self, create, extracted, **kwargs):
#         self.users.set(
#             get_user_model().objects.all()
#         )

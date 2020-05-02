# import uuid

# from django.conf import settings
# from django.db import models


# # class ChamberOfCommerce(models.Model):
# #     id = models.UUIDField(default=uuid.uuid4, primary_key=True)
# #     created_at = models.DateTimeField(auto_now_add=True)
# #     created_by = models.ForeignKey(
# #         settings.AUTH_USER_MODEL, models.CASCADE,
# #         blank=True, null=True
# #     )
# #     updated_at = models.DateTimeField(auto_now=True)

# #     name = models.CharField(max_length=256)
# #     descr = models.TextField(blank=True)

# #     users = models.ManyToManyField(
# #         settings.AUTH_USER_MODEL,
# #         symmetrical=False,
# #         related_name='chambersofcommerce',
# #         blank=True,
# #     )

# #     def __str__(self):
# #         return self.name

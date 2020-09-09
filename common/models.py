from django.db import models

# Create your models here.

class BaseModel(models.Model):
    created_date =  models.DateTimeField('first created date', auto_now_add=True)
    last_modified_date = models.DateTimeField('last modified date', auto_now=True)

    created_by_user_id = models.IntegerField("created by user id", null=True)
    created_by_user_name = models.CharField("created by user name", max_length=200, null=True)

    last_modified_by_user_id = models.IntegerField("last modified by user id", null=True)
    last_modified_by_user_name = models.CharField("last modified by user name", max_length=200, null=True)

    is_deleted = models.BooleanField('is deleted', default=False, null=False)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        super().save(*args, **kwargs)  # Call the "real" save() method.
        return True

    def save(self, *args, **kwargs):        
        super().save(*args, **kwargs)  # Call the "real" save() method.
        return True

    def is_deleted_display(seft):
        if(seft.is_deleted == True):
            return "Yes"
        else:
            return "No"
    is_deleted_display.short_description  = "Is Deleted?"
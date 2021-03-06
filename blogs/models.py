from django.db import models

# Create your models here.
class blogs(models.Model):
    heading = models.CharField(max_length=500)
    sample_text = models.CharField(max_length=500,default="none")
    content = models.TextField()
    date = models.DateField()
    user_email = models.EmailField()
    user_name = models.CharField(max_length=100)
class tag(models.Model): #to avoid multiple copy of same tag
    name = models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.name
class taginblog(models.Model):
    blog = models.ForeignKey('blogs', on_delete=models.CASCADE)
    tag = models.ForeignKey('tag', on_delete=models.CASCADE)
    class Meta:
        unique_together=(('blog','tag'))
        

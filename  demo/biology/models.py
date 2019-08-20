from django.db import models
from django.forms import ModelForm, FileInput
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone


class UploadFile(models.Model):
    class Meta:
        verbose_name_plural='Uploaded_Model'
    def __str__(self):
        return self.file.name.split('/')[-1] + ";" +str(self.upload_time.strftime('%Y-%m-%d,%H:%m:%S'))
    file = models.FileField(upload_to="upload/%Y%m%d")
    hash_id = models.CharField(max_length=255, primary_key=True)
    upload_time = models.DateTimeField(default=timezone.now())
# @receiver(post_delete, sender=UploadFile)
# def upload_file_delete(sender, instance, **kwargs):
#     instance.file.delete(False) 
class UploadFileForm(ModelForm):
    class Meta:
        model = UploadFile
        fields = ['file']
        widgets = {
            'file' : FileInput(attrs={'class' : 'custom-file-input', 'id' : 'customFile'}),
        }

class InputParams(models.Model):
    class Meta:
        verbose_name_plural='FBA_Results'
    def __str__(self):
        return "Inputs and FBA Results of " + self.upload_file_name
    GC = models.CharField(max_length=255)  
    EA = models.CharField(max_length=255) 
    H = models.CharField(max_length=255)  
    H2O = models.CharField(max_length=255)
    PI = models.CharField(max_length=255)
    NH4 = models.CharField(max_length=255)  
    NO3 = models.CharField(max_length=255)  
    SO4 = models.CharField(max_length=255)  
    O2 = models.CharField(max_length=255)  
    input_hash_id = models.CharField(max_length=255, primary_key=True)    # hash value of input file and inputs
    upload_file = models.ForeignKey(UploadFile, on_delete=models.CASCADE)
    upload_file_name = models.CharField(max_length=255)

class DownloadFile(models.Model):   # model of input file processed by COBRA
    def __str__(self):
        return self.download_file.name
    download_file = models.FileField(upload_to="download/%Y%m%d")
    download_file_hash_id = models.CharField(max_length=255, primary_key=True)    # hash value of input file and inputs 
    input_params = models.ForeignKey(InputParams, on_delete=models.CASCADE)   
   
# @receiver(post_delete, sender=DownloadFile)
# def download_file_delete(sender, instance, **kwargs):
#     instance.download_file.delete(False) 

class DecompositionFile(models.Model):
    class Meta:
        verbose_name_plural='Uploaded_Decomposition_File'
    def __str__(self):
        return self.file_name
    file = models.FileField(upload_to="decomposition/%Y%m%d")
    file_id = models.CharField(max_length=255, primary_key=True)
    file_name = models.CharField(max_length=255)
    
class CycleImg(models.Model):
    img_id = models.CharField(max_length=255, primary_key=True)
    img = models.ImageField(upload_to="img/%Y%m%d")
    value = models.FloatField(default=0)
    file = models.ForeignKey(DecompositionFile, on_delete=models.CASCADE)
# @receiver(post_delete, sender=CycleImg)
# def img_delete(sender, instance, **kwargs):
#     instance.img.delete(False) 
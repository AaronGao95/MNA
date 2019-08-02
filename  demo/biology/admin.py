from django.contrib import admin
from biology.models import UploadFile, DownloadFile, CycleImg, InputParams

# Register your models here.
class InputParamsInline(admin.TabularInline):
    model = InputParams
    extra = 0
    max_num = 20

class DownloadFileInline(admin.TabularInline):
    model = DownloadFile
    extra = 0
    max_num = 20

class CycleImgInline(admin.TabularInline):
    model = CycleImg
    extra = 0
    max_num = 20

class UploadFileAdmin(admin.ModelAdmin):
    inlines = [InputParamsInline]
    # list_display = ('file','hash_id')
    # fieldsets = (['File', {'fields': ('file',),}],
    #     ['Advanced', {'fields': ('hash_id',)}]
    # )

class InputParamsAdmin(admin.ModelAdmin):
    inlines = [DownloadFileInline]

class DownloadFileAdmin(admin.ModelAdmin):
    fieldsets = (
        ['Download File', {'fields':('download_file', 'upload_file')}],
        ['Inputs', {'fields':('GC','EA','H','H2O','PI','NH4','NO3','SO4','O2')}]
    )

admin.site.register(UploadFile, UploadFileAdmin)
admin.site.register(InputParams, InputParamsAdmin)

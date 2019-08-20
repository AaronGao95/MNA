from django.contrib import admin
from biology.models import UploadFile, DownloadFile, CycleImg, InputParams, DecompositionFile


admin.site.site_header = "MNA Administration"
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

class DecompositionFileAdmin(admin.ModelAdmin):
    inlines = [CycleImgInline]


admin.site.register(UploadFile, UploadFileAdmin)
admin.site.register(InputParams, InputParamsAdmin)
admin.site.register(DecompositionFile, DecompositionFileAdmin)

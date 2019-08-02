from django.shortcuts import render
from biology import models
import sys, mmap
import numpy as np
from io import BytesIO, StringIO
from django.http import FileResponse
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from wsgiref.util import FileWrapper
from django.http import Http404
from django.views import View
sys.path.append("/Users/aarongao/Desktop/Master Project/Site/ demo")
from ownPackages.opt import FileProcessing, md5File, md5String, GetImg_top_10, SearchImg, plot, GetScriptsInput
from demo.settings import *
import re, base64, json
from django.core.files.images import ImageFile
from django.core.files import File
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage


def home(request):
    context = {}
    cookie = get_cookie(request)
    if request.method == "POST":
        form = models.UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            GC = str(request.POST.get("growthCondition"))
            EA= float(request.POST.get("ex_ac_lowerBound"))
            H = float(request.POST.get("h_lowerBound"))
            H2O = float(request.POST.get("h2o_lowerBound"))
            PI = float(request.POST.get("pi_lowerBound"))
            NH4 = float(request.POST.get("nh4_lowerBound"))
            NO3 = float(request.POST.get("no3_lowerBound"))
            SO4= float(request.POST.get("so4_lowerBound"))
            O2 = float(request.POST.get("o2_lowerBound"))
            # upload file
            obj = form.save(commit=False)
            hash_id = md5File(obj.file)
           # check if the file exists or not
            file_exist_obj = models.UploadFile.objects.filter(hash_id=hash_id)	    
            if not file_exist_obj.exists():
                upload_file_obj = models.UploadFile(file=obj.file, hash_id=hash_id)
            else:
                upload_file_obj = file_exist_obj.first()
            # upload file end

            # check the md5 of upload file and inputs exists or not
            inputs = (hash_id,GC,EA,H,H2O,PI,NH4,NO3,SO4,O2)
            inputs_str = ''
            for i in inputs:
                inputs_str = inputs_str + str(i) + '?'
            input_hash_id = md5String(str(inputs_str))
            if not models.InputParams.objects.filter(input_hash_id=input_hash_id).exists():
                input_obj = models.InputParams(upload_file_id=hash_id,GC=GC,EA=EA,H=H,H2O=H2O,PI=PI,NH4=NH4,NO3=NO3,SO4=SO4,O2=O2,\
                    input_hash_id=input_hash_id,upload_file_name=obj.file.name.split('/')[-1])
                download_file_hash_id = md5String(input_hash_id+".txt")    
                # file processed by COBRA, save results as txt as default
                params = {}
                params['download_file_hash_id'] = download_file_hash_id
                params['upload_file_obj'] = upload_file_obj
                params['input_obj'] = input_obj
                params['download_file_obj'] = models.DownloadFile(input_params_id=input_hash_id, download_file_hash_id=download_file_hash_id)
                params['file_name'] = obj.file.name.split('/')[-1]
                params['growth_condition'] = GC
                params['ex_ac_lowerBound'] = EA
                params['h_lowerBound'] = H
                params['h2o_lowerBound'] = H2O
                params['pi_lowerBound'] = PI
                params['nh4_lowerBound'] = NH4
                params['no3_lowerBound'] = NO3
                params['so4_lowerBound'] = SO4
                params['o2_lowerBound'] = O2

                status = FileProcessing(params) # download_obj will be saved in this function
                if status == False:
                    form = models.UploadFileForm()
                    if cookie != None:
                        context['file'] = cookie
                        context['exception'] = True
                        context['form'] = form
                    response = render(request, 'home.html', context)
                    return response
                # end

            response = HttpResponseRedirect('/download/'+input_hash_id)
            response.set_cookie('hash_id', input_hash_id, expires=60*60*24*7)
            response.set_cookie('file_name', obj.file.name.split('/')[-1], expires=60*60*24*7)
            context['file'] = {'hash_id':input_hash_id, 'file_name':obj.file.name}
            if cookie != None:
                context["file"]['decomp_file_id'] = cookie["decomp_file_id"]
                context["file"]['decomp_file_name'] = cookie["decomp_file_name"]
            return response
    else:
        form = models.UploadFileForm()
    if cookie != None:
        context['file'] = cookie
    context['form'] = form
    return render(request, 'home.html', context)

def download(request, input_hash_id):
    params = {}
    obj = models.InputParams.objects.filter(input_hash_id=input_hash_id)
    if not obj.exists():
        raise Http404
    upload_file_name = obj.first().upload_file_name
    context = {}
    context['file'] = {'hash_id':input_hash_id, 'file_name':upload_file_name}
    cookie = get_cookie(request)
    if cookie != None:
        context["file"]['decomp_file_id'] = cookie["decomp_file_id"]
        context["file"]['decomp_file_name'] = cookie["decomp_file_name"]
    return render(request, 'download.html', context)

def download_content(request, input_hash_id, save_flag):
    save_flag = save_flag.lower()
    download_file_hash_id = md5String(input_hash_id+"."+save_flag)
    obj = models.InputParams.objects.filter(input_hash_id=input_hash_id)
    if not obj.exists():
        raise Http404
    obj = obj.first()
    params = {}
    download_obj = models.DownloadFile.objects.filter(download_file_hash_id=download_file_hash_id)
    if not download_obj.exists():
        upload_file_obj = obj.upload_file
        params['upload_file_obj'] = upload_file_obj
        params['input_obj'] = obj
        params['download_file_hash_id'] = download_file_hash_id
        params['download_file_obj'] = models.DownloadFile(input_params_id=obj.pk, download_file_hash_id=download_file_hash_id)
        params['file_name'] = obj.upload_file_name
        params['growth_condition'] = obj.GC
        params['ex_ac_lowerBound'] = obj.EA
        params['h_lowerBound'] = obj.H
        params['h2o_lowerBound'] = obj.H2O
        params['pi_lowerBound'] = obj.PI
        params['nh4_lowerBound'] = obj.NH4
        params['no3_lowerBound'] = obj.NO3
        params['so4_lowerBound'] = obj.SO4
        params['o2_lowerBound'] = obj.O2
        process_status = FileProcessing(params, save_flag=save_flag)
        if process_status == False:
            form = models.UploadFileForm()
            response = render(request, 'home.html', {'exception':True, 'form':form})
            return response
    new_download_obj = models.DownloadFile.objects.filter(download_file_hash_id=download_file_hash_id).first()
    download_file = File(new_download_obj.download_file)
    response = FileResponse(download_file)
    response['Content-Type'] = 'application/octet-stream' #设置头信息，告诉浏览器这是个文件
    Cont_Dis = 'attachment;filename=%s%s%s'%('Results', '.', save_flag)
    response['Content-Disposition'] = Cont_Dis
    return response

def decomposition(request, file_id):
    context = {}
    obj = models.DecompositionFile.objects.filter(file_id=file_id)
    if not obj.exists():
        raise Http404 
    file_name = obj.first().file_name
    context['file'] = {'decomp_file_id':file_id, 'decomp_file_name':file_name}
    cookie = get_cookie(request)
    if cookie != None:
        context["file"]['hash_id'] = cookie["hash_id"]
        context["file"]['file_name'] = None
    file = File(obj.first().file.file)
    with file.open() as file, mmap.mmap(file.fileno(),0,access=mmap.ACCESS_READ) as m:
        elements = []
        values = []
        ele_append = elements.append
        val_append = values.append
        while True:
            line = m.readline().strip()
            line = line.split(b'/')
            element = line[0].decode('utf-8').split()
            value = float(line[1])
            ele_append(element)
            val_append(value)
            if m.tell()==m.size():
                break

    # sort file
    a = list(zip(range(0,len(values)), values)) 
    del values
    dtype = [('eles_inx', np.int_),('vals', np.float_)]
    arr = np.array(a, dtype=dtype)
    arr = np.sort(arr, order='vals')
    context['lines'] = []
    arr = arr[-10:] # top ten
    arr = arr[::-1] # reverse array
    for i in arr:
        element = elements[i['eles_inx']]
        value = i['vals']
        context['lines'].append({'cycle':element, 'value':value})
    del elements, arr
    # end sort file

    # cookie = get_cookie(request)
    # if cookie != None:
    #     context['cookie'] = cookie

    return render(request, 'decomposition.html', context)


def visualisation(request, file_id):
    context = {}
    obj = models.DecompositionFile.objects.filter(file_id=file_id)
    if not obj.exists():
        raise Http404
    file_name = obj.first().file_name
    context['file'] = {'decomp_file_id':file_id, 'decomp_file_name':file_name}
    cookie = get_cookie(request)
    if cookie != None:
        context["file"]['hash_id'] = cookie["hash_id"]
        context["file"]['file_name'] = None
    # return top 10 figures
    GetImg_top_10(file_id)
    context['imgs'] = models.CycleImg.objects.filter(file=file_id)
    # end
    return render(request, 'visualisation.html', context)

def search(request, file_id):
    context = {}
    obj = models.DecompositionFile.objects.filter(file_id=file_id)
    if not obj.exists():
        raise Http404
    obj = obj.first()
    file_name = obj.file_name
    context['file'] = {'decomp_file_id':file_id, 'decomp_file_name':file_name}
    cookie = get_cookie(request)
    if cookie != None:
        context["file"]['hash_id'] = cookie["hash_id"]
        context["file"]['file_name'] = None     # only display decomp_file_name
    if request.method == 'GET':
        element_name = request.GET.get('name')
        upper = request.GET.get('upper')
        lower = request.GET.get('lower')
        context['name'] = str(element_name)
        context['upper'] = upper
        context['lower'] = lower
        if upper != "":
            upper = float(upper)
        else:
            upper = float("nan")
        if lower != "":
            lower = float(lower)
        else:
            lower = float("nan")
        results = SearchImg(element_name, obj, upper=upper, lower=lower)
        if results == False:
            context['results_length'] = 0
        else:
            results = list(results)
            context['results_length'] = len(results)
            page = request.GET.get("page",1)
            currentPage = int(page)
            pages = Paginator(results, 15)
            try:
                results = pages.page(page)
            except PageNotAnInteger:
                results = pages.page(1)
            except EmptyPage:
                results = pages.page(pages.num_pages)
            except InvalidPage:
                raise Http404
            # slice paginator
            if currentPage >=5:
                page_range = pages.page_range[currentPage-5:currentPage+4]
            else:
                page_range = pages.page_range[0:currentPage+4]
            # end
            context['page_range'] = page_range
            context["pages"] = pages
            context['results'] = results#   list[0][0]==element, list[0][1]==value
            context["currentPage"] = currentPage
        # end
    return render(request, 'search.html', context)

def vis_download(request, img_id):
    obj = models.CycleImg.objects.filter(img_id=img_id)
    if not obj.exists():
        raise Http404
    obj = obj.first()
    # path = MEDIA_ROOT + '/' + obj.img   #   absolute path
    img = ImageFile(obj.img)
    response = FileResponse(img)
    response['Content-Type'] = 'image/png' #设置头信息，告诉浏览器这是个文件
    Cont_Dis = 'attachment;filename=%s%s%s'%('Cycle', '.', 'png')
    response['Content-Disposition'] = Cont_Dis
    return response

def decomp_upload(request):
    cookie = get_cookie(request)
    context = {'file':{}}
    if cookie != None:
        context["file"]['hash_id'] = cookie["hash_id"]
        context["file"]['decomp_file_id'] = cookie["decomp_file_id"]
    return render(request, 'decomp-upload.html', context)

def decomp_scripts(request):
    cookie = get_cookie(request)
    if cookie != None:
        del cookie['decomp_file_name']
    context = {'file':cookie}
    return render(request, 'scripts.html', context)

def generate_input(request, input_hash_id):
    if request.method == "GET":
        compartment = request.GET.get("compartments")
        obj = models.InputParams.objects.filter(input_hash_id=input_hash_id)
        if not obj.exists():
            raise Http404
        txt_obj_id = md5String(input_hash_id+".txt")
        txt_obj = models.DownloadFile.objects.get(download_file_hash_id=txt_obj_id)
        buffer = GetScriptsInput(txt_obj, compartment=compartment)
        response = HttpResponse(FileWrapper(buffer), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=chlamydomonas_lna.csv'
        return response


def handler_404(request):
    return render(request, '404.html')

def ajax_search(request):
    if request.method == "GET":
        name = request.GET.get("name")
        upper = float(request.GET.get("upper"))
        lower = float(request.GET.get("lower"))
        file_id = request.GET.get("file")
        if name==None or upper==None or lower==None or file_id==None:
            raise Http404
        data = {}
        obj = models.DecompositionFile.objects.filter(file_id=file_id).first()
        res = SearchImg(name, obj, upper=upper, lower=lower)
        if res == False:
            data['count'] = 0
        else:
            data['count'] = len(list(res))
        return JsonResponse(data)

def ajax_view(request):
    data = {}
    if request.method == "GET":
        elements = request.GET.get("elements")
        value = request.GET.get("value")
        if elements == None or value == None:
            raise Http404
        elements = elements.split()    # replace white-space
        res = plot((elements,value))
        buffer = res['buffer']
        contents = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        img = "data:image/png;base64," + contents
        data['img'] = img
    return JsonResponse(data)

def search_download(request):
    if request.method == "GET":
        elements = request.GET.get("elements")
        value = request.GET.get("value")  
        elements = elements.split()
        res = plot((elements,value))
        buffer = res['buffer']
        buffer.seek(0)  # reset to the start
        response = FileResponse(buffer)
        response['Content-Type'] = 'image/png'
        Cont_Dis = 'attachment;filename=%s%s%s'%('Cycle', '.', 'png')
        response['Content-Disposition'] = Cont_Dis
    return response

def ajax_upload(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        if file.size == 0:
            return JsonResponse({'flag':False})
        file_id = md5File(file)
        file_name = file.name.split("/")[-1]
        if not models.DecompositionFile.objects.filter(file_id=file_id).exists():
            elements = []
            values = []
            ele_append = elements.append
            val_append = values.append
            try:
                file.fileno()
                with file.open() as file, mmap.mmap(file.fileno(),0,access=mmap.ACCESS_READ) as m:
                    while True:
                        try:
                            line = m.readline().strip()
                            line = line.split(b'/')
                            element = line[0].decode('utf-8')
                            value = float(line[1])
                            ele_append(element)
                            val_append(value)
                        except:
                            return JsonResponse({'flag':False})
                        if m.tell()==m.size():
                            break
            except:
                with file.open() as file:
                    lines = file.readlines()
                    for line in lines:
                        try:
                            line = line.strip()
                            line = line.split(b'/')
                            element = line[0]
                            value = float(line[1])
                            ele_append(element)
                            val_append(value)
                        except:
                            return JsonResponse({'flag':False})

            # sort file
            a = list(zip(range(0,len(values)), values)) 
            del values
            dtype = [('eles_inx', np.int_),('vals', np.float_)]
            arr = np.array(a, dtype=dtype)
            arr[::-1].sort(order='vals')
            buffer = StringIO()
            for i in arr:
                eles = elements[i['eles_inx']]
                line = '{}{}{}{}'.format(eles, '/', i['vals'],'\n')
                buffer.write(line)
            file = File(buffer)
            obj = models.DecompositionFile(file_id=file_id, file_name=file_name)
            obj.file.save(file_name, file)
            obj.save()
            buffer.close()
        GetImg_top_10(file_id)    
        url = "/decomp/visualisation/"+str(file_id)
        response = JsonResponse({'url':url, 'flag':True})
        response.set_cookie("decomp_file_id", str(file_id), expires=60*60*24*7)
        response.set_cookie("decomp_file_name", file_name, expires=60*60*24*7)
    return response

def download_scripts(request, os):
    # mac/linux os==0
    # windows os==1
    if int(os) == 0:
        obj = models.DecompositionScripts.objects.get(id=1)
    else:
        obj = models.DecompositionScripts.objects.get(id=2)        
    scripts = File(obj.scripts)
    response = FileResponse(scripts)
    response['Content-Type'] = 'application/zip' #设置头信息，告诉浏览器这是个文件
    Cont_Dis = 'attachment;filename=%s%s%s'%('Decomposition_Scripts', '.', 'zip')
    response['Content-Disposition'] = Cont_Dis
    return response


def guidance(request):
    cookie = get_cookie(request)
    if cookie != None:
        del cookie['file_name']     # do not display current file
        del cookie['decomp_file_name']
    context = {'file':cookie}
    return render(request, "guidance.html", context)

def get_cookie(request):
    context = {}
    context['hash_id'] = request.COOKIES.get('hash_id')
    context['file_name'] = request.COOKIES.get('file_name')
    context['decomp_file_id'] = request.COOKIES.get("decomp_file_id")
    context['decomp_file_name'] = request.COOKIES.get("decomp_file_name")
    if context['hash_id'] != None and context['file_name'] != None\
        or context['decomp_file_id'] != None and context['decomp_file_name'] != None:
        return context
    else:
        return None
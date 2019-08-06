import cobra
import pandas as pd
import re
from hashlib import md5
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO, StringIO
from multiprocessing import Pool
from biology import models
from django.core.files.images import ImageFile
from django.core.files import File
import mmap, math


def md5File(file):
    m = md5()
    m.update(file.read())
    return m.hexdigest()
def md5String(string):
    m = md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()
    
    
def FileProcessing(parameters):
    try:
        DW = 3e-11 # average dry weight of log phase chlamy cell = 48 pg (Mitchell 1992)
        CPerStarch300 = 1800 # derived from starch300 chemical formula
        ChlPerCell = (13.9+4)/(1e7) # 13.9 +- 4 micrograms Chl/10^7 cells (Gfeller 1984)
        starchDegAnLight = (4.95+1.35)*(1/1000)*(1/CPerStarch300)*(ChlPerCell/1000)*(1/DW) # approx. SS rate of anaerobic starch degradation in light = 4.95 +- 1.35 micromol C/mg Chl/hr (Gfeller 1984)
        starchDegAerLight = (2/3)*(4.95+1.35)*(1/1000)*(1/CPerStarch300)*(ChlPerCell/1000)*(1/DW) # approx. SS rate of aerobic starch degradation in light = 2/3 of anaerobic rate (Gfeller 1984)
        starchDegAnDark = (13.1+3.5)*(1/1000)*(1/CPerStarch300)*(ChlPerCell/1000)*(1/DW) # approx. SS rate of anaerobic starch degradation in dark = 13.1 +- 3.5 micromol C/mg Chl/hr (Gfeller 1984)
        starchDegAerDark = (2/3)*starchDegAnDark # approx. SS rate of aerobic starch degradation in dark = 2/3 of anaerobic rate (Gfeller 1984) = 2/3 of anaerobic rate (Gfeller 1984)
        
        # file=open("/Users/aarongao/Desktop/Master Project/Site/ demo/ownPackages/iRC1080-Chapman2.xml", "rb")
        # model = cobra.io.read_sbml_model(file)

        model = cobra.io.read_sbml_model(parameters['upload_file_obj'].file.open())

        model.reactions.get_by_id("Biomass_Chlamy_auto").objective_coefficient = 0
        model.reactions.get_by_id("Biomass_Chlamy_mixo").objective_coefficient = 0
        model.reactions.get_by_id("Biomass_Chlamy_hetero").objective_coefficient = 0
        if parameters['growth_condition'] == "auto":
            model.reactions.get_by_id("Biomass_Chlamy_auto").objective_coefficient = 1
        elif parameters['growth_condition'] == "mixo":
            model.reactions.get_by_id("Biomass_Chlamy_mixo").objective_coefficient = 1
        elif parameters['growth_condition'] == "hetero":
            model.reactions.get_by_id("Biomass_Chlamy_hetero").objective_coefficient = 1

        model.reactions.get_by_id("PRISM_solar_litho").upper_bound = 0
        model.reactions.get_by_id("PRISM_solar_litho").lower_bound = 0
        model.reactions.get_by_id("PRISM_solar_exo").upper_bound = 0
        model.reactions.get_by_id("PRISM_solar_exo").lower_bound = 0
        model.reactions.get_by_id("PRISM_incandescent_60W").upper_bound = 0
        model.reactions.get_by_id("PRISM_incandescent_60W").lower_bound = 0
        model.reactions.get_by_id("PRISM_fluorescent_warm_18W").upper_bound = 0
        model.reactions.get_by_id("PRISM_fluorescent_warm_18W").lower_bound = 0
        model.reactions.get_by_id("PRISM_fluorescent_cool_215W").upper_bound = 0
        model.reactions.get_by_id("PRISM_fluorescent_cool_215W").lower_bound = 0
        model.reactions.get_by_id("PRISM_metal_halide").upper_bound = 0
        model.reactions.get_by_id("PRISM_metal_halide").lower_bound = 0
        model.reactions.get_by_id("PRISM_high_pressure_sodium").upper_bound = 0
        model.reactions.get_by_id("PRISM_high_pressure_sodium").lower_bound = 0
        model.reactions.get_by_id("PRISM_growth_room").upper_bound = 0
        model.reactions.get_by_id("PRISM_growth_room").lower_bound = 0
        #model.reactions.get_by_id("PRISM_white_LED").upper_bound = 0
        #model.reactions.get_by_id("PRISM_white_LED").lower_bound = 0
        model.reactions.get_by_id("PRISM_design_growth").upper_bound = 10
        model.reactions.get_by_id("PRISM_design_growth").lower_bound = 10

        model.reactions.get_by_id("EX_h_LPAREN_e_RPAREN_").lower_bound = -parameters['h_lowerBound']
        model.reactions.get_by_id("EX_h2o_LPAREN_e_RPAREN_").lower_bound = -parameters['h2o_lowerBound']
        model.reactions.get_by_id("EX_pi_LPAREN_e_RPAREN_").lower_bound = -parameters['pi_lowerBound']
        model.reactions.get_by_id("EX_nh4_LPAREN_e_RPAREN_").lower_bound = -parameters['nh4_lowerBound']
        model.reactions.get_by_id("EX_no3_LPAREN_e_RPAREN_").lower_bound = -parameters['no3_lowerBound']
        model.reactions.get_by_id("EX_so4_LPAREN_e_RPAREN_").lower_bound = -parameters['so4_lowerBound']
        model.reactions.get_by_id("EX_o2_LPAREN_e_RPAREN_").lower_bound = -parameters['o2_lowerBound']

        model.reactions.get_by_id("EX_ac_LPAREN_e_RPAREN_").lower_bound = -parameters['ex_ac_lowerBound']
        model.reactions.get_by_id("EX_ac_LPAREN_e_RPAREN_").upper_bound = 0

        model.reactions.get_by_id("EX_starch_LPAREN_h_RPAREN_").lower_bound = 0
        model.reactions.get_by_id("EX_starch_LPAREN_h_RPAREN_").upper_bound = 0
        model.reactions.get_by_id("STARCH300DEGRA").upper_bound = starchDegAerLight/2
        model.reactions.get_by_id("STARCH300DEGR2A").upper_bound = 0
        model.reactions.get_by_id("STARCH300DEGRB").upper_bound = starchDegAerLight/2
        model.reactions.get_by_id("STARCH300DEGR2B").upper_bound = 0

        model.reactions.get_by_id("PCHLDR").lower_bound = 0
        model.reactions.get_by_id("PCHLDR").upper_bound = 0
        model.reactions.get_by_id("PFKh").lower_bound = 0
        model.reactions.get_by_id("PFKh").upper_bound = 0
        model.reactions.get_by_id("G6PADHh").lower_bound = 0
        model.reactions.get_by_id("G6PADHh").upper_bound = 0
        model.reactions.get_by_id("G6PBDHh").lower_bound = 0
        model.reactions.get_by_id("G6PBDHh").upper_bound = 0
        model.reactions.get_by_id("FBAh").lower_bound = 0
        model.reactions.get_by_id("FBAh").upper_bound = 0
        model.reactions.get_by_id("H2Oth").upper_bound = 0
        #model.reactions.get_by_id("Biomass_Chlamy_mixo").lower_bound = 0
        #model.reactions.get_by_id("Biomass_Chlamy_mixo").upper_bound = 0
        #model.reactions.get_by_id("Biomass_Chlamy_hetero").lower_bound = 0
        #model.reactions.get_by_id("Biomass_Chlamy_hetero").upper_bound = 0

        LNA_sol = cobra.flux_analysis.parsimonious.optimize_minimal_flux(model)
        # print("pFBA status: ", LNA_sol.status)
        # print("pFBA solution: ", LNA_sol.objective_value)
        # print(type(LNA_sol.fluxes))
        # print(LNA_sol.fluxes)

        status =  LNA_sol.status
        solution = LNA_sol.objective_value
        fluxes = LNA_sol.fluxes
        
        try:
            file_txt = BytesIO()
            file_csv = StringIO()
            with file_txt, file_csv:
                file_txt.seek(0)    #locate to the head of the file
                file_csv.seek(0)

                # initialise txt
                file_txt.write(bytes("Input File:"+parameters['file_name']+'\n', "utf-8"))
                file_txt.write(bytes("------------------------------------------\n", "utf-8"))
                file_txt.write(bytes("Status: "+str(status)+"\n", "utf-8"))
                file_txt.write(bytes("------------------------------------------\n", "utf-8"))
                file_txt.write(bytes("Solution: "+str(solution)+"\n", "utf-8"))
                file_txt.write(bytes("------------------------------------------\n", "utf-8"))
                # end

                # initialise csv
                flux_index = []
                flux_value = []
                flux_index.append('Input_File')
                flux_index.append('Status')
                flux_index.append('Solution')
                flux_index.append('')
                flux_index.append('Reaction')
                flux_value.append(parameters['file_name'])
                flux_value.append(status)
                flux_value.append(solution)
                flux_value.append('')
                flux_value.append('Flux_Value')
                # end

                for index in fluxes.index:
                    # txt content
                    line = str(index) + ':' + str(fluxes[index]) + '\n'
                    line = bytes(line, "utf-8")
                    file_txt.write(line)
                    # end

                    # csv content
                    flux_index.append(index)
                    flux_value.append(fluxes[index])
                    # end
        
                file_txt.seek(0)
                txt_file_hash_id = parameters['txt_file_hash_id']
                file_txt = File(file_txt)

                data = pd.DataFrame({'index': flux_index, 'value': flux_value})
                data.to_csv(file_csv, index=False, header=False)   # save csv file to buffer
                file_csv.seek(0)
                file_csv = File(file_csv)
                csv_file_hash_id = parameters['csv_file_hash_id']
                # save objects (if exist, will not update the database)
                parameters['upload_file_obj'].save()
                parameters['input_obj'].save()
                # save txt into database
                parameters['txt_file_obj'].download_file.save(txt_file_hash_id+"."+"txt", file_txt)
                parameters['txt_file_obj'].save()
                # save csv into database
                parameters['csv_file_obj'].download_file.save(csv_file_hash_id+"."+"csv", file_csv)
                parameters['csv_file_obj'].save()
        except Exception as exp:
            return False

        return True
    except Exception as e:
        print(e)
        return False



def GetImg_top_10(file_id):
    # process scripts
    img_obj = models.CycleImg.objects.filter(file_id=file_id)
    if img_obj.exists() and len(img_obj) == 10: # won't plot if 10 imgs were ploted before
        return False
    file_obj = models.DecompositionFile.objects.get(file_id=file_id)
    file = File(file_obj.file.file)
    with file.open() as file, mmap.mmap(file.fileno(),0,access=mmap.ACCESS_READ) as m:
        elements = []
        values = []
        ele_append = elements.append
        val_append = values.append
        count = 0
        while True:
            line = m.readline().strip()
            line = line.split(b'/')
            element = line[0].decode('utf-8').split()
            value = float(line[1])
            ele_append(element)
            val_append(value)
            count += 1
            if m.tell()==m.size() or count >=10:
                break
        # # sort file
        # a = list(zip(range(0,len(values)), values)) 
        # del values
        # dtype = [('eles_inx', np.int_),('vals', np.float_)]
        # arr = np.array(a, dtype=dtype)
        # arr = np.sort(arr, order='vals')
        # arr = arr[-10:] # top ten
        # arr = arr[::-1] # reverse array
        # for i in arr:
        #     element = elements[i['eles_inx']]
        #     value = i['vals']
        #     lines.append({'cycle':element, 'value':value})
        # del elements, arr
        # # end sort file
        
    for line_inx in range(0, count):
        img_id=file_id+'_'+str(line_inx)
        if models.CycleImg.objects.filter(img_id=img_id).exists():  # if this data is not in the database
            del elements[line_inx]
            del values[line_inx]
    inputs = zip(elements, values)
    print(inputs)
    pool = Pool()
    res = pool.map(plot,inputs)
    print(res)
    for i in range(0,len(res)):
        instance = res[i]['buffer']
        img = ImageFile(instance)
        obj = models.CycleImg(img_id=file_id+'_'+str(i), value=res[i]['val'], file_id=file_id)
        obj.img.save(file_id+'_'+str(i)+'.png', img)
        obj.save()
        instance.close()
    pool.close()
    return True

def plot(args):
    plt.switch_backend('agg')
    elements, value = args
    ele = elements.copy()
    ele.insert(0, ele.pop(-1))
    edges = list(zip(ele, elements))
    nodes_num = len(edges)
    fig = plt.figure()
    G = nx.DiGraph()
    G.add_edges_from(edges)
    nx.draw_circular(G, font_color='red', with_labels=False, node_color='white', edge_color="#969696", arrows=True, node_size=350)
    labels_R = {}
    labels_M = {}
    for i in G.nodes():
        if re.match("R_", i):
            labels_R[i] = i
        else:
            labels_M[i] = i
    nx.draw_networkx_labels(G, nx.circular_layout(G), labels_R, font_size=8, font_color='red')
    nx.draw_networkx_labels(G, nx.circular_layout(G), labels_M, font_size=8, font_color='#45962e')
    plt.axis('off')
    plt.text(0, 0, str(value), horizontalalignment='center', verticalalignment='center', bbox=dict(facecolor='red', alpha=0.5), size=12)
    buffer = BytesIO()
    if nodes_num > 18:
        length = (nodes_num - 18) * 0.2 + 6.4
        width = (nodes_num - 18) * 0.15 + 4.8
        fig.set_size_inches(length,width,forward=True)
    fig.savefig(buffer, dpi=200, format="png")

    plt.close()
    res = {}
    res['buffer'] = buffer
    res['val'] = value
    return res
    
def SearchImg(name, obj, upper=float('nan'), lower=float('nan')):
    decomp_file = File(obj.file.file)
    with decomp_file.open() as file,\
        mmap.mmap(file.fileno(),0,access=mmap.ACCESS_READ) as m:
        elements = []
        values = []
        # locate cycles when upper bound and lower bound are not NaN
        if not math.isnan(upper) and not math.isnan(lower):
            while True:
                line = m.readline().strip()
                cycle = line.split(b'/')[0]
                value = float(line.split(b'/')[-1])
                if upper >= value and lower <= value:
                    if cycle.find(bytes(name, encoding='utf8')) >= 0:
                        elements.append(cycle.decode("utf-8").split())
                        values.append(value)
                if m.tell()==m.size():
                    break
        #   end        
        # locate cycles when upper bound and lower bound are NaN
        elif math.isnan(upper) and math.isnan(lower):
            while True:
                line = m.readline().strip()
                cycle = line.split(b'/')[0]
                value = float(line.split(b'/')[-1])
                if cycle.find(bytes(name, encoding='utf8')) >= 0:
                    elements.append(cycle.decode("utf-8").split())
                    values.append(value)
                if m.tell()==m.size():
                    break
        # end
        else:
            if math.isnan(upper) == True:
                while True:
                    line = m.readline().strip()
                    cycle = line.split(b'/')[0]
                    value = float(line.split(b'/')[-1])
                    if value >= lower:
                        if cycle.find(bytes(name, encoding='utf8')) >= 0:
                            elements.append(cycle.decode("utf-8").split(" "))
                            values.append(value)
                    if m.tell()==m.size():
                        break
            else:
                while True:
                    line = m.readline().strip()
                    cycle = line.split(b'/')[0]
                    value = float(line.split(b'/')[-1])
                    if value <= upper:
                        if cycle.find(bytes(name, encoding='utf8')) >= 0:
                            elements.append(cycle.decode("utf-8").split(" "))
                            values.append(value)
                    if m.tell()==m.size():
                        break
    if len(elements) == 0 and len(values) == 0:
        return False
    else:
        return zip(elements, values)
    # buffer = BytesIO()
    # plt.savefig(buffer, dpi=300)
    # plot_data.append({'value':value, 'plot': buffer.getvalue()})
    # plt.close()
    
def GetScriptsInput(txt_obj, compartment="u"):
    with open("./static_files/reference.csv", "rb") as ref_file: # open reference file with "rb" in iobuffer
        reference_df = pd.read_csv(ref_file)    # transform reference file into datafram
        txt_file = txt_obj.download_file
        count_line = 1  # reaction data starts with 7th line
        data = {'reaction':[], 'value':[]}
        with txt_file.open() as file, mmap.mmap(file.fileno(),0,access=mmap.ACCESS_READ) as m:
            while True:
                line = m.readline().strip()
                if count_line < 7:
                    count_line += 1
                    continue
                res = line.split(b':')
                data['reaction'].append("R_"+str(res[0].decode('utf-8')))
                data['value'].append(str(res[1].decode('utf-8')))
                if m.tell() == m.size():
                    break
        current_data = pd.DataFrame({'reaction':data['reaction'], 'value':data['value']})
        merge_file = pd.merge(reference_df, current_data, on="reaction")
        formulas = []
        for row in merge_file.itertuples(index=True):
            reaction = row[1]
            species = row[2]
            current_compartment = row[4]
            mass = row[5]   #type == float
            role = row[6]   
            stoich = row[7] # type == float
            value = row[8]  # type == string
            mass_flux = float(mass) * float(value)
            if current_compartment == compartment and abs(mass_flux) > 1e-6:
                # if re.search("product", role):
                #     a.append(reaction)
                #     b.append(str(stoich)+" "+species)
                #     c.append(mass_flux)
                # else:
                #     a.append(str(stoich)+" "+species)
                #     b.append(reaction)
                #     c.append(mass_flux)
                if re.search("product", role):
                    formula = "%s%s %s %s %s%s%s%s"%('"',reaction,"->",str(stoich),species,'";',str(mass_flux),';')
                    formulas.append(formula)
                else:
                    formula = "%s%s %s %s %s%s%s%s"%('"',str(stoich),species,"->",reaction,'";',str(mass_flux),';')
                    formulas.append(formula)
        df = pd.DataFrame({"index":formulas})
        # df = pd.DataFrame({'a':a,'b':b,'c':c})
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)
    return buffer
    # df.to_csv("/Users/aarongao/Desktop/Decomposition_scripts/compartments/h/lna/chlamydomonas_lna.csv",index=False,header=False)

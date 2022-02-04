import glob
import pickle
import time
import concurrent.futures

print("Import complete")


def OpenPickle(f):
    with open(f, 'rb') as Create:
        Detail = pickle.load(Create)
        return Detail



def LoadTMSDevices(directory):
    valmaster = []
    for f in glob.glob(directory):
        T = OpenPickle(f)
        for t in T:
            if t not in valmaster:
                valmaster.append(t)
    with open('TMS_Combined\TMS_Master','wb') as f:
        pickle.dump(valmaster,f)
    return valmaster


def AddTMSDevicesToFeederMaster(master,feedermaster):
    BadList = [0,'0',"","Null"]
    DevList = feedermaster
    for item in feedermaster:
        for node in master:
            if item[0] == node[0]:
                pass
            elif item[2] in BadList:
                pass
            elif item[2] == node[3] or item[2] == node[2]:
                if node not in DevList:
                    DevList.append(node)
        for node in master:
            if item[0] == node[0]:
                pass
            elif item[3] in BadList:
                pass
            elif item[3] == node[2] or item[3] == node[3]:
                if node not in DevList:
                    DevList.append(node)
    return DevList



def Nodify(master):
    BadList = [0,'0',"","Null"]
    DevList = []
    for item in master:
        FNNL = []
        for node in master:
            if item[0] == node[0]:
                pass
            elif item[2] in BadList:
                pass
            elif item[2] == node[3] or item[2] == node[2]:
                FNNL.append(node[0])
            if FNNL == []:
                FNNL.append('end')
        item.append(FNNL)
        SNNL = []
        for node in master:
            if item[0] == node[0]:
                pass
            elif item[3] in BadList:
                pass
            elif item[3] == node[2] or item[3] == node[3]:
                SNNL.append(node[0])
            if SNNL == []:
                SNNL.append('end')
        item.append(SNNL)
        DevList.append(item)
    return DevList


def DiagnoseConnectivity(FeederWithTMS):
    Detail = []
    BREAKER = [v for v in FeederWithTMS if v[1] == 16]
    if len(BREAKER) < 1:
        print("Error: No BREAKER Found")
    elif len(BREAKER) > 1:
        print("Error:",len(BREAKER),"BREAKERS Found")
    else:
        B = BREAKER[0][0]
    print("Starting Connectivity for BREAKER:",B)
    x = 1
    T = [item[0] for item in FeederWithTMS if item[1] in [59,60,12]]
    print("Total Electricity Delivery Points:",len(T))
    Success = []
    Failure = []
    #Recursive function that traces connectivity for each Electricity Point of Delivery
    for t in T:
        #print(x,"Out of",len(T),"Electricity Delivery Points Processed")
        NL = [t]
        for a in NL:
            for b in FeederWithTMS:
                if a == b[0]:
                    CN = b[4]+b[5]
                    if B not in NL:
                        NL += [item for item in CN if item not in NL]

        #If the G3E_FID of the Breaker ends up in the Connectivity list, we consider it a success. Otherwise, the connectivity check failed.
        if str(B) in NL:
            Success.append(t)
            #print("Success")
            Detail.append([B,t,"Success",NL[-1]])
        else:
            Failure.append(t)
            Detail.append([B,t,"Failure",NL[-1]])
            #print("Failure",t)
            #print(NL)
        x += 1
    ConnectPercent = len(Success)/len(Failure+Success)
    print(ConnectPercent)
    return ConnectPercent, Detail

def DiagnoseConnectivityDist(file,valmaster):
    Detail = []
    ConnectPercent = 0
    NL = list(set([item[2] for item in valmaster if item[2] != '0'] + [item[3] for item in valmaster if item[3] != '0']))
    feedermaster = OpenPickle(file)
    TMS_Connect = [item for item in feedermaster if item[2] in NL or item[3] in NL]
    BREAKER = [item for item in TMS_Connect if item[1] == 16]
    if len(BREAKER) < 1:
        print("Error: No BREAKER Found")
        return ConnectPercent, Detail
    elif len(BREAKER) > 1:
        print("Error:",len(BREAKER),"BREAKERS Found")
        return ConnectPercent, Detail
    else:
        B = BREAKER[0][0]
    ProxyDevice = [item for item in TMS_Connect if item[1] != 16]
    if len(ProxyDevice) < 1:
        print("Error: No ProxyDevice Found")
        return ConnectPercent, Detail
    elif len(ProxyDevice) > 1:
        print("Error:",len(ProxyDevice),"ProxyDevices Found")
        return ConnectPercent, Detail
    else:
        P = ProxyDevice[0][0]
    FeederWithNodes = Nodify(feedermaster)
    #print("Starting Connectivity for ProxyDevice:",P)
    x = 1
    T = [item[0] for item in FeederWithNodes if item[1] in [59,60,12]]
    #print("Total Electricity Delivery Points:",len(T))
    Success = []
    Failure = []
    #Recursive function that traces connectivity for each Electricity Point of Delivery
    for t in T:
        #print(x,"Out of",len(T),"Electricity Delivery Points Processed")
        NL = [t]
        for a in NL:
            for b in FeederWithNodes:
                if a == b[0]:
                    CN = b[4]+b[5]
                    if P not in NL:
                        NL += [item for item in CN if item not in NL]

        #If the G3E_FID of the Breaker ends up in the Connectivity list, we consider it a success. Otherwise, the connectivity check failed.
        if str(P) in NL:
            Success.append(t)
            #print("Success")
            Detail.append([P,t,"Success",NL[-1]])
        else:
            Failure.append(t)
            Detail.append([P,t,"Failure",NL[-1]])
            #print("Failure",t)
            #print(NL)
        x += 1
    ConnectPercent = len(Success)/len(Failure+Success)
    #print(file,"Total Electricity Delivery Points:",len(T),ConnectPercent)
    #print(ConnectPercent)
    return ConnectPercent, Detail

def GetTMSConnected(FeederWithTMS):
    pass
    

print("Functions Loaded")


def Run(R):

    filelist = [f for f in glob.glob('Feeders\*')[0:R]] 
    x = 1
    for f in filelist:
        print("Processing",f,",",x,"out of",len(filelist),"Total Feeders")
        try:
            valmaster = OpenPickle('TMS_Combined\TMS_Master')
            feedermaster = OpenPickle(f)
            #feedermaster = [d for d in feedermaster_x if d[1] == 16]
            FeederWithTMS = AddTMSDevicesToFeederMaster(valmaster,feedermaster)
            FeederWithNodes = Nodify(FeederWithTMS)
            fname = str("Feeders_Processed\\"+f.split("\\")[-1])
            with open(fname,'wb') as loader:
                pickle.dump(FeederWithNodes,loader)
        except:
            print("Error with",f)
            pass
        x += 1

    FullDetail = []
    FullSummary = []
    start = time.time()
    filelist = [f for f in glob.glob('Feeders_Processed\*')[0:R]]
    x = 1
    for f in filelist:
        print("Processing",f,",",x,"out of",len(filelist),"Total Feeders")
        try:
            FeederWithNodes = OpenPickle(f)
            ConnectPercent, Detail = DiagnoseConnectivity(FeederWithNodes)
            FullDetail += Detail
            FullSummary.append([f,ConnectPercent])
            fname = str("Results\Detail_Results"+str(start))
            #with open(fname,'wb') as loader:
                #pickle.dump(FullDetail,loader)
            #fname = str("Results\Summary_Results"+str(start))
            #with open(fname,'wb') as loader:
                #pickle.dump(FullSummary,loader)
        except:
            print("Error with",f)
            pass
        x += 1

    #for file in glob.glob("Results\*"):
        #print(file)
        #l = OpenPickle(file)
        #for line in l:
            #print(line)

def RunDistOnlyX(R):
    valmaster = OpenPickle('TMS_Combined\TMS_Master')
    filelist = [f for f in glob.glob('Feeders\*')[0:R]]
    FullDetail = []
    FullSummary = []
    start = time.time()
    x = 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=w) as executor:
        future_to_url = {executor.submit(DiagnoseConnectivityDist, f, valmaster, 60): url for url in URLS}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
    for f in filelist:
        processstart = time.time()
        print("Processing",f,",",x,"out of",len(filelist),"Total Feeders")
        try:
            ConnectPercent, Detail = DiagnoseConnectivityDist(f,valmaster)
            FullDetail += Detail
            FullSummary.append([f,ConnectPercent])
            fname = str("Results\Detail_Results"+str(start))
            with open(fname,'wb') as loader:
                pickle.dump(FullDetail,loader)
            fname = str("Results\Summary_Results"+str(start))
            with open(fname,'wb') as loader:
                pickle.dump(FullSummary,loader)
        except:
            print("Error with",f)
            pass
        x += 1
        processend = time.time()
        print(processend - processstart, "Seconds to Process Feeder")
        try:
            print((processend - processstart)/len(Detail),"Seconds Per Electricity Point of Delivery")
        except:
            pass


def RunDistOnly(R):
    valmaster = OpenPickle('TMS_Combined\TMS_Master')
    filelist = [f for f in glob.glob('Feeders\*')[R:1010]]
    FullDetail = []
    FullSummary = []
    start = time.time()
    x = 1
    w = 5
    with concurrent.futures.ThreadPoolExecutor(max_workers=w) as executor:
        future_to_url = {executor.submit(DiagnoseConnectivityDist, f, valmaster): f for f in filelist}
        for future in concurrent.futures.as_completed(future_to_url):
            f = future_to_url[future]
            #print("Processing",f,",",x,"out of",len(filelist),"Total Feeders")
            try:
                ConnectPercent, Detail = future.result()
                FullDetail += Detail
                FullSummary.append([f,ConnectPercent])
                print("Processed",f,",",x,"out of",len(filelist),"Total Feeders,",ConnectPercent)
                fname = str("Results\Detail_Results"+str(start))
                with open(fname,'wb') as loader:
                    pickle.dump(FullDetail,loader)
                fname = str("Results\Summary_Results"+str(start))
                with open(fname,'wb') as loader:
                    pickle.dump(FullSummary,loader)
            except:
                pass
            x += 1
    end = time.time()
    print(end - start)


#X = len(glob.glob('Feeders\*'))
#X = 0
#RunDistOnly(X)
for file in glob.glob("Results\*"):
    print(file)
    #l = OpenPickle(file)
    #for line in l[0:10]:
        #print(line)

file = 'Results\Summary_Results1640899419.9990802'
l = OpenPickle(file)
print(len(l))
perfectfeeders = [line for line in l if line[1] == 1.0]
feederswitherrors = [line for line in l if line[1] != 0 and line not in perfectfeeders]
print(len(perfectfeeders))
print(len(feederswitherrors))

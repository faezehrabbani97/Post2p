import numpy as np
import pandas as pd
from PyQt5 import QtWidgets
from GUI import Ui_MainWindow
import plotly.express as px
import copy
import matplotlib.pyplot as plt
import os.path
import easygui
import random
import itertools
from scipy.stats.stats import pearsonr
from scipy import signal
from scipy.ndimage import gaussian_filter1d
from sklearn.decomposition import PCA
import running
import glob
import functions
import bottleneck as bn
import xml_parser
import json
import datetime
# Loading data
current_date = datetime.date.today()
current_time = datetime.datetime.now().time()
# Loading data
Base_path = easygui.diropenbox(title='select folder contaning data')
print("Base path = ", Base_path)
file_name1 = "Results_2.3_Sliding_check"
save_direction1 = os.path.join(Base_path, file_name1)
isExist1 = os.path.exists(save_direction1)

if isExist1:
    pass
else:
    os.mkdir(save_direction1)

save_direction_figure = os.path.join(save_direction1, "Figures")
isExist1 = os.path.exists(save_direction_figure)
if isExist1:
    pass
else:
    os.mkdir(save_direction_figure)

save_data = os.path.join(save_direction1, "data")
isExist1 = os.path.exists(save_data)
if isExist1:
    pass
else:
    os.mkdir(save_data)

file_name2 = "permutation_test"
save_direction202 = os.path.join(save_direction1, file_name2)
isExist1 = os.path.exists(save_direction202)
if isExist1:
    pass
else:
    os.mkdir(save_direction202)

file_name030 = "lag"
save_direction030 = os.path.join(save_direction1, file_name030)
isExist1 = os.path.exists(save_direction030)
if isExist1:
    pass
else:
    os.mkdir(save_direction030)

code = str(12)
Base_path2 = os.path.join(Base_path + "\suite2p" + "\plane0")
# speed
movement_file = glob.glob(Base_path + '/*.abf')

# suite2p
cell = np.load((os.path.join(Base_path2, "iscell.npy")), allow_pickle=True)
F = np.load((os.path.join(Base_path2, "F.npy")), allow_pickle=True)
Fneu_raw = np.load((os.path.join(Base_path2, "Fneu.npy")), allow_pickle=True)
# facemap
facemap = easygui.fileopenbox(title='Select facemap results for this session')
facemap = np.load(facemap, allow_pickle=True)
pupil = facemap.item()['pupil']  # stupid code #check it
pupil = pupil[0]
pupil = pupil['area']

motion = facemap.item()['motion']
motion = motion[1]

np.nan_to_num(pupil, copy=False)
np.nan_to_num(motion, copy=False)

xml = easygui.fileopenbox(title='Select xml file for this session')
xml = xml_parser.bruker_xml_parser(xml)
channel_number = xml['Nchannels']
laserWavelength = xml['settings']['laserWavelength']
objectiveLens = xml['settings']['objectiveLens']
objectiveLensMag = xml['settings']['objectiveLensMag']
opticalZoom = xml['settings']['opticalZoom']
bitDepth = xml['settings']['bitDepth']
dwellTime = xml['settings']['dwellTime']
framePeriod = xml['settings']['framePeriod']
micronsPerPixel = xml['settings']['micronsPerPixel']
TwophotonLaserPower = xml['settings']['twophotonLaserPower']
# In[5]:
F = F.tolist()
Fneu_raw = Fneu_raw.tolist()
# In[6]:
# detect Neurons between ROIs
Fneu_raw, keeped_ROI = functions.detect_cell(cell, Fneu_raw)
F, _ = functions.detect_cell(cell, F)
functions.save_data("ROI_order.npy",save_data,keeped_ROI)
# In[7]:
movement = running.single_getspeed(movement_file[0], np.size(F, 1))
speed = np.copy(movement['speed'])
n = (len(F) - 1)

# # interpolating data
##############################################
fp = pupil
fp1 = motion
x_inter = xml['Green']['relativeTime']
last = x_inter[-1]
step = last/len(pupil)
#xp = np.arange(x_inter[0],last,step, dtype= float)
xp = np.linspace(x_inter[0], last, len(pupil))
x_inter = xml['Green']['relativeTime']
pupil = np.interp(x_inter, xp, fp)
motion = np.interp(x_inter, xp, fp1 )
print("data for facemap were interpolated")
###############################################################

fig01 = plt.figure(figsize=(7, 2))
TIM = np.arange(0,len(motion))
plt.plot(TIM,motion)
functions.save_fig("raw_face_motion.png", save_direction_figure,fig01)
#########################################
fig02 = plt.figure(figsize=(7, 2))
TIM = np.arange(0,len(pupil))
plt.plot(TIM,pupil)
functions.save_fig("pupil.png", save_direction_figure,fig02)
##########################################################
functions.save_data("raw_motion.npy",save_data,motion)
functions.save_data("raw_pupil.npy",save_data,pupil)
#########################################################
Mean_F = np.mean(F, 0)
functions.save_data("raw_mean_F.npy",save_data,Mean_F)
fig001 = plt.figure(figsize=(7, 2))
TIM = np.arange(0,len(Mean_F))
plt.plot(TIM,Mean_F)
functions.save_fig("raw_mean_F.png", save_direction_figure,fig001)
###########################################################
class MyWindow(QtWidgets.QMainWindow):
    def __init__(self, image_file, data_file):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self,save_direction_figure, save_data)
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    data_path = save_data
    figure_path = save_direction_figure
    window = MyWindow(save_direction_figure, save_data)
    window.show()
    app.exec_()
DO_MOTION = window.ui.FaceAnalyze
Do_pupil = window.ui.PupilAnalyze
print("DO pupil", Do_pupil)
print("DO_MOTION", DO_MOTION)
neuropil_impact_factor = window.ui.neuropil
F0_method = window.ui.F0
remove_blink = window.ui.remove_blink
if remove_blink == 1:
    blink = "blinking frames were removed"
else:
    blink = "No blinking frame were removed"
ST_FA = window.ui.first_frame
END_FA = window.ui.last_frame
first_F_frame =  window.ui.first_dF
last_F_frame = window.ui.last_dF

if  ST_FA >= first_F_frame:
    st_FA = ST_FA
else:
    st_FA = first_F_frame
if END_FA <= last_F_frame:
    end_FA = END_FA
else:
    end_FA = last_F_frame
###########################################################
fs = 30
F = F - (neuropil_impact_factor * Fneu_raw)
# calculating F0
percentile = 10
F0 = functions.calculate_F0(F, fs, percentile, mode = F0_method, win=60)
# Calculating dF
dF = functions.deltaF_calculate(F, F0)
print(len(dF))
############################################################
# n_cells_raw = len(dF)
# cells_removed = []
# for i, v in enumerate(F0):
#     if v <= 1.5 * Fneu_raw[i]:
#         cells_removed.append(i)
# np.delete(F0, cells_removed, 0)
# np.delete(dF, cells_removed, 0)
# np.delete(F, cells_removed, 0)
# np.delete(Fneu_raw, cells_removed, 0)
# np.delete(cell, cells_removed, 0)
# print(len(dF))
# print('-- Removed %s cells out of %s due to low fluorescence' % (len(cells_removed), n_cells_raw))
##########################################################
r = np.arange(0, len(pupil))
if remove_blink == 0:
    ALL_ID = np.arange(0, len(pupil))
elif remove_blink == 1:
    blink_detectin = bn.move_var(pupil, window=4, min_count=1)
    MAx = np.max(blink_detectin)
    Min = np.min(blink_detectin)
    Range = (MAx - Min)/20

    blink_list = []
    for i in range(len(pupil)):
        if blink_detectin[i] > Range:
            blink_list.append(i)
            if (i-1) not in blink_list:
                blink_list.extend([(i-1),(i-2),(i-3),(i-4),(i-5),(i - 6), (i - 7), (i-8), (i - 9), (i - 10)])
            elif (i+1) not in blink_list:
                blink_list.extend([(i + 1), (i + 2), (i + 3), (i + 4), (i + 5),(i + 6), (i + 7), (i+8), (i + 9), (i + 10)])
    # print("These frames were removed for blinking",blink_list)
    blink_list = set(blink_list)
    blink_list = sorted(blink_list)
    ALL_ID = [x for x in r if x not in blink_list]
###################################################
#remove grooming
new_id = []
for i in (ALL_ID):
    if i >= st_FA and i < end_FA:
        new_id.append(i)
##################################################
print("len df befor groomng", len(dF[0]))
dff = []
for j in range(len(dF)):
    DF = []
    for k in new_id:
        DF.append(dF[j][k])
    dff.append(DF)
dF = np.array(dff)
print("len df after groomng", len(dF[0]))
#############################################################
new_motion = []
for k in (new_id):
    new_motion.append(motion[k])
motion = np.array(new_motion)
#############################################################
new_pupil = []
for k in (new_id):
    new_pupil.append(pupil[k])
pupil = np.array(new_pupil)
##############################################################
TIME = xml['Green']['relativeTime']
new_time=[]
for k in (new_id):
    new_time.append(TIME[k])
TIme = np.array(new_time)
functions.save_data("time.npy",save_data,TIme)
##############################################################
new_speed = []
for k in (new_id):
    new_speed.append(speed[k])
speed = np.array(new_speed)
##############################################################
f0 = []
for j in range(len(F0)):
    ff0 = []
    for k in new_id:
        ff0.append(F0[j][k])
    f0.append(ff0)
F0 = np.array(f0)
###############################################################
ffff = []
for j in range(len(F)):
    FFF = []
    for k in new_id:
        FFF.append(F[j][k])
    ffff.append(FFF)
F = np.array(ffff)

# # Normalize Motion Energy and Pupil from Facemap


# NORMALIZED df/f
#test
normal_df = functions.Normal_df(dF)
#test

# Save data
functions.save_data("Speed.npy",save_data,speed)
functions.save_data("motion_energy.npy",save_data,motion)
functions.save_data("pupil.npy",save_data,pupil)
functions.save_data("F.npy",save_data,F)
functions.save_data("F0.npy",save_data,F0)
functions.save_data("dF.npy",save_data,dF)

# sampling rate
Fs = 30
second = len(motion) // Fs
tstep = 1 / Fs
N = len(dF[0])
Step = second / len(dF[0])
###################
Time = np.arange(0, len(motion))
filtered_motion = gaussian_filter1d(motion, 15)
ids = np.arange(0, len(filtered_motion))
motion_threshold = 2*(np.std(motion))
#Extracting Indexes and intervals for WMI
id_above_thr_motion = np.extract(filtered_motion >= motion_threshold, ids)
motion_index, motion_window, Real_time_m_window = functions.find_intervals(id_above_thr_motion, 2, TIme) #to extract quiescence index use function with a small interval
motion_index2, motion_window2, Real_time_m_window2 = functions.find_intervals(id_above_thr_motion, 30, TIme) #to extract motion index use the function with bigger interval.
#motion_window2: it only select motion windows that at least is one Secon
quiescence_window, quiescence_index = functions.quiescence_interval(motion_window, ids)
motion_index2 = list(itertools.chain(*motion_index2))
quiescence_index= list(itertools.chain(*quiescence_index))


################
filtered_speed = gaussian_filter1d(speed, 15)
speed_threshold = 0.5
#Extracting Indexes and intervals for LMI
id_above_thr_speed = np.extract(filtered_speed >= speed_threshold, ids)
speed_index, speed_window, Real_Time_S_window = functions.find_intervals(id_above_thr_speed, 2, TIme) # to extract quiescence index use function with a small interval
speed_index2, speed_window2, Real_Time_S_window2 = functions.find_intervals(id_above_thr_speed, 60, TIme) # to extract running index use the function with bigger interval
quiescence_window_S, quiescence_index_S = functions.quiescence_interval(speed_window, ids)

#fCalculating LMI
speed_index2 = list(itertools.chain(*speed_index2))
quiescence_index_S= list(itertools.chain(*quiescence_index_S))
dF_NoMotion_S, dF_Motion_S = functions.dF_faceMotion(speed_index2, quiescence_index_S, dF)
S_mean_dF_NoMotion = np.mean(dF_NoMotion_S, 1)
S_mean_dF_Motion = np.mean(dF_Motion_S, 1)
LMI = []  # Locomotion Modulation Index
for i in range(len(dF)):
    LMI_i = (S_mean_dF_Motion[i] - S_mean_dF_NoMotion[i]) / (S_mean_dF_Motion[i] + S_mean_dF_NoMotion[i])
    LMI.append(LMI_i)

#Permutation
#DO_MOTION = 1
#######################################
# from scipy.signal import convolve
# #NEW
# tau=1.3 #characteristic decay time
# kernel_size=10 #size of the kernel in units of tau
# dt=np.mean(np.diff(time)) #spacing between successive timepoints
# n_points=int(kernel_size*tau/dt)
# kernel_times=np.linspace(-n_points*dt,n_points*dt,2*n_points+1) #linearly spaced array from -n_points*dt to n_points*dt with spacing dt
# kernel=np.exp(-kernel_times/tau) #define kernel as exponential decay
# kernel[kernel_times<0]=0 #set to zero for negative times
#
# fig,ax=plt.subplots()
# ax.plot(kernel_times,kernel)
# ax.set_xlabel('time (s)')
# plt.show()
# speed = convolve(speed,kernel,mode='same')*dt
# motion = convolve(motion,kernel,mode='same')*dt

########################################
print("Start of permutation test")
if Do_pupil == 1:
    valid_neurons_pupil, out_neurons_pupil = functions.permutation(dF, pupil,"pupil", save_direction202)
    functions.save_data("valid_neurons_pupil.npy", save_data, valid_neurons_pupil)
    fig = plt.figure(figsize=(7, 5))
    labels = ['valid neuron', 'unvalid neuron']
    sizes = [len(valid_neurons_pupil), len(out_neurons_pupil)]
    colors = ['aquamarine', 'plum']
    plt.pie(sizes, labels=[f'{label} ({size})' for label, size in zip(labels, sizes)], colors=colors,
            autopct='%1.1f%%')
    plt.title('permutation test result (pupil)')
    functions.save_fig("validation_Pupil.png", save_direction202, fig)
else:
    pass
valid_neurons_speed, out_neurons_speed = functions.permutation(dF, speed,"speed", save_direction202)
functions.save_data("valid_neurons_speed.npy",save_data,valid_neurons_speed)
if DO_MOTION == 1:
    valid_neurons_face, out_neurons_face = functions.permutation(dF, motion,"motion", save_direction202)
    functions.save_data("valid_neurons_face.npy", save_data, valid_neurons_face)
else:
    valid_neurons_face = []
    out_neurons_face = []
permutation_results = {
    'valid_neurons_speed': valid_neurons_speed,
    'out_neurons_speed': out_neurons_speed,
    'valid_neurons_facemotion': valid_neurons_face,
    'out_neurons_face' : out_neurons_face
}
file_name_1 = "permutation_results.json"
save_direction_1 = os.path.join(save_direction202, file_name_1)
isExist = os.path.exists(save_direction_1)
if isExist:
    pass
else:
    with open(save_direction_1, 'w') as file:
        json.dump(permutation_results, file)
##############################################
fig = plt.figure(figsize=(7, 5))
labels = ['valid neuron', 'unvalid neuron']
sizes = [len(valid_neurons_speed), len(out_neurons_speed)]
colors = ['aquamarine', 'plum']
plt.pie(sizes, labels=[f'{label} ({size})' for label, size in zip(labels, sizes)], colors=colors, autopct='%1.1f%%')
plt.title('permutation test result (speed)')
functions.save_fig("validation_speed.png", save_direction202,fig)
if DO_MOTION == 1:
    fig = plt.figure(figsize=(7, 5))
    labels = ['valid neuron', 'unvalid neuron']
    sizes = [len(valid_neurons_face), len(out_neurons_face)]
    colors = ['aquamarine', 'plum']
    plt.pie(sizes, labels=[f'{label} ({size})' for label, size in zip(labels, sizes)], colors=colors, autopct='%1.1f%%')
    plt.title('permutation test result (facemotion)')
    functions.save_fig("validation_facemotion.png", save_direction202,fig)
else:
    pass
print("End of Permutation Test")
if DO_MOTION == 1:
    if len(valid_neurons_face) == 0 :
        raise Exception("Zero Neuron is valid after permutation test for face motion and dF ")
else:
    pass
if len(valid_neurons_speed) == 0 :
    raise Exception("Zero Neuron is valid after permutation test for speed and dF ")
ROI = random.choice(valid_neurons_speed)
ROI2 = random.choice(valid_neurons_speed)
ROi = str(ROI)
ROi2 = str(ROI2)

functions.HistoPlot(LMI,"All LMI",save_direction_figure)
functions.save_data("All_LMI.npy",save_data,LMI)
############################
S_mean_dF_NoMotion = np.mean(dF_NoMotion_S, 1)
S_mean_dF_Motion = np.mean(dF_Motion_S, 1)
#here
fig122 = plt.figure(figsize=(14, 7))
plt.title(label='dF Run & dF Rest(LMI)', y=1.05, fontsize=30)
NUM1 = np.arange(0, len(S_mean_dF_NoMotion))
colors = np.where(np.in1d(NUM1, out_neurons_speed), 'red', 'lightgreen')
plt.scatter(S_mean_dF_NoMotion, S_mean_dF_Motion, s=100, c = colors)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.ylabel('mean dF run', fontsize=19, labelpad=10)
plt.xlabel('mean dF rest ', fontsize=19, labelpad=10)
functions.save_fig("dF_RUN_REST_LMI.png", save_direction_figure, fig122)


#save
functions.save_data("All_mean_dF_rest_LMI.npy",save_data,S_mean_dF_NoMotion)
functions.save_data("All_mean_dF_run_LMI.npy",save_data,S_mean_dF_Motion)
# CALCUlatin Runing LMI

#############################
#double_check
Total_Time =  len(TIme) / fs
RUN_TIME = len(dF_Motion_S[0]) / fs
REST_TIME = len(dF_NoMotion_S[0]) / fs
Run_percentage = (RUN_TIME/Total_Time) * 100
#############################

filtered_speed = gaussian_filter1d(speed, 15)  # check standard deviation for Gaussian kernel
max_val = max(filtered_speed)
y = np.arange(0, max_val, 0.1)
fig25, ax = plt.subplots(figsize=(17, 6))
ax.plot(TIme, filtered_speed)
ax.margins(x=0.01)
threshold = 0.5
plt.ylabel('Speed(cm/s)', labelpad=10)
plt.xlabel('Time(S)', labelpad=10)
ax.set_facecolor("white")
ax.axhline(threshold, color='orange', lw=2)
for i in Real_Time_S_window2:
    handle = plt.fill_betweenx(y, i[0], i[-1], color='lightpink', alpha=.5, label='runing>2(S)')
functions.save_fig("filtered_speed.png", save_direction_figure, fig25)

# ## Total Movment WMI
if DO_MOTION ==1:

    # calculating general WMI
    dF_NoMotion, dF_Motion = functions.dF_faceMotion(motion_index2, quiescence_index, dF)
    mean_dF_NoMotion = np.mean(dF_NoMotion, 1)
    mean_dF_Motion = np.mean(dF_Motion, 1)
    A_WMI = []  # whisking Modulation Index
    for i in range(len(dF)):
        WMI_i = (mean_dF_Motion[i] - mean_dF_NoMotion[i]) / (mean_dF_Motion[i] + mean_dF_NoMotion[i])
        A_WMI.append(WMI_i)
    # extracting indexes and intervals for only whisking WMI(whisking when mouse is not running)
    quiescence_window2, quiescence_index2 = functions.quiescence_interval(speed_window2, ids)
    quiescence_index2 = list(itertools.chain(*quiescence_index2))
    only_whisking_index = []
    for i in motion_index2:
        if i in quiescence_index2:
            only_whisking_index.append(i)
    _, only_whisking_window, real_time_only_whisking_window = functions.find_intervals(only_whisking_index, 3, TIme)
    # calculate WMI for only whisking periods
    _, dF_only_whisking = functions.dF_faceMotion(only_whisking_index, quiescence_index, dF)
    # for no whisking dF we will use the same mean resting dF (mean_dF_NoMotion) as general WMI
    mean_dF_only_whisking = np.mean(dF_only_whisking, 1)
    only_whisking_WMI = []  # whisking Modulation Index
    for i in range(len(dF)):
        WMI_i = (mean_dF_only_whisking[i] - mean_dF_NoMotion[i]) / (mean_dF_only_whisking[i] + mean_dF_NoMotion[i])
        only_whisking_WMI.append(WMI_i)

    functions.save_data("WMI.npy",save_data,A_WMI)
    ################################
    #AD
    Total_Time = len(TIme) / fs
    Whisking_TIME = len(dF_Motion[0]) / fs
    Whisking_percentage = (Whisking_TIME / Total_Time)*100
    ####################################
    fig123 = plt.figure(figsize=(14, 7))
    plt.title(label='dF Whisking & dF No Whisking(WMI)', y=1.05, fontsize=30)
    NUM1 = np.arange(0, len(mean_dF_NoMotion))
    colors = np.where(np.in1d(NUM1, out_neurons_face), 'red', 'lightgreen')
    plt.scatter(mean_dF_NoMotion, mean_dF_Motion, s=100, c = colors)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('dF/F Whisking', fontsize=19, labelpad=10)
    plt.xlabel('dF/F NO Whisking ', fontsize=19, labelpad=10)
    functions.save_fig("dF_Whisking_No_Whisking(WMI).png", save_direction_figure, fig123)
    ####################################
    functions.save_data("All_cell_mean_dF_NoMotion_Total_WMI.npy", save_data, mean_dF_NoMotion)
    functions.save_data("All_cell_mean_dF_Motion_Total_WMI.npy", save_data, mean_dF_Motion)
    fig1010 = plt.figure(figsize=(14, 7))
    num = np.arange(0, len(A_WMI))
    plt.title(label='WMI', y=1.05, fontsize=30)
    plt.scatter(num, A_WMI, s=100, color = 'paleturquoise')
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('WMI', fontsize=19, labelpad=10)
    plt.xlabel('Neuron ', fontsize=19, labelpad=10)
    functions.save_fig("WMI.png", save_direction_figure,fig1010)
    fig, ax = plt.subplots(figsize=(17, 4))
    ax.plot(TIme, motion)
    ax.margins(x=0)
    plt.ylabel('motion energy', labelpad=10)
    plt.xlabel('Time(S)', labelpad=10)
    ax.set_facecolor("white")
    ax.axhline(motion_threshold, color='orange', lw=2)
    ax.fill_between(TIme, 0, 1, where=motion > motion_threshold,
                    color='pink', alpha=0.5, transform=ax.get_xaxis_transform())
    functions.save_fig("Face_motion_for_absolut_WMI.png", save_direction_figure, fig)
    functions.HistoPlot(A_WMI,'absolut WMI', save_direction_figure)
    # motion energy

    fig8 = plt.figure(figsize=(16, 7))
    plt.title(label='face motion energy', y=1.05, fontsize=20)
    plt.plot(TIme, motion)
    filter_w = gaussian_filter1d(motion, 12)
    plt.plot(TIme, filter_w)
    plt.axhline(y=motion_threshold, label='median', linewidth=4, color="green", alpha=0.5)
    # plt.plot(time,const1,linewidth=4)

    '''plt.plot(time,const2)
    plt.plot(time,const3)'''
    # plt.ylabel('face motion energy', fontsize=15)

    MAx_Val = max(motion)
    Min_Val = min(motion)
    y = np.arange(Min_Val, (MAx_Val + 0.1), 0.1)

    for i in Real_time_m_window2:
        handle = plt.fill_betweenx(y, i[0], i[-1], color='lightpink', alpha=.5, label='runing>2(S) ± 1S')
    plt.legend(handles=[handle], loc=2, prop={'size': 14})

    plt.xlabel('Time(S)', fontsize=15, labelpad=8)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.margins(x=0.01)
    functions.save_fig("motion_energy3.png", save_direction_figure,fig8)

    functions.save_data("Rest_WMI.npy",save_data,only_whisking_WMI)

    functions.save_data("mean_dF_NOMotion_only_whiskingWMI.npy",save_data,mean_dF_NoMotion)
    functions.save_data("mean_dF_Motion_only_whiskingWMI.npy",save_data,mean_dF_only_whisking)

    functions.HistoPlot(only_whisking_WMI,'WMI Rest', save_direction_figure)
    # In[34]:motionkkjkjk
    # Ploting Pupil

    fig7 = plt.figure(figsize=(17, 3))
    plt.plot(TIme, pupil)
    plt.xlabel('Time(S)', fontsize=14, labelpad=8)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    # plt.ylim(0.6, 0.8)
    plt.margins(x=0)
    functions.save_fig("pupil.png", save_direction_figure,fig7)
else:
    pass
fs = 30
fig5 = plt.figure(figsize=(17, 8))
f, t, Sxx = signal.spectrogram(dF[ROI], fs)
plt.pcolormesh(t, f, Sxx, shading='gouraud')
plt.ylabel('Frequency [Hz]', fontsize=19)
plt.xlabel('Time [sec]', fontsize=19)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
functions.save_fig("Power_Spectrum.png", save_direction_figure, fig5)
#####################
fig6 = plt.figure(figsize=(16, 8))
plt.pcolormesh(dF)
plt.colorbar()
plt.ylabel('Neuron', fontsize=19, labelpad=8)
plt.xlabel('Time [frame]', fontsize=19, labelpad=8)
plt.yticks(fontsize=15)
plt.xticks(fontsize=15)
functions.save_fig("color-coded plot.png", save_direction_figure, fig6)
# Normalized color-coded plot
fig20 = plt.figure(figsize=(16, 8))
plt.pcolormesh(normal_df)
plt.colorbar()
plt.ylabel('Neuron', fontsize=19, labelpad=8)
plt.xlabel('Time [frame]', fontsize=19, labelpad=8)
plt.yticks(fontsize=15)
plt.xticks(fontsize=15)
functions.save_fig("normal_color-coded plot.png", save_direction_figure, fig20)
# sort normalized dF base on LMI
dF_speed_valid = []
for i in valid_neurons_speed:
    dF_speed_valid.append(normal_df[i])
dF_speed_valid = np.array(dF_speed_valid)
# Calcolating correlation between speed and df/f
speed_corr = []
for i in range(len(F)):
    correlation = pearsonr(speed, dF[i])
    speed_corr.append(correlation[0])
functions.save_data("speed_all_corr.npy", save_data, speed_corr)
dF_speed_correlation_sorted = [dF for speed_corr, dF in sorted(zip(speed_corr, dF))]
Normal_dF_speed_correlation_sorted = functions.Normal_df(dF_speed_correlation_sorted)
mean_dF0 = np.mean(F0, 1)
##########################
Valid_NotValid_speed = len(speed_corr) * ["NO"]
for i in valid_neurons_speed:
    Valid_NotValid_speed[i] = "yes"
speed_corr_histo_data = {
    "Correlation": speed_corr,
    "Speed validity": Valid_NotValid_speed
}
color_map = {"NO": "silver", "yes": "palevioletred"}
Speed_corr_histo_data = pd.DataFrame(speed_corr_histo_data)
fig = px.histogram(Speed_corr_histo_data, x="Correlation", color="Speed validity", marginal="violin", # can be `box`, `violin`
                         hover_data=Speed_corr_histo_data.columns, nbins=15,barmode='relative',  opacity = 0.5, color_discrete_map=color_map )
fig.update_layout(plot_bgcolor='white')
fig.update_traces(marker_line_color='white', marker_line_width=2)

save_direction_histo = os.path.join(save_direction_figure, "Speed_corr_validity.png")

###########################

# Calcolating correlation between face motion and df/f
if DO_MOTION == 1:

    face_corr = []
    for i in range(len(F)):
        Correlation = pearsonr(motion, dF[i])
        face_corr.append(Correlation[0])
    functions.save_data("face_corr.npy",save_data,face_corr)

    dF_face_correlation_sorted = [dF for face_corr, dF in sorted(zip(face_corr, dF))]
    Normal_dF_face_correlation_sorted = functions.Normal_df(dF_face_correlation_sorted)
    #####
    Valid_NotValid_face = len(face_corr) * ["NO"]
    for i in valid_neurons_face:
        Valid_NotValid_face[i] = "yes"
    face_corr_histo_data = {
        "Correlation": face_corr,
        "Face validity": Valid_NotValid_face
    }
    color_map = {"NO": "silver", "yes": "palevioletred"}
    Face_corr_histo_data = pd.DataFrame(face_corr_histo_data)
    fig = px.histogram(Face_corr_histo_data, x="Correlation", color="Face validity", marginal="violin",
                       # can be `box`, `violin`
                       hover_data=Face_corr_histo_data.columns, nbins=15, barmode='relative', opacity=0.5,
                       color_discrete_map=color_map)
    fig.update_layout(plot_bgcolor='white')
    fig.update_traces(marker_line_color='white', marker_line_width=2)
    fig.show()
    save_direction_histo = os.path.join(save_direction_figure, "Face_corr_validity.png")


    # In[43]:
    # Normal_color-coded plot sorted by LMI
    # sort nourmal Neuron base on LMI
    fig22 = plt.figure(figsize=(16, 8))
    plt.pcolormesh(Normal_dF_face_correlation_sorted)
    plt.colorbar()
    plt.ylabel('Neuron', fontsize=19, labelpad=8)
    plt.xlabel('Time [frame]', fontsize=19, labelpad=8)
    plt.yticks(fontsize=15)
    plt.xticks(fontsize=15)
    functions.save_fig("face_Sorted_normal_colorCoded plot.png", save_direction_figure, fig22)
    mean_dF0_speed_valid = []
    for i in valid_neurons_speed:
        mean_dF0_speed_valid.append(mean_dF0[i])
    mean_dF0_speed_valid = np.array(mean_dF0_speed_valid)
    # # Correlation
    # Calcolating correlation between pupil and df/f
    pupil_corr = []
    for i in range(len(F)):
        P_correlation = pearsonr(pupil, dF[i])
        pupil_corr.append(P_correlation[0])
    functions.save_data("pupil_all_corr.npy",save_data,pupil_corr)
    # Calcolating correlation between face motion and speed
    num = np.arange(0, len(speed_corr))
    fig404 = plt.figure(figsize=(14, 9))
    colors = np.where(np.in1d(num, out_neurons_face), 'red', 'lightgreen')
    sc = plt.scatter(num, mean_dF0 , s=100, c=colors)
    plt.xlabel('Neuron', fontsize=20, labelpad=10)
    plt.ylabel('mean df0', fontsize=20, labelpad=10)
    plt.title(label="df0", y=1.05, fontsize=19)
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label='fail face P Test', markerfacecolor='red', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='pass face P Test', markerfacecolor='lightgreen', markersize=10)]
    plt.legend(handles=legend_elements)
    functions.save_fig("df0_face.png", save_direction_figure, fig404)
else:
    pass
sorted_mean_dF0 = [mean_dF0 for LMI , mean_dF0 in sorted(zip(LMI, mean_dF0))]
num = np.arange(0, len(sorted_mean_dF0))
fig44 = plt.figure(figsize=(14, 9))
colors = np.where(np.in1d(num, out_neurons_speed), 'red', 'lightgreen')
sc = plt.scatter(num, sorted_mean_dF0, s=100, c=colors)
plt.xlabel('Neuron', fontsize=20, labelpad=10)
plt.ylabel('mean df0', fontsize=20, labelpad=10)
plt.title(label="df0 sorted by LMI", y=1.05, fontsize=19)
functions.save_fig("df0 sorted by LMI.png", save_direction_figure, fig44)
########################
num = np.arange(0, len(mean_dF0))
fig405 = plt.figure(figsize=(14, 9))
colors = np.where(np.in1d(num, out_neurons_speed), 'red', 'lightgreen')
sc = plt.scatter(num, mean_dF0, s=100, c=colors)
plt.xlabel('Neuron', fontsize=20, labelpad=10)
plt.ylabel('mean df0', fontsize=20, labelpad=10)
plt.title(label="df0", y=1.05, fontsize=19)
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', label='fail speed P Test', markerfacecolor='red', markersize=10),
    plt.Line2D([0], [0], marker='o', color='w', label='pass speed P Test', markerfacecolor='lightgreen',  markersize=10)]
plt.legend(handles=legend_elements)
functions.save_fig("df0_speed.png", save_direction_figure, fig405)
#check-check

Mean__dF = np.mean(dF, 0)

fig101,ax = plt.subplots(figsize=(10, 5))
ax2=ax.twinx()
ax2.plot(TIme,speed, color="green", alpha= 0.5)
ax.plot(TIme, Mean__dF, color="red", alpha= 0.5)
plt.title("mean dF vs speed")
functions.save_fig("mean_dF_VS_speed.png", save_direction_figure, fig101)
################################
Mean_dF = np.mean(dF, 1)
if DO_MOTION == 1:
    fig102,ax = plt.subplots(figsize=(10, 5))
    ax2=ax.twinx()
    ax2.plot( TIme,motion, color="green", alpha= 0.5)
    ax.plot(TIme, Mean__dF, color="red", alpha= 0.5)
    plt.title("mean dF vs face motion")
    functions.save_fig("mean_dF_VS_facemotion.png", save_direction_figure,fig102)

    # Comparing face_motion and speed correlation
    fig11 = plt.figure(figsize=(11, 6))
    plt.title(label='Speed & face motion', y=1.05, fontsize=18)
    plt.plot(np.unique(speed_corr), np.poly1d(np.polyfit(speed_corr, face_corr, 1))(np.unique(speed_corr)), linewidth=3,
             color='salmon')
    plt.scatter(speed_corr, face_corr, s=80, color='gray')
    plt.ylabel('face motion correlation', fontsize=15, labelpad=10)
    plt.xlabel('speed correlation', fontsize=15, labelpad=10)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    functions.save_fig("Face_motion&Speed_Correlation.png", save_direction_figure, fig11)

    # pupil*F Correlation plot
    NUM = np.arange(0, len(dF))
    fig112 = plt.figure(figsize=(14, 6))
    sc = plt.scatter(NUM, pupil_corr, s=100, color='gray')

    plt.xlabel('Neuron', fontsize=15, labelpad=10)
    plt.ylabel('correlation', fontsize=15, labelpad=10)
    plt.title(label='pupil & F Correlation', y=1.05, fontsize=18)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    functions.save_fig("pupil&F_Correlation.png", save_direction_figure, fig112)

    fig13 = plt.figure(figsize=(14, 6))
    colors = np.where(np.in1d(NUM, out_neurons_face), 'red', 'lightgreen')
    sc = plt.scatter(NUM, face_corr,s=120, c=colors)
    plt.xlabel('Neuron', fontsize=15, labelpad=10)
    plt.ylabel('correlation', fontsize=15, labelpad=10)
    plt.title(label='Face_motion & F Correlation', y=1.05, fontsize=18)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)

    functions.save_fig("Face_motion&F_Correlation.png", save_direction_figure, fig13)
    ######################
    faceValidCorr = []
    for i in valid_neurons_face:
        faceValidCorr.append(face_corr[i])
    faceValidCorr = np.array(faceValidCorr)
    functions.save_data("Valid_face&F_Correlation.npy", save_data, faceValidCorr)
else:
    pass
# In[54]:


# speed*F Correlation plot
NUM =  np.arange(0, len(dF))
fig12 = plt.figure(figsize=(14, 6))
colors = np.where(np.in1d(NUM, out_neurons_speed), 'red', 'lightgreen')
sc = plt.scatter(NUM, speed_corr, s=100, c=colors)
plt.xlabel('Neuron', fontsize=15, labelpad=10)
plt.ylabel('correlation', fontsize=15, labelpad=10)
plt.title(label='Speed & F Correlation', y=1.05, fontsize=18)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)

SpeedValidCorr = []
for i in valid_neurons_speed:
    SpeedValidCorr.append(speed_corr[i])
SpeedValidCorr = np.array(SpeedValidCorr)
functions.save_data("Valid_Speed&F_Correlation.npy", save_data, SpeedValidCorr)
functions.save_fig("speed&F_Correlation.png",save_direction_figure,fig12)
############################################
# # PCA
number = len(dF)
PCAcell = []
pca = PCA(n_components=number)
cell_PCA = pca.fit_transform(dF)
cell_pca1 = []
for i in range(len(cell_PCA)):
    cell_pca1.append(cell_PCA[i][0])

cell_pca2 = []
for i in range(len(cell_PCA)):
    cell_pca2.append(cell_PCA[i][1])

cell_pca3 = []
for i in range(len(cell_PCA)):
    cell_pca3.append(cell_PCA[i][2])
PCAcell.append(cell_pca1)
PCAcell.append(cell_pca2)
PCAcell.append(cell_pca3)
functions.save_data("PCAcell.npy", save_data, PCAcell)

w = pca.explained_variance_ratio_
fig34 = plt.figure(figsize=(14, 6))
num = np.arange(0, len(cell_PCA))
plt.hist(num, weights=w * 100, edgecolor="black", color="gray", bins=29)
functions.save_fig("PC_values.png",save_direction_figure,fig34)
# PCA TIME
PCAtime = []
rev_df = dF.T
pca = PCA(n_components=3)
time_PCA = pca.fit_transform(rev_df)

time_pca1 = []
for i in range(len(time_PCA)):
    time_pca1.append(time_PCA[i][0])

time_pca2 = []
for i in range(len(time_PCA)):
    time_pca2.append(time_PCA[i][1])

time_pca3 = []
for i in range(len(time_PCA)):
    time_pca3.append(time_PCA[i][2])
print(pca.explained_variance_ratio_)

PCAtime.append(time_pca1)
PCAtime.append(time_pca2)
PCAtime.append(time_pca3)
functions.save_data("PCAtime.npy", save_data, PCAtime)

plt.figure(figsize=(8, 8))
plt.scatter(time_pca1, time_pca2, s=2, color="olive")
plt.ylabel('PC2', size=20, labelpad=10)
plt.xlabel('PC1', size=20, labelpad=10)
plt.close()
# In[61]:


fig41 = plt.figure(figsize=(8, 8))

plt.scatter(cell_pca1, cell_pca2, s=80, color='gray', alpha=0.6)
plt.xlabel('PC1', size=20, labelpad=10)
plt.ylabel('PC2', size=20, labelpad=10)
functions.save_fig("PC1vs2.png",save_direction_figure,fig41)
# PCA TIME
fig50 = plt.figure(figsize=(16, 8))
gs = fig50.add_gridspec(20, 65)
filtered_time_PCA1 = gaussian_filter1d(time_pca1, 10)
filtered_time_PCA2 = gaussian_filter1d(time_pca2, 10)
filtered_time_PCA3 = gaussian_filter1d(time_pca3, 10)
filtered_speed2 = gaussian_filter1d(speed, 10)

ax = fig50.add_subplot(gs[:6, :])
ax.plot(TIme, filtered_speed2, label='speed', linewidth=2)
ax.plot(TIme, filtered_time_PCA1, label='PCA1', linewidth=2)
ax.legend(bbox_to_anchor=(0.08, 1), prop={'size': 8}, borderaxespad=0)
ax.margins(x=0.01)

ax1 = fig50.add_subplot(gs[7:13, :])
ax1.plot(TIme, filtered_speed2, label='speed', linewidth=2)
ax1.plot(TIme, filtered_time_PCA2, label='PCA2', linewidth=2, color='brown')
ax1.legend(bbox_to_anchor=(0.08, 1), prop={'size': 8}, borderaxespad=0)
ax1.margins(x=0.01)

ax2 = fig50.add_subplot(gs[14:20, :])
ax2.plot(TIme, filtered_speed2, label='speed', linewidth=2)
ax2.plot(TIme, filtered_time_PCA3, label='PCA3', linewidth=2, color='olive')
ax2.legend(bbox_to_anchor=(0.08, 1), prop={'size': 8}, borderaxespad=0)
ax2.margins(x=0.01)
# Remove spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
plt.xlabel('Time', fontsize=17, labelpad=10)
functions.save_fig("PC_time.png",save_direction_figure,fig50)
# # Runing Plots

# In[63]:


# Runing
max_val = max(speed)
y = np.arange(0, max_val, 0.1)
const = len(speed) * [0.5]
fig16 = plt.figure(figsize=(16, 7))
# plt.plot(time,s)
plt.plot(TIme, speed, )
plt.plot(TIme, const, linewidth=4)
plt.margins(x=0)
for i in Real_Time_S_window2:
    handle = plt.fill_betweenx(y, i[0], i[-1], color='lightpink', alpha=.5, label='runing>2(S)')
plt.legend(handles=[handle], loc=2, prop={'size': 14})
plt.ylabel('Speed(cm/s)', fontsize=20, labelpad=10)
plt.xlabel('Time(S)', fontsize=20, labelpad=10)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
functions.save_fig("speed.png",save_direction_figure,fig16)
# Calculating start and end of each movment period( wil be used in figures)

er = 1 / 10 * (max(motion))
# motion energy

fig8 = plt.figure(figsize=(16, 3))
plt.title(label='face motion energy', y=1.05, fontsize=20)
plt.plot(TIme, motion)

# plt.plot(time,const1,linewidth=4)
'''plt.plot(time,const2)
plt.plot(time,const3)'''
# plt.ylabel('face motion energy', fontsize=15)
ti = np.arange(0, len(F[0]))
fig17 = plt.figure(figsize=(19, 13))
for i in range(len(F)):
    plt.plot(ti, F[i], linewidth=0.5, label='dF/f')
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.xlabel('Time(S)', fontsize=20, labelpad=10)
functions.save_fig("all_traces.png", save_direction_figure, fig17)
leN = len(dF)
sp = np.copy(speed)
sp[sp == 0] = 'nan'
speed_mean = leN * [np.nanmean(sp)]
LMI_A_array = np.array(LMI)
LMI_mean_speed = np.stack((LMI_A_array, speed_mean), axis=1)
functions.save_data('All_LMI_mean_speed', save_data, LMI_mean_speed)
if DO_MOTION == 1:
    MAx_Val = max(motion)
    Min_Val = min(motion)
    y = np.arange(Min_Val, (MAx_Val + 0.1), 0.1)
    for i in Real_time_m_window2:
        handle = plt.fill_betweenx(y, i[0], i[-1], color='lightpink', alpha=.5, label='runing>2(S) ± 1S')
    plt.legend(handles=[handle], loc=2, prop={'size': 10})
    plt.xlabel('Time(S)', fontsize=15, labelpad=8)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.margins(x=0.01)
    functions.save_fig("motion_energy.png",save_direction_figure,fig8)
    # # All in one plot
    normal_motion = []
    p = max(abs(motion))
    for i in range(len(motion)):
        normal_motion.append(motion[i] / p)
    # Normalize puipl
    normal_pupil = []
    l = max(abs(pupil))
    for i in range(len(pupil)):
        normal_pupil.append(pupil[i] / l)
    ##############################
    ROi = str(ROI)
    # Some example data to display
    Step = second / len(speed)
    max_val = max(speed)
    max_face = max(normal_motion)
    y = np.arange(0, max_val, 0.1)
    y5_0 = np.arange(0, max_face, 0.1)
    x = TIme
    xx = np.arange(0, len(dF[ROI]))
    y1 = F[ROI]
    y1_1 = F0[ROI]
    y2 = dF[ROI]
    y3 = speed
    y4 = normal_motion
    y5 = normal_pupil
    ###################
    fig18 = plt.figure(figsize=(20, 26), dpi=150)
    gs = fig18.add_gridspec(5, hspace=1, wspace=0)
    (ax1, ax2, ax3, ax4, ax5) = gs.subplots(sharey=False)
    # fig.suptitle('ROI '+ ROi,fontsize=29)
    plt.text(.5, 0.95, 'ROI ' + ROi, fontsize=29, transform=fig18.transFigure, horizontalalignment='center')
    ax1.plot(xx, y1)
    ax1.plot(xx, y1_1, label = 'F0')
    ax1.set_title('Raw fluorescence', fontsize=20, y=1.1)
    ax1.legend()
    ax1.margins(x=0)
    ax2.plot(x, y2, 'tab:orange')
    ax2.set_title('df/f', fontsize=20, y=1.1)
    ax2.margins(x=0)
    ax3.plot(x, y3, 'tab:green')
    ax3.set_title('speed', fontsize=20, y=1.1)
    ax3.margins(x=0)

    for i in Real_Time_S_window2:
        handle = ax3.fill_betweenx(y, i[0], i[-1], color='lightpink', alpha=.5, label='runing')
    # plt.legend(handles=[handle],loc=2, prop={'size': 14})

    ax4.plot(x, y4, 'tab:red')
    ax4.set_title('Face motion', fontsize=20, y=1.1)
    ax4.margins(x=0)

    ax5.plot(x, y5)
    ax5.set_title(label='pupil', fontsize=20, y=1.1)
    ax5.margins(x=0)

    for i in Real_time_m_window2:
        handle2 = ax4.fill_betweenx(y5_0, i[0], i[-1], color='lightpink', alpha=.5)
    ####################################
    plt.xlabel('Time', fontsize=22, labelpad=25)
    plt.xticks(fontsize=25)
    for ax in fig18.get_axes():
        ax.label_outer()
        ax.tick_params(axis='both', labelsize=15)
    functions.save_fig("all.png", save_direction_figure, fig18)

    fig19 = plt.figure(figsize=(36, 20))
    x = TIme
    y00 = normal_pupil
    y0 = speed
    y1 = normal_motion
    y2 = dF[ROI]
    gs = fig19.add_gridspec(28, 45)

    # plot00
    ax00 = fig19.add_subplot(gs[3:5, :43])
    ax00.set_title('Pupil', fontsize=25, y=1.)
    ax00.plot(x, y00, linewidth=4)
    ax00.set_xticks([])
    ax00.margins(x=0)
    ax00.set_facecolor("white")
    plt.yticks(fontsize=20)

    # plot0
    ax0 = fig19.add_subplot(gs[0:2, :43])
    ax0.set_title('Running Speed', fontsize=25, y=1)
    ax0.plot(x, y0, linewidth=4)
    ax0.set_xticks([])
    plt.yticks(fontsize=20)
    ax0.margins(x=0)
    ax0.set_ylabel('cm/S', fontsize=20)
    ax0.set_facecolor("white")
    # Plot1
    ax1 = fig19.add_subplot(gs[10:22, :43])
    ax1.set_title('color code', fontsize=25, y=1.0, horizontalalignment='center')
    ax1.pcolormesh(Normal_dF_face_correlation_sorted)
    ax1.set_xticks([])
    ax1.margins(x=0)
    ax1.set_ylabel('Neuron', fontsize=25)
    plt.yticks(fontsize=20)
    # Plot2
    m = ax1.pcolormesh(Normal_dF_face_correlation_sorted)
    ax2 = fig19.add_subplot(gs[10:22, 44:45])
    fig19.colorbar(m, cax=ax2)
    plt.yticks(fontsize=20)
    # Plot3
    ax3 = fig19.add_subplot(gs[7:9, :43])
    ax3.set_title('face motion', fontsize=25, y=1.0, horizontalalignment='center')
    ax3.plot(x, y1)
    ax3.margins(x=0)
    ax3.set_facecolor("white")
    ax3.set_xticks([])
    plt.yticks(fontsize=20)
    # Plot4
    ax4 = fig19.add_subplot(gs[23:25, :43])
    ax4.set_title('dF/F', fontsize=25, y=1.0, horizontalalignment='center')
    ax4.plot(x, y2)
    ax4.margins(x=0)
    ax4.set_facecolor("white")
    ax4.set_xticks([])
    plt.yticks(fontsize=20)

    # plot5
    ax5 = fig19.add_subplot(gs[26:28, :43])
    ax5.set_title('dF/F', fontsize=25, y=1.)
    ax5.plot(x, dF[ROI2])
    ax5.set_xlabel('Time(s)', fontsize=25)
    # x1.set_ylabel('Neuron',fontsize=25)
    plt.yticks(fontsize=20)
    plt.xticks(fontsize=20)
    ax5.margins(x=0)
    ax5.set_facecolor("white")
    functions.save_fig("all22.png", save_direction_figure, fig19)
    # # Save variables
    # Calculating_mean
    WMI = np.array(A_WMI)
    mf = np.copy(motion)
    mf[mf == 0] = 'nan'
    mean_motion = leN * [np.nanmean(mf)]

    mp = np.copy(pupil)
    mp[mp == 0] = 'nan'
    mean_pupil = leN * [np.nanmean(mp)]

else:
    ###############################################
    fig19 = plt.figure(figsize=(36, 20))
    x = TIme
    y0 = speed
    y2 = dF[ROI]
    gs = fig19.add_gridspec(21, 45)
    # plot0
    ax0 = fig19.add_subplot(gs[0:2, :43])
    ax0.set_title('Running Speed', fontsize=25, y=1)
    ax0.plot(x, y0, linewidth=4)
    ax0.set_xticks([])
    plt.yticks(fontsize=20)
    ax0.margins(x=0)
    ax0.set_ylabel('cm/S', fontsize=20)
    ax0.set_facecolor("white")
    # Plot1
    ax1 = fig19.add_subplot(gs[3:15, :43])
    ax1.set_title('color code', fontsize=25, y=1.0, horizontalalignment='center')
    ax1.pcolormesh(Normal_dF_speed_correlation_sorted)
    ax1.set_xticks([])
    ax1.margins(x=0)
    ax1.set_ylabel('Neuron', fontsize=25)
    plt.yticks(fontsize=20)

    # Plot2
    m = ax1.pcolormesh(Normal_dF_speed_correlation_sorted)
    ax2 = fig19.add_subplot(gs[3:15, 44:45])
    fig19.colorbar(m, cax=ax2)
    plt.yticks(fontsize=20)
    # Plot4
    ax4 = fig19.add_subplot(gs[16:18, :43])
    ax4.set_title('dF/F', fontsize=25, y=1.0, horizontalalignment='center')
    ax4.plot(x, y2)
    ax4.margins(x=0)
    ax4.set_facecolor("white")
    ax4.set_xticks([])
    plt.yticks(fontsize=20)
    # plot5
    ax5 = fig19.add_subplot(gs[19:21, :43])
    ax5.set_title('dF/F', fontsize=25, y=1.)
    ax5.plot(x, dF[ROI2])
    ax5.set_xlabel('Time(s)', fontsize=25)
    # x1.set_ylabel('Neuron',fontsize=25)
    plt.yticks(fontsize=20)
    plt.xticks(fontsize=20)
    ax5.margins(x=0)
    ax5.set_facecolor("white")
    functions.save_fig("all22.png", save_direction_figure, fig19)
    ###############################################

#LAG
############################################

if DO_MOTION == 1:
    valid_speed_lag, lag_mean_dF_speed = functions.lag(TIme,valid_neurons_speed, save_direction030, dF, speed, "speed",speed_corr)
    valid_daceMo_lag, lag_mean_dF_facemotion = functions.lag(TIme,valid_neurons_face, save_direction030, dF, motion, "face motion",face_corr)

    lag_results = {
        'speed_lag_valid_ROIs': valid_speed_lag,
        'lag_mean_dF_speed': lag_mean_dF_speed,
        'FaceMotion_lag_valid_ROIs': valid_daceMo_lag,
        'lag_mean_dF_facemotion' : lag_mean_dF_facemotion}

    file_name_2 = "lag_results.json"
    save_direction_2 = os.path.join(save_direction030, file_name_2)
    isExist = os.path.exists(save_direction_2)
    if isExist:
        pass
    else:
        with open(save_direction_2, 'w') as file:
            json.dump(lag_results, file)

else:
    valid_speed_lag, lag_mean_dF_speed = functions.lag(TIme, valid_neurons_speed, save_direction030, dF, speed, "speed", speed_corr)
    print("End of lag calculation")
if Do_pupil == 1:
    pupil_lag, lag_mean_dF_pupil = functions.lag(TIme,valid_neurons_pupil, save_direction030, dF, pupil, "pupil",pupil_corr)

#save settings


# # A Summry of variables
#Excel file should change
#########################################
if DO_MOTION ==1:



    t = "ROI"
    columns = []
    for i in range(len(dF)):
        a = (f'{t}{i}')
        columns.append(a)

    df = pd.DataFrame(
        [LMI,  WMI, speed_mean],
        index=['LMI', 'WMI', 'mean_speed'], columns=columns).T

    file_name2 = 'variable.xlsx'
    save_direction2 = os.path.join(save_data, file_name2)
    df.to_excel(save_direction2)
else:
    t = "ROI"
    columns = []
    for i in range(len(dF)):
        a = (f'{t}{i}')
        columns.append(a)

    df = pd.DataFrame(
        [LMI, speed_mean],
        index=['Absolut_LMI', 'mean_speed'], columns=columns).T

    file_name2 = 'variable.xlsx'
    save_direction2 = os.path.join(save_data, file_name2)
    df.to_excel(save_direction2)
#Save parameters
if DO_MOTION == 1 :
    parameters = f"Date = {current_date}\n" \
                 f"Time = {current_time}\n" \
                 f"First Frame = {st_FA}\nLast frame = {end_FA}\n {blink}\n" \
                 f"Session duration =  {Total_Time}\n" \
                 f"Runnig Time = {RUN_TIME}\n" \
                 f"Rest Time =  {REST_TIME}\n" \
                 f"Run percentage = {Run_percentage}\n" \
                 f"Whisking Time {Whisking_TIME}\n" \
                 f"Whisking percentage = {Whisking_percentage}\n" \
                 f"neuropil impact factor = {neuropil_impact_factor}\n" \
                 f"F0 calculating method = {F0_method}\nThis session has {len(pupil)} frames\nrelative time base on xml:\n" \
                 f"first frame{TIme[0]}(s)\n last frame {TIme[-1]}(s)\n" \
                 f"save path = {save_direction1}\n" \
                 f"suite2p path = {Base_path}\n" \
                 f"channel number = {channel_number}\nLaser Wavelength = {laserWavelength}\nObjective Lens = {objectiveLens}" \
                 f"Objective Lens Mag = {objectiveLensMag}\nOptical Zoom = {opticalZoom}\nBit Depth = {bitDepth}\nDwell Time = {dwellTime}" \
                 f"Frame Period{framePeriod}\nMicrons Per Pixel = {micronsPerPixel}\n Two Photon Laser Power{TwophotonLaserPower}"
else:
    parameters = f"Date = {current_date}\n" \
                 f"Time = {current_time}\n" \
                 f"First Frame = {st_FA}\nLast frame = {end_FA}\n {blink}\n" \
                 f"Session duration =  {Total_Time}\n" \
                 f"Runnig Time = {RUN_TIME}\n" \
                 f"Rest Time =  {REST_TIME}\n" \
                 f"Run percentage = {Run_percentage}\n" \
                 f"neuropil impact factor = {neuropil_impact_factor}\n" \
                 f"F0 calculating method = {F0_method}\nThis session has {len(pupil)} frames\nrelative time base on xml:\n" \
                 f"first frame{TIme[0]}(s)\n last frame {TIme[-1]}(s)\n" \
                 f"save path = {save_direction1}\n" \
                 f"suite2p path = {Base_path}\n" \
                 f"channel number = {channel_number}\nLaser Wavelength = {laserWavelength}\nObjective Lens = {objectiveLens}" \
                 f"Objective Lens Mag = {objectiveLensMag}\nOptical Zoom = {opticalZoom}\nBit Depth = {bitDepth}\nDwell Time = {dwellTime}" \
                 f"Frame Period{framePeriod}\nMicrons Per Pixel = {micronsPerPixel}\n Two Photon Laser Power{TwophotonLaserPower}"


save_direction_text = os.path.join(save_data , "parameters.text")
isExist = os.path.exists(save_direction_text)
if isExist:
    pass
else:
    with open(save_direction_text, 'a') as file:
        # Write the text to the file
        file.write(parameters + '\n')
print("End of program")
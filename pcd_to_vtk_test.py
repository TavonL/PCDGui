import os

from vtkmodules.util.numpy_support import numpy_to_vtk
import vtk
from plyfile import PlyData, PlyElement
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkPoints,
    vtkUnsignedCharArray
)
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkPolyData
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
)

'''读取点云数据为np格式，转化为VTK显示的类'''
STPLS3D_SEG_ID_TO_COLOR={'0': [255, 0, 0], '1': [0, 255, 0], '2': [0, 0, 255],
                        '3': [255, 0, 0], '4': [0, 255, 0], '5': [0, 0, 255],
                        '6': [255, 0, 0], '7': [0, 255, 0], '8': [0, 0, 255],
                        '9': [255, 0, 0], '10': [0, 255, 0], '11': [0, 0, 255],
                        '12': [255, 0, 0], '13': [0, 255, 0], '14': [0, 0, 255],
                        '15': [255, 0, 255], '17': [0, 0, 255],
                         '18': [255, 0, 255],'19':[0, 255, 0]}
STPLS3D_SEG_ID_TO_CLASSNAME={'0': 'Ground', '1': 'Building', '2': 'LowVegetation',
                        '3': 'MediumVegetation', '4': 'HighVegetation', '5': 'Vehicle',
                        '6': 'Truck', '7': 'Aircraft', '8': 'MilitaryVehicle',
                        '9': 'Bike', '10': 'Motorcycle', '11': 'LightPole',
                        '12': 'StreetSgin', '13': 'Clutter', '14': 'Fence',
                        '15': 'Road', '17': 'Windows',
                         '18': 'Dirt','19':'Grass'}
class PCD_VTK_ACTOR():
    def read_pcd_txt(self,datapath):
        pass
    def read_pcd_ply(self,datapath):
        plydata=PlyData.read(datapath)
        np_x=np.array(plydata['vertex']['x']).reshape(-1,1)
        np_y=np.array(plydata['vertex']['y']).reshape(-1,1)
        np_z=np.array(plydata['vertex']['z']).reshape(-1,1)
        np_points=np.concatenate((np_x,np_y,np_z),axis=1)
        np_r = np.array(plydata['vertex']['red']).reshape(-1, 1)
        np_g = np.array(plydata['vertex']['green']).reshape(-1, 1)
        np_b = np.array(plydata['vertex']['blue']).reshape(-1, 1)
        np_color = np.concatenate((np_r, np_g, np_b), axis=1)
        np_class=np.array(plydata['vertex']['class'])
        np_instance=np.array(plydata['vertex']['instance'])
        return np_points,np_color,np_class,np_instance
    def color_change(self):
        list_color=[]
        if self.vistype=='sem':
            for i in self.pcdclass:
                list_color.append(self.colortable[str(i)])
        else:
            for i in self.pcdinstance:
                list_color.append(self.colortable[str(i)])

        new_color=np.asarray((list_color))
        self.color=new_color
    def refresh_color(self):
        ptcolor = vtkUnsignedCharArray()
        ptcolor.SetNumberOfComponents(3)
        for i in self.color:
            ptcolor.InsertNextTuple(i)
            self.vtkpolydata.GetCellData().SetScalars(ptcolor)
    def colortable_change(self,colortable):
        self.colortable=colortable
        self.color_change()
        self.refresh_color()
    def __init__(self,datapath,vistype='origin',colortable=None):
        super(PCD_VTK_ACTOR,self).__init__()
        points,color,pcdclass,pcdinstance=self.read_pcd_ply(datapath=datapath)
        self.points=points
        self.color=color
        self.pcdclass=pcdclass
        self.pcdinstance=pcdinstance
        self.points_num=len(points)
        self.pcd_name=datapath.split('\\')[-1]
        self.vistype=vistype
        self.colortable=colortable
        vtkpoints=vtkPoints()
        vtkpoints.SetData(numpy_to_vtk(points))
        self.vtkpolydata=vtkPolyData()
        self.vtkpolydata.SetPoints(vtkpoints)
        vtkvert=vtkCellArray()
        for i in range(len(points)):
            vtkvert.InsertNextCell(1)
            vtkvert.InsertCellPoint(i)
        self.vtkpolydata.SetVerts(vtkvert)

        if vistype!='origin':
            self.color_change()
        self.refresh_color()

        mapper = vtkPolyDataMapper()
        mapper.SetInputData(self.vtkpolydata)
        actor = vtkActor()
        actor.SetMapper(mapper)
        self.pcdactor=actor

class PCD_VTK_DATASET():
    def class_color_settiing(self,pcdclass):
        if self.dataset_name=='STPLS3D':
            self.semcolor_table=STPLS3D_SEG_ID_TO_COLOR
    def instacne_color_setting(self,pcdinstance):
        pass
    def init_pcdvis_actor(self,dataset_path):
        file_name_list=os.listdir(dataset_path)
        i=0
        if self.mode=='sem':
            for f in file_name_list:
                self.pcdvis_origin.append(PCD_VTK_ACTOR(datapath=dataset_path+'\\'+f))
                self.pcdvis_gt.append(PCD_VTK_ACTOR(datapath=dataset_path + '\\' + f,vistype=self.mode,colortable=self.semcolor_table))
                #self.pcdvis1.append(PCD_VTK_ACTOR(datapath=dataset_path + '\\' + f,vistype='sem',colortable=self.semcolor_table))
                #self.pcdvis2.append(PCD_VTK_ACTOR(datapath=dataset_path + '\\' + f, vistype=self.mode, colortable=self.semcolor_table))
                i=i+1
                break
        else:
            for f in file_name_list:
                self.pcdvis_origin.append(PCD_VTK_ACTOR(datapath=dataset_path+'\\'+f))
                self.pcdvis_gt.append(PCD_VTK_ACTOR(datapath=dataset_path + '\\' + f,vistype=self.mode,colortable=self.inscolor_table))
                self.pcdvis1.append(PCD_VTK_ACTOR(datapath=dataset_path + '\\' + f,vistype='sem',colortable=self.semcolor_table))
                self.pcdvis2.append(
                    PCD_VTK_ACTOR(datapath=dataset_path + '\\' + f, vistype=self.mode, colortable=self.inscolor_table))
                i = i + 1
                break

    def __init__(self,dataset_path,mode='sem',dataset_name='STPLS3D'):
        super(PCD_VTK_DATASET, self).__init__()
        self.dataset_path=dataset_path
        self.dataset_name=dataset_name
        self.dataset_num=0
        self.sem_id_to_label=None
        self.inscolor_table=None
        self.semcolor_table=None
        self.pcdvis_origin=None
        self.pcdvis_gt=None
        self.pcdvis1=None
        self.pcdvis2=None
        self.mode=mode
        self.file_name_list = os.listdir(dataset_path)
        self.dataset_num=len(self.file_name_list)
        if dataset_name=='STPLS3D':
            self.sem_id_to_label=STPLS3D_SEG_ID_TO_CLASSNAME
            self.semcolor_table=STPLS3D_SEG_ID_TO_COLOR
        else:
            pass
        if self.mode!='sem':
            #设置instance的颜色表
            pass
        #self.init_pcdvis_actor(self.dataset_path)

class DatasetLoadingThread(QtCore.QThread):
    _signal=QtCore.pyqtSignal(int)
    def __init__(self,dataset,id=0):
        super(DatasetLoadingThread,self).__init__()
        self.dataset=dataset
        self.id=id
    def get_dataset(self):
        return self.dataset
    def run(self):
        if self.dataset.mode == 'sem':
            self.dataset.pcdvis_origin=PCD_VTK_ACTOR(datapath=self.dataset.dataset_path + '\\' + self.dataset.file_name_list[self.id])
            self._signal.emit(25)
            self.dataset.pcdvis_gt=PCD_VTK_ACTOR(datapath=self.dataset.dataset_path + '\\' + self.dataset.file_name_list[self.id], vistype=self.dataset.mode, colortable=self.dataset.semcolor_table)
            self._signal.emit(50)
            self.dataset.pcdvis1=PCD_VTK_ACTOR(datapath=self.dataset.dataset_path + '\\' + self.dataset.file_name_list[self.id],vistype='sem',colortable=self.dataset.semcolor_table)
            self._signal.emit(75)
            self.dataset.pcdvis2=PCD_VTK_ACTOR(datapath=self.dataset.dataset_path + '\\' + self.dataset.file_name_list[self.id], vistype=self.dataset.mode, colortable=self.dataset.semcolor_table)
            self._signal.emit(100)
        else:
            self.dataset.pcdvis_origin=PCD_VTK_ACTOR(datapath=self.dataset.dataset_path + '\\' + self.dataset.file_name_list[self.id])
            self._signal.emit(25)
            self.dataset.pcdvis_gt=PCD_VTK_ACTOR(datapath=self.dataset.dataset_path + '\\' + self.dataset.file_name_list[self.id], vistype=self.dataset.mode, colortable=self.dataset.inscolor_table)
            self._signal.emit(50)
            self.dataset.pcdvis1=PCD_VTK_ACTOR(datapath=self.dataset.dataset_path + '\\' + self.dataset.file_name_list[self.id], vistype='sem', colortable=self.dataset.semcolor_table)
            self._signal.emit(75)
            self.dataset.pcdvis2=PCD_VTK_ACTOR(datapath=self.dataset.dataset_path + '\\' + self.dataset.file_name_list[self.id], vistype=self.dataset.mode, colortable=self.dataset.inscolor_table)
            self._signal.emit(100)

















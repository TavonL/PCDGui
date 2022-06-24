import os

from vtkmodules.util.numpy_support import numpy_to_vtk
import vtk
from plyfile import PlyData, PlyElement
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    vtkPoints,
    vtkUnsignedCharArray,
    vtkLookupTable,
    VTK_INT
)
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkPolyData,

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
class PcdToVtkSource():
    def read_pcd_ply(self,datapath):
        plydata = PlyData.read(datapath)
        np_x = np.array(plydata['vertex']['x']).reshape(-1, 1)
        np_y = np.array(plydata['vertex']['y']).reshape(-1, 1)
        np_z = np.array(plydata['vertex']['z']).reshape(-1, 1)
        np_points = np.concatenate((np_x, np_y, np_z), axis=1)
        np_r = np.array(plydata['vertex']['red']).reshape(-1, 1)
        np_g = np.array(plydata['vertex']['green']).reshape(-1, 1)
        np_b = np.array(plydata['vertex']['blue']).reshape(-1, 1)
        np_color = np.concatenate((np_r, np_g, np_b), axis=1)
        np_class = np.array(plydata['vertex']['class'])
        np_instance = np.array(plydata['vertex']['instance'])
        return np_points, np_color, np_class, np_instance
    def read_pcd_npz(self,datapath):
        data=np.load(datapath)
        np_points=data['coord']
        np_color=data['color']/2+0.5#(0-1)
        np_class=data['gt_sem']
        return np_points, np_color, np_class
    def __init__(self,datapath=None,mode='origin'):
        super(PcdToVtkSource,self).__init__()
        if mode=='origin':
            np_points, np_color, np_class, np_instance=self.read_pcd_ply(datapath)
        elif mode=='ins':
            #调用接口运行ins seg模型
            pass
        else:
            #弱监督分割要根据不同的模型，大坑
            #输入 datapath 输出 全监督的模型内容 弱监督的模型内容
            np_points, np_color, np_class = self.read_pcd_npz(datapath)
        vtk_points = vtkPoints()
        vtk_points.SetData(numpy_to_vtk(np_points))
        self.source = vtkPolyData()
        self.source.SetPoints(vtk_points)
        self.points_num = len(np_points)
        self.pcd_name = datapath.split('\\')[-1]
        vtk_vert = vtkCellArray()
        for i in range(self.points_num):
            vtk_vert.InsertNextCell(1)
            vtk_vert.InsertCellPoint(i)
        self.source.SetVerts(vtk_vert)

        #color类型为Unsign Char ("0-255","0-255","0-255")
        vtk_color=numpy_to_vtk(np_color)
        vtk_color.SetName('color')

        vtk_class=numpy_to_vtk(np_class,array_type=VTK_INT)
        vtk_class.SetName('class')

        self.source.GetCellData().AddArray(vtk_color)
        self.source.GetCellData().AddArray(vtk_class)

        self.source.GetCellData().SetActiveScalars('color')
        self.source.GetCellData().SetActiveScalars('class')
        if mode=='ins':
            vtk_instance=numpy_to_vtk(np_instance,array_type=VTK_INT)
            vtk_instance.SetName('instance')
            self.source.GetCellData().AddArray(vtk_instance)
            self.source.GetCellData().SetActiveScalars('instance')



class PcdToVtkActor():
    def __init__(self,vtk_data,mode='origin'):
        super(PcdToVtkActor,self).__init__()
        self.data=vtk_data.source
        self.mapper=vtkPolyDataMapper()
        self.actor=vtkActor()
        self.mapper.SetInputData(self.data)
        self.actor.SetMapper(self.mapper)
        self.lut=vtkLookupTable()
        self.mapper.SetLookupTable(self.lut)
        self.mode=mode
        self.setting_color()

    def setting_lut(self,color_nums=20):
        self.lut.SetNumberOfColors(color_nums)
        self.lut.SetHueRange(0, 1)
        self.lut.Build()
    def setting_lut_by_input(self,input_colors):
        #input_colors是c*4的列表 id,r,g,b| r,g,b 范围为0-1
        for color in input_colors:
            self.lut.SetTableValue(color[0],color[1],color[2],color[3])
        self.lut.Build()

        pass
    def setting_color(self,input_colors=None):
        if self.mode=='origin':
            self.mapper.ScalarVisibilityOn()
            self.mapper.SetColorModeToDirectScalars()
            self.mapper.SetScalarModeToUseCellFieldData()
            self.mapper.SelectColorArray('color')
        elif self.mode=='sem':
            self.mapper.ScalarVisibilityOn()
            self.mapper.SetColorModeToMapScalars()
            self.mapper.SetScalarModeToUseCellFieldData()

            self.setting_lut()
            self.mapper.SetScalarRange(0,19)
            self.mapper.SelectColorArray('class')
        else:
            self.mapper.ScalarVisibilityOn()
            self.mapper.SetColorModeToMapScalars()
            self.mapper.SetScalarModeToUseCellFieldData()
            self.setting_lut()
            self.mapper.SetScalarRange(0, 19)
            self.mapper.SelectColorArray('Instance')


















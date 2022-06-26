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
COLORTABEL=[[0,0,1,0],[1,1,0,0]]
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
        np_sem_gt=data['gt_sem']
        np_sem_pred=data['sem']
        return np_points, np_color, np_sem_gt,np_sem_pred
    def read_pcd_npz_test(self,datapath,mode='ins'):
        if mode=='ins':
            #return {'xyz_np': xyz_np, 'rgb_np': rgb_np, 'sem_gt_np':sem_gt_np, 'ins_gt_np':ins_gt_np,
                    #'sem_pred_np': sem_pred_np, 'ins_pred_np': ins_pred_np, 'nInstance': nInstance,
                    #'nProposal': nProposal, 'APs': APs, 'sem_oa': sem_oa, 'sem_miou': sem_miou}
            data=np.load(datapath)
            np_points=data['xyz_np']
            np_color=data['rgb_np']/255
            np_sem_gt=data['sem_gt_np']
            np_ins_gt=data['ins_gt_np']
            np_sem_pred=data['sem_pred_np']
            np_ins_pred=data['ins_pred_np']
            num_instance=data['nInstance']
            num_proposal=data['nProposal']
            APs=data['APs']
            sem_acc=data['sem_oa']
            sem_miou=data['sem_miou']
            return np_points,np_color,np_sem_pred,np_ins_gt,np_ins_pred,num_instance,num_proposal,APs,sem_acc,sem_miou
        else:
            data = np.load(datapath)
            np_points = data['coord']
            np_color = data['color'] / 2 + 0.5  # (0-1)
            np_sem_gt = data['gt_sem']

            np_sem_pred_1 = data['sem1']
            sem_acc_1=data['acc1']
            sem_miou_1=data['miou1']
                #OTOC

            np_sem_pred_2 = data['sem2']
            sem_acc_2 = data['acc2']
            sem_miou_2 = data['miou2']
                #3D-UNet全监督

            return np_points,np_color,np_sem_gt,np_sem_pred_1,np_sem_pred_2,sem_acc_1,sem_miou_1,sem_acc_2,sem_miou_2

    def __init__(self,datapath=None,mode='ins',semModel=None):
        super(PcdToVtkSource,self).__init__()
        if mode=='ins':
            #调用接口运行ins seg模型
            #假装函数 (语义类别只有两类，建筑物和非建筑物)
            np_points, np_color, np_sem_pred, np_ins_gt,np_ins_pred,num_instance,num_proposal,APs,sem_acc,sem_miou=self.read_pcd_npz_test(datapath,mode=mode)
            self.num_instance=num_instance+1#存在-100
            self.num_proposal=num_proposal+1#存在-100
            self.APs=APs
            self.sem_acc=sem_acc
            self.sem_miou=sem_miou
            np_ins_gt[np_ins_gt==-100]=num_instance
            np_ins_pred[np_ins_pred==-100]=num_proposal

        else:
            #弱监督分割要根据不同的模型，大坑
            #输入 datapath 输出 全监督的模型内容 弱监督的模型内容

            np_points, np_color, np_sem_gt,np_sem_pred_1,np_sem_pred_2,sem_acc_1,sem_miou_1,sem_acc_2,sem_miou_2= self.read_pcd_npz_test(datapath,mode=mode)
            self.sem_acc_1 = sem_acc_1
            self.sem_miou_1 = sem_miou_1
            self.sem_acc_2 = sem_acc_2
            self.sem_miou_2 = sem_miou_2


        vtk_points = vtkPoints()
        vtk_points.SetData(numpy_to_vtk(np_points))
        self.source = vtkPolyData()
        self.source.SetPoints(vtk_points)
        self.points_num = len(np_points)
        self.pcd_name = (datapath.split('\\')[-1]).split('.')[0]

        self.mode=mode
        vtk_vert = vtkCellArray()
        for i in range(self.points_num):
            vtk_vert.InsertNextCell(1)
            vtk_vert.InsertCellPoint(i)
        self.source.SetVerts(vtk_vert)
        #color类型为Unsign Char ("0-255","0-255","0-255")
        vtk_color=numpy_to_vtk(np_color)
        vtk_color.SetName('color')
        self.source.GetCellData().AddArray(vtk_color)
        self.source.GetCellData().SetActiveScalars('color')

        if self.mode=='ins':
            vtk_sem_pred = numpy_to_vtk(np_sem_pred, array_type=VTK_INT)
            vtk_sem_pred.SetName('semPred')
            self.source.GetCellData().AddArray(vtk_sem_pred)
            self.source.GetCellData().SetActiveScalars('semPred')
            vtk_ins_gt = numpy_to_vtk(np_ins_gt, array_type=VTK_INT)
            vtk_ins_gt.SetName('insGT')
            self.source.GetCellData().AddArray(vtk_ins_gt)
            self.source.GetCellData().SetActiveScalars('insGT')
            vtk_ins_pred = numpy_to_vtk(np_ins_pred, array_type=VTK_INT)
            vtk_ins_pred.SetName('insPred')
            self.source.GetCellData().AddArray(vtk_ins_pred)
            self.source.GetCellData().SetActiveScalars('insPred')
        else:
            vtk_sem_pred_1 = numpy_to_vtk(np_sem_pred_1, array_type=VTK_INT)
            vtk_sem_pred_1.SetName('semPred1')
            self.source.GetCellData().AddArray(vtk_sem_pred_1)
            self.source.GetCellData().SetActiveScalars('semPred1')
            vtk_sem_pred_2 = numpy_to_vtk(np_sem_pred_2, array_type=VTK_INT)
            vtk_sem_pred_2.SetName('semPred2')
            self.source.GetCellData().AddArray(vtk_sem_pred_2)
            self.source.GetCellData().SetActiveScalars('semPred2')
            vtk_sem_gt = numpy_to_vtk(np_sem_gt, array_type=VTK_INT)
            vtk_sem_gt.SetName('semGT')
            self.source.GetCellData().AddArray(vtk_sem_gt)
            self.source.GetCellData().SetActiveScalars('semGT')




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
        if vtk_data.mode=="ins":
            self.num_sem=2#building and 非building
            self.num_instance=vtk_data.num_instance
            self.num_proposal=vtk_data.num_proposal
        else:
            self.num_sem=20
            self.num_instance=None
            self.num_proposal=None

        self.setting_color()

    def setting_lut(self,color_nums=20):
        self.lut.SetNumberOfColors(color_nums)
        self.lut.SetHueRange(0.67, 0)
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
        elif self.mode=='semGT':
            self.mapper.ScalarVisibilityOn()
            self.mapper.SetColorModeToMapScalars()
            self.mapper.SetScalarModeToUseCellFieldData()
            self.setting_lut(color_nums=self.num_sem)
            self.mapper.SetScalarRange(0,self.num_sem-1)
            self.mapper.SelectColorArray('semGT')
        elif self.mode=='insGT':
            self.mapper.ScalarVisibilityOn()
            self.mapper.SetColorModeToMapScalars()
            self.mapper.SetScalarModeToUseCellFieldData()
            self.setting_lut(color_nums=self.num_instance)
            self.mapper.SetScalarRange(0, self.num_instance-1)
            self.mapper.SelectColorArray('insGT')
        elif self.mode=='insPred':
            self.mapper.ScalarVisibilityOn()
            self.mapper.SetColorModeToMapScalars()
            self.mapper.SetScalarModeToUseCellFieldData()
            self.setting_lut(color_nums=self.num_proposal)
            self.mapper.SetScalarRange(0, self.num_proposal-1)
            self.mapper.SelectColorArray('insPred')
        elif self.mode=='semPred1':
            #semPred1
            self.mapper.ScalarVisibilityOn()
            self.mapper.SetColorModeToMapScalars()
            self.mapper.SetScalarModeToUseCellFieldData()
            self.setting_lut(color_nums=self.num_sem)
            #self.setting_lut_by_input(input_colors=COLORTABEL)
            self.mapper.SetScalarRange(0, self.num_sem-1)
            self.mapper.SelectColorArray('semPred1')
        elif self.mode == 'semPred2':
            # semPred2
            self.mapper.ScalarVisibilityOn()
            self.mapper.SetColorModeToMapScalars()
            self.mapper.SetScalarModeToUseCellFieldData()
            self.setting_lut(color_nums=self.num_sem)
            # self.setting_lut_by_input(input_colors=COLORTABEL)
            self.mapper.SetScalarRange(0, self.num_sem - 1)
            self.mapper.SelectColorArray('semPred2')
        else:
            # semPred
            self.mapper.ScalarVisibilityOn()
            self.mapper.SetColorModeToMapScalars()
            self.mapper.SetScalarModeToUseCellFieldData()
            self.setting_lut(color_nums=self.num_sem)
            # self.setting_lut_by_input(input_colors=COLORTABEL)
            self.mapper.SetScalarRange(0, self.num_sem - 1)
            self.mapper.SelectColorArray('semPred')



















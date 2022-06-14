import os

from vtkmodules.util.numpy_support import numpy_to_vtk
import vtk
from plyfile import PlyData, PlyElement
from PyQt5 import QtCore, QtGui, QtWidgets
from pcd_to_vtk import PcdToVtkSource
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
class DatasetLoadingThread(QtCore.QThread):
    _signal=QtCore.pyqtSignal(int)
    def __init__(self,dataset_path):
        super(DatasetLoadingThread,self).__init__()
        self.dataset_path=dataset_path
        self.sources=[]
    def get_sources(self):
        return self.sources
    def run(self):
        file_name_list = os.listdir(self.dataset_path)
        i=0
        max=len(file_name_list)
        for f in file_name_list:
            self.sources.append(PcdToVtkSource(self.dataset_path+'\\'+f))
            i=i+1
            self._signal.emit(i*100/max)
            if i==5:
                self._signal.emit(100)
                return



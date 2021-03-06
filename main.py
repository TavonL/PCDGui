from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import vtk
from PyQt5 import QtCore, QtGui, QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from pcdgui import Ui_Form
from qt_material import apply_stylesheet
from pcd_to_vtk import PcdToVtkActor,PcdToVtkSource
from pcd_thread import DatasetLoadingThread
import open3d as o3d
import numpy as np



class MyWindow(QtWidgets.QMainWindow, Ui_Form):
    def text_change(self,source):
        self.label_pcdname.setText('Point Cloud Name:' + source.pcd_name)
        self.label_pointnum.setText('Points Num:' + str(source.points_num))

        self.label_sem_acc.setText("Semantic Seg Acc:"+str(np.around(source.sem_acc,3)))
        self.label_sem_miou.setText("Semantic Seg mIou:" + str(np.around(source.sem_miou,3)))
        self.label_ins_APs.setText("Instance Seg APs:"+str(np.around(source.APs[0],3))+"  "+str(np.around(source.APs[1],3))+"  "+str(np.around(source.APs[2],3)))
    def text_change_weakly(self,source):
        self.label_pcdname_weakly.setText('Point Cloud Name:' + source.pcd_name)
        self.label_pointnum_weakly.setText('Points Num:' + str(source.points_num))
        if self.label_backbone1.text()=="Ours_Weakly_Sup":
            self.label_sem_acc_1.setText("Semantic Seg 1 Acc:" + str(np.around(source.sem_acc_1,3)))
            self.label_sem_miou_1.setText("Semantic Seg 1 mIou:" + str(np.around(source.sem_miou_1,3)))
        else:
            self.label_sem_acc_1.setText("Semantic Seg 1 Acc:" + str(np.around(source.sem_acc_2, 3)))
            self.label_sem_miou_1.setText("Semantic Seg 1 mIou:" + str(np.around(source.sem_miou_2, 3)))
        if self.label_backbone2.text()=="Ours_Weakly_Sup":
            self.label_sem_acc_2.setText("Semantic Seg 2 Acc:" + str(np.around(source.sem_acc_1, 3)))
            self.label_sem_miou_2.setText("Semantic Seg 2 mIou:" + str(np.around(source.sem_miou_1, 3)))
        else:
            self.label_sem_acc_2.setText("Semantic Seg 2 Acc:" + str(np.around(source.sem_acc_2,3)))
            self.label_sem_miou_2.setText("Semantic Seg 2 mIou:" + str(np.around(source.sem_miou_2,3)))
    def weakly_visualize(self,source,mode='init'):

        if mode!='init':
            self.ren_origin_weakly.RemoveActor(self.actor_origin_weakly.actor)
            self.ren_gt_weakly.RemoveActor(self.actor_gt_weakly.actor)
            self.ren_sup1.RemoveActor(self.actor_sup1.actor)
            self.ren_sup2.RemoveActor(self.actor_sup2.actor)
        self.actor_origin_weakly = PcdToVtkActor(source)
        self.actor_gt_weakly = PcdToVtkActor(source,mode='semGT')
        if self.label_backbone1.text()=="Ours_Weakly_Sup":
            self.actor_sup1 = PcdToVtkActor(source,mode='semPred1')
        else:
            self.actor_sup1 = PcdToVtkActor(source, mode='semPred2')
        if self.label_backbone2.text()=="Ours_Weakly_Sup":
            self.actor_sup2 = PcdToVtkActor(source, mode='semPred1')
        else:
            self.actor_sup2 = PcdToVtkActor(source,mode='semPred2')
        self.ren_origin_weakly.AddActor(self.actor_origin_weakly.actor)
        self.ren_gt_weakly.AddActor(self.actor_gt_weakly.actor)
        self.ren_sup1.AddActor(self.actor_sup1.actor)
        self.ren_sup2.AddActor(self.actor_sup2.actor)
        self.ren_origin_weakly.ResetCamera()
        self.ren_gt_weakly.ResetCamera()
        self.ren_sup1.ResetCamera()
        self.ren_sup2.ResetCamera()
        self.iren_origin_weakly.Initialize()
        self.iren_gt_weakly.Initialize()
        self.iren_sup1.Initialize()
        self.iren_sup2.Initialize()
    def visualize(self,source,mode='init'):
        if mode!='init':
            self.ren_origin.RemoveActor(self.actor_origin.actor)
            self.ren_gt.RemoveActor(self.actor_gt.actor)
            self.ren_sem.RemoveActor(self.actor_sem.actor)
            self.ren_ins.RemoveActor(self.actor_ins.actor)
        self.actor_origin = PcdToVtkActor(source)
        self.actor_gt= PcdToVtkActor(source,mode='insGT')
        self.actor_sem = PcdToVtkActor(source,mode='semPred')
        self.actor_ins = PcdToVtkActor(source,mode='insPred')
        self.ren_origin.AddActor(self.actor_origin.actor)
        self.ren_gt.AddActor(self.actor_gt.actor)
        self.ren_sem.AddActor(self.actor_sem.actor)
        self.ren_ins.AddActor(self.actor_ins.actor)
        self.ren_origin.ResetCamera()
        self.ren_gt.ResetCamera()
        self.ren_sem.ResetCamera()
        self.ren_ins.ResetCamera()
        self.iren_origin.Initialize()
        self.iren_gt.Initialize()
        self.iren_sem.Initialize()
        self.iren_ins.Initialize()

    def changeProgressBar_weakly(self,value):
        self.loadingbar.setValue(value)
        if value==100:
            self.sources_weakly = self.workthread.get_sources()
            if self.load_weakly_counts==0:

                self.weakly_visualize(self.sources_weakly[0])
                self.load_weakly_counts = 1

            else:
                self.weakly_visualize(self.sources_weakly[0],mode="update")
                self.load_weakly_counts=1
            self.pushButton_previous_weakly.setEnabled(False)
            if len(self.sources_weakly)>1:
                self.pushButton_next_weakly.setEnabled(True)
            self.label_pcdnum_weakly.setText(str(1)+'/'+str(len(self.sources_weakly)))
            #self.label_pcdname_weakly.setText('Point Cloud Name:'+self.sources_weakly[0].pcd_name)
            #self.label_pointnum_weakly.setText('Points Num:'+str(self.sources_weakly[0].points_num))
            self.text_change_weakly(self.sources_weakly[0])
    def changeProgressBar(self,value):
        self.loadingbar.setValue(value)
        if value == 100:
            self.sources = self.workthread.get_sources()
            if self.load_counts==0:
                self.visualize(self.sources[0])
                self.load_counts=1
            else:
                self.visualize(self.sources[0],mode="update")
                self.load_counts= 1
            self.pushButton_previous.setEnabled(False)
            if len(self.sources) > 1:
                self.pushButton_next.setEnabled(True)
            self.label_pcdnum.setText(str(1) + '/' + str(len(self.sources)))
            #self.label_pcdname.setText('Point Cloud Name:' + self.sources[0].pcd_name)
            #self.label_pointnum.setText('Points Num:' + str(self.sources[0].points_num))
            self.text_change(self.sources[0])



    def dataset_select(self):
        folder=QtWidgets.QFileDialog.getExistingDirectory()
        if folder==self.label_datasetname_weakly.text():
            return
        self.label_datasetname.setText(folder)
        folder = folder.replace('/', '\\')
        if self.label_datasetname.text()!="None":
            self.pushButton_loading.setEnabled(True)
    def dataset_select_weakly(self):
        folder=QtWidgets.QFileDialog.getExistingDirectory()
        if folder==self.label_datasetname_weakly.text():
            return
        self.label_datasetname_weakly.setText(folder)
        folder=folder.replace('/','\\')
        #self.pushButton_loading_weakly.setEnabled(True)
        self.pushButton_backbone1_select.setEnabled(True)
        self.pushButton_backbone2_select.setEnabled(True)
    def backbone_select_1(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory()
        self.label_backbone1.setText(folder.split('/')[-1])
        if self.label_backbone2.text()!="None":
            self.pushButton_loading_weakly.setEnabled(True)

    def backbone_select_2(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory()
        self.label_backbone2.setText(folder.split('/')[-1])
        if self.label_backbone1.text()!="None":
            self.pushButton_loading_weakly.setEnabled(True)


    def loading_weakly(self):
        folder = self.label_datasetname_weakly.text()
        folder = folder.replace('/', '\\')
        self.loadingbar = QtWidgets.QProgressDialog()
        self.loadingbar.setGeometry(QtCore.QRect(1000, 580, 800, 300))
        self.loadingbar.setRange(0, 100)
        self.loadingbar.setValue(0)
        self.loadingbar.setMinimumDuration(1000)
        self.loadingbar.setWindowTitle('????????????')
        self.loadingbar.setLabelText('Loading Point Cloud')
        self.loadingbar.setCancelButtonText(None)
        self.loadingbar.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.workthread = DatasetLoadingThread(folder,mode='sem')
        self.workthread._signal.connect(self.changeProgressBar_weakly)
        self.workthread.start()
    def loading(self):
        folder=self.label_datasetname.text()
        folder = folder.replace('/', '\\')
        self.loadingbar = QtWidgets.QProgressDialog()
        self.loadingbar.setGeometry(QtCore.QRect(1000, 580, 800, 300))
        self.loadingbar.setRange(0, 100)
        self.loadingbar.setValue(0)
        self.loadingbar.setMinimumDuration(1000)
        self.loadingbar.setWindowTitle('????????????')
        self.loadingbar.setLabelText('Loading Point Cloud')
        self.loadingbar.setCancelButtonText(None)
        self.loadingbar.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.workthread = DatasetLoadingThread(folder,mode='ins')
        self.workthread._signal.connect(self.changeProgressBar)
        self.workthread.start()
    def next_weakly(self):
        #??????????????????????????????????????????next
        idx,total=(self.label_pcdnum_weakly.text()).split('/')
        idx=str(int(idx)+1)
        if int(idx)>=int(total):
            self.pushButton_next_weakly.setEnabled(False)
        if int(idx)>1:
            self.pushButton_previous_weakly.setEnabled(True)
        self.weakly_visualize(self.sources_weakly[int(idx)-1],mode='update')
        self.label_pcdnum_weakly.setText(idx + '/' + total)
        #self.label_pcdname_weakly.setText('Point Cloud Name:' + self.sources_weakly[int(idx)-1].pcd_name)
        #self.label_pointnum_weakly.setText('Points Num:' + str(self.sources_weakly[int(idx)-1].points_num))
        self.text_change_weakly(self.sources_weakly[int(idx)-1])
    def next(self):
        # ??????????????????????????????????????????next
        idx, total = (self.label_pcdnum.text()).split('/')
        idx = str(int(idx) + 1)
        if int(idx) >= int(total):
            self.pushButton_next.setEnabled(False)
        if int(idx) > 1:
            self.pushButton_previous.setEnabled(True)
        self.visualize(self.sources[int(idx) - 1], mode='update')
        self.label_pcdnum.setText(idx + '/' + total)
        #self.label_pcdname.setText('Point Cloud Name:' + self.sources[int(idx) - 1].pcd_name)
        #self.label_pointnum.setText('Points Num:' + str(self.sources[int(idx) - 1].points_num))
        self.text_change(self.sources[int(idx) - 1])
    def previous(self):
        # ??????????????????????????????????????????previous
        idx, total = (self.label_pcdnum.text()).split('/')
        idx = str(int(idx) - 1)
        if int(idx) < int(total):
            self.pushButton_next.setEnabled(True)
        if int(idx) <= 1:
            self.pushButton_previous.setEnabled(False)
        self.visualize(self.sources[int(idx) - 1], mode='update')
        self.label_pcdnum.setText(idx + '/' + total)
        #self.label_pcdname.setText('Point Cloud Name:' + self.sources[int(idx) - 1].pcd_name)
        #self.label_pointnum.setText('Points Num:' + str(self.sources[int(idx) - 1].points_num))
        self.text_change(self.sources[int(idx) - 1])
    def previous_weakly(self):
        # ??????????????????????????????????????????previous
        idx, total = (self.label_pcdnum_weakly.text()).split('/')
        idx = str(int(idx)-1)
        if int(idx) < int(total):
            self.pushButton_next_weakly.setEnabled(True)
        if int(idx) <=1:
            self.pushButton_previous_weakly.setEnabled(False)
        self.weakly_visualize(self.sources_weakly[int(idx) - 1],mode='update')
        self.label_pcdnum_weakly.setText(idx + '/' + total)
        #self.label_pcdname_weakly.setText('Point Cloud Name:' + self.sources_weakly[int(idx) - 1].pcd_name)
        #self.label_pointnum_weakly.setText('Points Num:' + str(self.sources_weakly[int(idx) - 1].points_num))
        self.text_change_weakly(self.sources_weakly[int(idx) - 1])




    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)

        self.pushButton_dataset_select.clicked.connect(self.dataset_select)
        self.pushButton_datasetweakly_select.clicked.connect(self.dataset_select_weakly)
        self.pushButton_backbone1_select.clicked.connect(self.backbone_select_1)
        self.pushButton_backbone2_select.clicked.connect(self.backbone_select_2)

        self.pushButton_previous_weakly.clicked.connect(self.previous_weakly)
        self.pushButton_next_weakly.clicked.connect(self.next_weakly)
        self.pushButton_previous.clicked.connect(self.previous)
        self.pushButton_next.clicked.connect(self.next)

        self.pushButton_loading_weakly.clicked.connect(self.loading_weakly)
        self.pushButton_loading.clicked.connect(self.loading)

        self.pushButton_previous.setEnabled(False)
        self.pushButton_next.setEnabled(False)
        self.pushButton_next_weakly.setEnabled(False)
        self.pushButton_previous_weakly.setEnabled(False)
        self.pushButton_colorsetting.setEnabled(False)
        self.pushButton_colorsetting_weakly.setEnabled(False)
        self.pushButton_backbone1_select.setEnabled(False)
        self.pushButton_backbone2_select.setEnabled(False)
        self.pushButton_loading.setEnabled(False)
        self.pushButton_loading_weakly.setEnabled(False)

        self.sources_weakly=None
        self.sources=None
        self.actor_origin_weakly = None
        self.actor_gt_weakly = None
        self.actor_sup1 = None
        self.actor_sup2 = None
        self.actor_origin =None
        self.actor_sem=None
        self.actor_ins=None
        self.actor_gt=None
        self.load_counts=0
        self.load_weakly_counts=0



        self.frame_origin = QtWidgets.QFrame()
        self.vtkWidget_origin = QVTKRenderWindowInteractor(self.frame_origin)
        self.frame_origin_weakly = QtWidgets.QFrame()
        self.vtkWidget_origin_weakly = QVTKRenderWindowInteractor(self.frame_origin_weakly)

        self.frame_gt = QtWidgets.QFrame()
        self.vtkWidget_gt = QVTKRenderWindowInteractor(self.frame_gt)
        self.frame_gt_weakly = QtWidgets.QFrame()
        self.vtkWidget_gt_weakly = QVTKRenderWindowInteractor(self.frame_gt_weakly)

        self.frame_sem = QtWidgets.QFrame()
        self.vtkWidget_sem = QVTKRenderWindowInteractor(self.frame_sem)
        self.frame_sup1 = QtWidgets.QFrame()
        self.vtkWidget_sup1 = QVTKRenderWindowInteractor(self.frame_sup1)

        self.frame_ins = QtWidgets.QFrame()
        self.vtkWidget_ins = QVTKRenderWindowInteractor(self.frame_ins)
        self.frame_sup2 = QtWidgets.QFrame()
        self.vtkWidget_sup2 = QVTKRenderWindowInteractor(self.frame_sup2)

        self.formLayout_origin.addWidget(self.vtkWidget_origin)
        self.formLayout_gt.addWidget(self.vtkWidget_gt)
        self.formLayout_semseg.addWidget(self.vtkWidget_sem)
        self.formLayout_insseg.addWidget(self.vtkWidget_ins)
        self.formLayout_origin_weakly.addWidget(self.vtkWidget_origin_weakly)
        self.formLayout_gt_weakly.addWidget(self.vtkWidget_gt_weakly)
        self.formLayout_semseg_sup1.addWidget(self.vtkWidget_sup1)
        self.formLayout_semseg_sup2.addWidget(self.vtkWidget_sup2)


        self.ren_origin = vtk.vtkRenderer()
        self.ren_gt = vtk.vtkRenderer()
        self.ren_sem = vtk.vtkRenderer()
        self.ren_ins = vtk.vtkRenderer()
        self.ren_origin_weakly = vtk.vtkRenderer()
        self.ren_gt_weakly = vtk.vtkRenderer()
        self.ren_sup1 = vtk.vtkRenderer()
        self.ren_sup2 = vtk.vtkRenderer()

        self.vtkWidget_origin.GetRenderWindow().AddRenderer(self.ren_origin)
        self.vtkWidget_gt.GetRenderWindow().AddRenderer(self.ren_gt)
        self.vtkWidget_sem.GetRenderWindow().AddRenderer(self.ren_sem)
        self.vtkWidget_ins.GetRenderWindow().AddRenderer(self.ren_ins)
        self.vtkWidget_origin_weakly.GetRenderWindow().AddRenderer(self.ren_origin_weakly)
        self.vtkWidget_gt_weakly.GetRenderWindow().AddRenderer(self.ren_gt_weakly)
        self.vtkWidget_sup1.GetRenderWindow().AddRenderer(self.ren_sup1)
        self.vtkWidget_sup2.GetRenderWindow().AddRenderer(self.ren_sup2)

        self.iren_origin = self.vtkWidget_origin.GetRenderWindow().GetInteractor()
        self.iren_gt = self.vtkWidget_gt.GetRenderWindow().GetInteractor()
        self.iren_sem = self.vtkWidget_sem.GetRenderWindow().GetInteractor()
        self.iren_ins = self.vtkWidget_ins.GetRenderWindow().GetInteractor()
        self.iren_origin_weakly=self.vtkWidget_origin_weakly.GetRenderWindow().GetInteractor()
        self.iren_gt_weakly=self.vtkWidget_gt_weakly.GetRenderWindow().GetInteractor()
        self.iren_sup1=self.vtkWidget_sup1.GetRenderWindow().GetInteractor()
        self.iren_sup2=self.vtkWidget_sup2.GetRenderWindow().GetInteractor()

        #actor_origin=PCD_VTK_ACTOR(datapath='')
        #actor_gt = PCD_VTK_ACTOR(datapath='')
        #actor_sem = PCD_VTK_ACTOR(datapath='')
        #actor_ins = PCD_VTK_ACTOR(datapath='')

        #self.ren_origin.AddActor(actor_origin.pcdactor)
        #source=PcdToVtkSource('STPLS3D\\Synthetic_v3\\1_points_GTv3.ply')
        #actor=PcdToVtkActor(source)
        #actor.setting_color()
        #self.ren_origin.AddActor(actor.actor)
        self.ren_origin.ResetCamera()

        #self.ren_gt.AddActor(actor_gt.pcdactor)
        #actor2=PcdToVtkActor(source)
        #actor2.setting_color(mode='sem')
        #self.ren_gt.AddActor(actor2.actor)
        self.ren_gt.ResetCamera()

        #self.ren_sem.AddActor(actor_sem.pcdactor)
        self.ren_sem.ResetCamera()

        #self.ren_ins.AddActor(actor_ins.pcdactor)
        self.ren_ins.ResetCamera()

        self.show()

        self.iren_origin.Initialize()
        self.iren_gt.Initialize()
        self.iren_sem.Initialize()
        self.iren_ins.Initialize()
        self.iren_origin_weakly.Initialize()
        self.iren_gt_weakly.Initialize()
        self.iren_sup1.Initialize()
        self.iren_sup2.Initialize()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    apply_stylesheet(app, theme='dark_teal.xml')
    window.show()
    sys.exit(app.exec_())



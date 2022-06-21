# PCDGui
点云测试展示软件
# PCDGui
点云测试展示软件(老版代码)
main.py运行后在当前weakly seg标签页下，右上角点击select按钮，选取数据所在文件夹并进入文件夹后再点‘选择文件夹’按钮,测试数据放在
效果为四个窗口加载了一个STPLS3D场景点云
可以加入格式一致的ply点云进行测试 要求有属性x y z r g b class instance


* 默认在windows平台上运行 如需在linux平台上运行 请修改对应路径的代码
* main.py 第54行 注释掉
* pcd_to_vtk.py 第62行 ‘\\’换成'/'
* pcd_thread.py 第35行‘\\’换成'/'
（可能还有其他需要修改）

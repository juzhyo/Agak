# -*- coding: utf-8 -*-
"""
Agaration
A photocurrent mapping program

Giulio Baldi, Henrique Rosa, Ho Yi Wei, Justin Zhou
"""

import sys
import qdarkstyle
import os
import time
import pyvisa
import numpy as np
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import uic
from PyQt5 import QtChart as qtch
from PyQt5 import QtGui as qtg
from collections import deque
import psutil
from pymeasure.instruments.srs import SR830
import matplotlib.pyplot as plt

# sys.path.append(r'E:\Python\Codes\1_main_codes')
# from DAQ_main import *       

MW_Ui, MW_Base = uic.loadUiType('mainwindow.ui')

class MainWindow(MW_Base, MW_Ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # toolbar = self.addToolBar('File')
        # open_action = toolbar.addAction("Open")
        # save_action = toolbar.addAction("Save")
        # run_action = toolbar.addAction("Run")
        
        run_action = self.toolBar.addAction('Run')
        stop_action = self.toolBar.addAction('Stop')
        
        open_icon = self.style().standardIcon(qtw.QStyle.SP_DirOpenIcon)
        save_icon = self.style().standardIcon(qtw.QStyle.SP_DriveHDIcon)
        run_icon = self.style().standardIcon(qtw.QStyle.SP_MediaPlay)
        stop_icon = self.style().standardIcon(qtw.QStyle.SP_MediaStop)
        
        # open_action.setIcon(open_icon)
        # save_action.setIcon(save_icon)
        # run_action.setIcon(run_icon)
        
        run_action.setIcon(run_icon)
        stop_action.setIcon(stop_icon)
        
        # toolbar.setMovable(False)
        # toolbar.setFloatable(False)
        # toolbar.setAllowedAreas(qtc.Qt.TopToolBarArea)
        
        values = qtc.pyqtSignal(float)
        
        resources_list = self.get_resources()
        self.populate_resources(self.equipments_sr830_address, sorted(resources_list,key=self.sort_GPIB))
        self.populate_resources(self.equipments_b2902a_address, sorted(resources_list,key=self.sort_ASRL))
        self.populate_resources(self.equipments_pm100d_address, resources_list)
        self.populate_resources(self.equipments_m2_laser_address, resources_list)
        
        ### Plots ###
        self.max_size = qtc.QSize(300,300)
        self.image = qtg.QImage(self.max_size, qtg.QImage.Format_ARGB32)
        self.image.fill(qtg.QColor('black'))
        self.build_image('./temp/x_map.png')
        self.plots_x.setPixmap(qtg.QPixmap(self.image))
        self.build_image('./temp/y_map.png')
        self.plots_y.setPixmap(qtg.QPixmap(self.image))
        self.build_image('./temp/r_map.png')
        self.plots_r.setPixmap(qtg.QPixmap(self.image))
        self.build_image('./temp/theta_map.png')
        self.plots_theta.setPixmap(qtg.QPixmap(self.image))
              
        self.channel1_view()
        self.channel2_view()
        # channel1_display = channel1_view()
        # self.plots_hbox.addWidget(channel1_display)
        # self.parameters_sr830_channel_display_vbox.addWidget(channel1_display)
        # self.parameters_sr830_channel1_display.addWidget(channel1_display)
        # self.parameters_sr830_channel2_display.addWidget(disk_usage_view)
        
        self.equipments_sr830_connect.clicked.connect(lambda: self.equipments_connect(SR830,self.equipments_sr830_address.currentText()))
        self.equipments_sr830_connect.clicked.connect(lambda: self.equipments_check_status(SR830,self.equipments_sr830_address.currentText(),self.parameters_sr830))
        
        self.parameters_sr830_time_constant.currentIndexChanged.connect(lambda: self.set_sr830_parameters(self.equipments_sr830_address.currentText(),'time_constant'))
        self.parameters_sr830_filter_slope.currentIndexChanged.connect(lambda: self.set_sr830_parameters(self.equipments_sr830_address.currentText(),'filter_slope'))
        self.parameters_sr830_input_config.currentIndexChanged.connect(lambda: self.set_sr830_parameters(self.equipments_sr830_address.currentText(),'input_config'))
        self.parameters_sr830_frequency.valueChanged.connect(lambda: self.set_sr830_parameters(self.equipments_sr830_address.currentText(),'frequency'))
        self.parameters_sr830_input_coupling_ac.clicked.connect(lambda: self.set_sr830_parameters(self.equipments_sr830_address.currentText(),'input_coupling'))
        self.parameters_sr830_input_coupling_dc.clicked.connect(lambda: self.set_sr830_parameters(self.equipments_sr830_address.currentText(),'input_coupling'))
        self.parameters_sr830_input_grounding_float.clicked.connect(lambda: self.set_sr830_parameters(self.equipments_sr830_address.currentText(),'input_grounding'))
        self.parameters_sr830_input_grounding_ground.clicked.connect(lambda: self.set_sr830_parameters(self.equipments_sr830_address.currentText(),'input_grounding'))
        self.parameters_sr830_sensitivity.currentIndexChanged.connect(lambda: self.set_sr830_parameters(self.equipments_sr830_address.currentText(),'sensitivity'))
        self.parameters_sr830_channel1.currentIndexChanged.connect(lambda: self.set_sr830_parameters(self.equipments_sr830_address.currentText(),'channel1'))
        self.parameters_sr830_channel2.currentIndexChanged.connect(lambda: self.set_sr830_parameters(self.equipments_sr830_address.currentText(),'channel2'))
        
        run_action.setCheckable(True)
        
        # self.parameters_sr830_signal_input_ac.clicked.connect(lambda: self.button_toggle(self.parameters_sr830_signal_input_ac,[self.parameters_sr830_signal_input_ac]))
        
        run_action.changed.connect(lambda: self.run(run_action))
        while run_action.isChecked() == True:
            self.log_box.append('Measuring...')
            time.sleep(1)
            
        # print(self.get_to_set_sr830_parameters())
    
        
        self.show()
        
    def get_resources(self):
        return pyvisa.ResourceManager().list_resources()
    
    def sort_GPIB(self, value):
        return value[0:4] != 'GPIB'
    
    def sort_ASRL(self, value):
        return value[0:4] != 'ASRL'
        

    def populate_resources(self, combobox, resources_list):
        """Populate a combobox with available resource addresses"""
    
        for i in range(len(resources_list)):
            combobox.addItem(resources_list[i],i)
            
    def equipments_connect(self, instrument, resource_name):
        return instrument(resource_name)
    
    def equipments_check_status(self, instrument, resource_name, parameters_box):
        try:
            instrument(resource_name).id
            parameters_box.setEnabled(True)
            
            if instrument == SR830:
                self.parameters_sr830_input_coupling_ac.setEnabled(True)
                self.sr830 = instrument(resource_name)

            
        except:
            self.log_box.append('<span style="color:lightcoral">[ERROR] Equipment connection failed<\span>')
            parameters_box.setDisabled(True)
            return
            
        self.log_box.append('<span style="color:palegreen">[SUCCESS] Equipment connected</span>')
        
    def equipments_refresh_clicked(self):
        resources_list = self.get_resources()
        self.populate_resources(self.equipments_sr830_address, resources_list)
        
    def button_toggle(self, button, button_list):
        if button.isChecked() == False:
            button.setChecked(True)
            
            for i in range(len(button_list)):
                i.setChecked(False)
        else:
            pass
        
    # parameters_galvo = 
        
    def run(self,run_action,parameters_sr830=[],parameters_galvo=[]):
        if run_action.isChecked() == True:
            
            self.parameters_galvo = {'step': self.parameters_galvo_step_value.value(),
                                     'x_max': float(self.parameters_galvo_x_max.text()),
                                     'x_min': float(self.parameters_galvo_x_min.text()),
                                     'y_max': float(self.parameters_galvo_y_max.text()),
                                     'y_min': float(self.parameters_galvo_y_min.text())}
            
            plots = {'x':self.plots_x,
                     'y':self.plots_y,
                     'r':self.plots_r,
                     'theta':self.plots_theta}
            
            if self.parameters_sr830.isEnabled() == True:
                
                
                self.mapper = Mapper()
                self.mapper_thread = qtc.QThread()
                self.mapper.moveToThread(self.mapper_thread)
                self.mapper.mapping_finished.connect(self.mapper_thread.quit)
                #mapper_thread.started.connect(lambda: mapper.set_sr830(self.sr830))
                #mapper_thread.started.connect(lambda: mapper.set_sr830(self.parameters_galvo))
                #mapper_thread.started.connect(lambda: mapper.do_mapping())
                #mapper_thread.started.connect(lambda: mapper.print_sr830())
                # mapper_thread.started.connect(lambda: mapper.set_parameters_galvo(parameters_galvo))
                # mapper_thread.started.connect(lambda: mapper.set_plots(plots))
                # mapper_thread.started.connect(lambda: mapper.do_mapping())
                self.mapper_thread.start()
                self.mapper.set_sr830(self.sr830)
                self.mapper.set_parameters_galvo(self.parameters_galvo)
                # self.mapper.set_plots(plots)
                # self.mapper.moved.connect(form.addResult)
                self.mapper_thread.started.connect(self.mapper.do_mapping)
                self.mapper.mapping_started.connect(lambda: self.log_box.append('[MEASUREMENT] Starting...'))
                self.mapper.mapping_finished.connect(lambda: self.log_box.append('<span style="color:palegreen">[MEASUREMENT] Complete</span>'))
                self.mapper.mapping_moved.connect(self.refresh_plots)
                
                self.mapper.mapping_finished.connect(lambda: run_action.setChecked(False))
                
                # scan_step = self.parameters_galvo_step_value.value()
                # n_x_steps = int((float(self.parameters_galvo_x_max.text()) - float(self.parameters_galvo_x_min.text()))/scan_step) + 1
                # n_y_steps = int((float(self.parameters_galvo_y_max.text()) - float(self.parameters_galvo_y_min.text()))/scan_step) + 1
   
                # x_map = np.zeros([n_x_steps*n_y_steps,3])
                # y_map = np.zeros([n_x_steps*n_y_steps,3])
                # r_map = np.zeros([n_x_steps*n_y_steps,3])
                # theta_map = np.zeros([n_x_steps*n_y_steps,3])
                
                # for i in range(n_x_steps):
                #     x_position = float(self.parameters_galvo_x_min.text()) + i*scan_step
                #     # set_X_mirror(x_position)
                    
                #     for j in range(n_y_steps): 
                #         y_position = float(self.parameters_galvo_y_min.text()) + j*scan_step
                #         # set_Y_mirror(y_position)
                #         # print([x_position,y_position])
                #         x_map[i*n_y_steps+j] = [x_position, y_position, self.sr830.x]
                #         y_map[i*n_y_steps+j] = [x_position, y_position, self.sr830.y]
                #         r_map[i*n_y_steps+j] = [x_position, y_position, self.sr830.magnitude]
                #         theta_map[i*n_y_steps+j] = [x_position, y_position, self.sr830.theta]
                        
                #         np.savetxt('./x_map_temp.txt',x_map)
                #         np.savetxt('./y_map_temp.txt',y_map)
                #         np.savetxt('./r_map_temp.txt',r_map)
                #         np.savetxt('./theta_map_temp.txt',theta_map)
                        
                #         self.generate_display_image(x_map, n_x_steps, n_y_steps, './temp/x_map.png')
                #         self.generate_display_image(y_map, n_x_steps, n_y_steps, './temp/y_map.png')
                #         self.generate_display_image(r_map, n_x_steps, n_y_steps, './temp/r_map.png')
                #         self.generate_display_image(theta_map, n_x_steps, n_y_steps, './temp/theta_map.png')
                        
                #         self.build_image('./temp/x_map.png')
                #         self.plots_x.setPixmap(qtg.QPixmap(self.image))
                #         self.build_image('./temp/y_map.png')
                #         self.plots_y.setPixmap(qtg.QPixmap(self.image))
                #         self.build_image('./temp/r_map.png')
                #         self.plots_r.setPixmap(qtg.QPixmap(self.image))
                #         self.build_image('./temp/theta_map.png')
                #         self.plots_theta.setPixmap(qtg.QPixmap(self.image))
                
                # np.savetxt('x_map.txt',x_map)
                # np.savetxt('y_map.txt',y_map)
                # np.savetxt('r_map.txt',r_map)
                # np.savetxt('theta_map.txt',theta_map)
                
                
                
                
            else:
                self.log_box.append('<span style="color:lightcoral">[ERROR] SR830 not connected<\span>')
                run_action.setChecked(False)
             
        else:
            pass
        
    def get_to_set_sr830_parameters(self):
        time_constant = [30000,10000,3000,1000,300,100,30,10,3,1,0.3,0.1,0.03,0.01,0.003,0.001,0.0003,0.0001,0.00003,0.00001]
        filter_slope = [24,16,12,6]
        input_config = ['A','A - B','I (1 MOhm)', 'I (100 MOhm)']
        input_coupling = ['AC','DC']
        input_grounding = ['Float','Ground']
        input_notch_config = ['None', 'Line', '2 x Line', 'Both']
        sensitivity = [1,5e-1,2e-1,1e-1,5e-2,2e-2,1e-2,5e-3,2e-3,1e-3,5e-4,2e-4,1e-4,5e-5,2e-5,1e-5,5e-6,2e-6,1e-6,5e-7,2e-7,1e-7,5e-8,2e-8,1e-8,5e-9,2e-9,1e-9]
        channel1 = ['X', 'R', 'X Noise', 'Aux In 1', 'Aux In 2']
        channel2 = ['Y', 'Theta', 'Y Noise', 'Aux In 3', 'Aux In 4']                
        
        return {'time_constant':time_constant[self.parameters_sr830_time_constant.currentIndex()],
                'filter_slope':filter_slope[self.parameters_sr830_filter_slope.currentIndex()],
                'input_config':input_config[self.parameters_sr830_input_config.currentIndex()],
                'frequency':self.parameters_sr830_frequency.value(),
                'input_coupling':input_coupling[self.parameters_sr830_input_coupling_dc.isChecked()],
                'input_grounding':input_grounding[self.parameters_sr830_input_grounding_ground.isChecked()],
                'sensitivity':sensitivity[self.parameters_sr830_sensitivity.currentIndex()],
                'channel1':channel1[self.parameters_sr830_channel1.currentIndex()],
                'channel2':channel2[self.parameters_sr830_channel2.currentIndex()]}
    
    def get_current_sr830_parameters(self,resource_name):
        return {'time_constant':SR830(resource_name).time_constant,
                'filter_slope':SR830(resource_name).filter_slope,
                'input_config':SR830(resource_name).input_config,
                'frequency':SR830(resource_name).frequency,
                'input_coupling':SR830(resource_name).input_coupling,
                'input_grounding':SR830(resource_name).input_grounding,
                'sensitivity':SR830(resource_name).sensitivity,
                'channel1':SR830(resource_name).channel1,
                'channel2':SR830(resource_name).channel2}

    def sr830_parameters_changed(self,resource_name):
        return self.get_to_set_sr830_parameters() != self.get_current_sr830_parameters(resource_name)
    
    def set_sr830_parameters(self,resource_name,parameter='all'):
        to_set_parameters = self.get_to_set_sr830_parameters()
        
        if parameter=='all':
            current_parameters = self.get_current_sr830_parameters(resource_name)
        
            parameter_names = ['time_constant',
                               'filter_slope',
                               'input_config',
                               'frequency',
                               'input_coupling',
                               'input_grounding',
                               'sensitivity',
                               'channel1',
                               'channel2']
            
            for i in range(len(to_set_parameters)):
                parameter_name = parameter_names[i]
                if to_set_parameters[parameter_name] != current_parameters[parameter_name]:
                    if isinstance(to_set_parameters[parameter_name],str) == True:
                        exec('SR830("' + resource_name + '").' + parameter_name + '= "' + to_set_parameters[parameter_name] + '"')
                    else:
                        exec('SR830("' + resource_name + '").' + parameter_name + '=' + str(to_set_parameters[parameter_name]))
            
                else:
                    pass
        else:
            parameter_name = parameter
            if isinstance(to_set_parameters[parameter_name],str) == True:
                exec('SR830("' + resource_name + '").' + parameter_name + '= "' + to_set_parameters[parameter_name] + '"')
            else:
                exec('SR830("' + resource_name + '").' + parameter_name + '=' + str(to_set_parameters[parameter_name]))
                
        return
    
    def channel1_view(self):
        num_data_points = 80
        
        self.channel1_chart = qtch.QChart()
        self.channel1_chart.setMargins(qtc.QMargins(0,-25,0,0))
        self.channel1_chart.setTheme(qtch.QChart.ChartThemeLight)
        self.channel1_chart.setBackgroundVisible(False)
        self.channel1_chart.setBackgroundRoundness(0)
        self.channel1_chart.layout().setContentsMargins(0,0,0,0)
        self.parameters_sr830_channel1_display.setChart(self.channel1_chart)
        
        # self.series = qtch.QSplineSeries(name="Channel 1")
        self.channel1_series = qtch.QLineSeries()
        self.channel1_chart.addSeries(self.channel1_series)
        
        self.channel1_data = deque([0] * num_data_points, maxlen=num_data_points)
        self.channel1_series.append([qtc.QPointF(x, y) for x, y in enumerate(self.channel1_data)])
        
        x_axis = qtch.QValueAxis()
        x_axis.setRange(0, num_data_points)
        x_axis.setLabelsVisible(False)
        y_axis = qtch.QValueAxis()
        gridColor = qtg.QColor('#696969')
        x_axis.setGridLineColor(gridColor)
        y_axis.setGridLineColor(gridColor)

        y_axis.setRange(-1e-5, 1e-5)
        self.channel1_chart.setAxisX(x_axis, self.channel1_series)
        self.channel1_chart.setAxisY(y_axis, self.channel1_series)
        
        self.channel1_timer = qtc.QTimer(interval=500, timeout=self.refresh_channel1_stats)
        self.channel1_timer.start()
        
    def channel2_view(self):
        num_data_points = 80
        
        self.channel2_chart = qtch.QChart()
        self.channel2_chart.setMargins(qtc.QMargins(0,-25,0,0))
        self.channel2_chart.setTheme(qtch.QChart.ChartThemeLight)
        self.channel2_chart.setBackgroundVisible(False)
        self.channel2_chart.setBackgroundRoundness(0)
        self.channel2_chart.layout().setContentsMargins(0,0,0,0)
        self.parameters_sr830_channel2_display.setChart(self.channel2_chart)
        
        # self.series = qtch.QSplineSeries(name="Channel 1")
        self.channel2_series = qtch.QLineSeries()
        self.channel2_chart.addSeries(self.channel2_series)
        
        self.channel2_data = deque([0] * num_data_points, maxlen=num_data_points)
        self.channel2_series.append([qtc.QPointF(x, y) for x, y in enumerate(self.channel2_data)])
        
        x_axis = qtch.QValueAxis()
        x_axis.setRange(0, num_data_points)
        x_axis.setLabelsVisible(False)
        y_axis = qtch.QValueAxis()
        gridColor = qtg.QColor('#696969')
        x_axis.setGridLineColor(gridColor)
        y_axis.setGridLineColor(gridColor)
        y_axis.setRange(-1e-5, 1e-5)
        
        self.channel2_chart.setAxisX(x_axis, self.channel2_series)
        self.channel2_chart.setAxisY(y_axis, self.channel2_series)
        
        self.channel2_timer = qtc.QTimer(interval=500, timeout=self.refresh_channel2_stats)
        self.channel2_timer.start()
        # chart = qtch.QChart()
        # chart.setMargins(qtc.QMargins(0,-25,0,0))
        # chart.setTheme(qtch.QChart.ChartThemeLight)
        # chart.setBackgroundVisible(False)
        # chart.setBackgroundRoundness(0)
        # chart.layout().setContentsMargins(0,0,0,0)
        # self.parameters_sr830_channel2_display.setChart(chart)
        
        # # self.series = qtch.QSplineSeries(name="Channel 1")
        # self.series = qtch.QSplineSeries()
        # chart.addSeries(self.series)
        
        # self.data = deque([0] * num_data_points, maxlen=num_data_points)
        # self.series.append([qtc.QPoint(x, y) for x, y in enumerate(self.data)])
        
        # x_axis = qtch.QValueAxis()
        # x_axis.setRange(0, num_data_points)
        # x_axis.setLabelsVisible(False)
        # y_axis = qtch.QValueAxis()
        # y_axis.setRange(0, 100)
        # chart.setAxisX(x_axis, self.series)
        # chart.setAxisY(y_axis, self.series)
        
        # self.timer = qtc.QTimer(interval=200, timeout=self.refresh_stats)
        # self.timer.start()
        

    def build_image(self, filename):
        if False:
        # if not data.get('ímage_source'):
            self.image.fill(qtg.QColor('black'))
        else:
            self.image.load(filename)
            # if not (self.max_size - self.image.size()).isValid():
            #     self.image = self.image.scaled(self.max_size, qtc.Qt.KeepAspectRatio)
            
    def generate_display_image(self, data, nrows, ncols, filename, title):
        fig = plt.figure()
        
        title_obj = plt.title(title)
        plt.setp(title_obj, color='white') 
        
        ax = fig.add_subplot(111)
        ax.set_xlabel('X (V)')
        ax.set_ylabel('Y (V)')
        
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        # ax.xaxis.ticklabels.set_color('white')
        # ax.yaxis.ticklabels.set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        
        x, y, temp = data.T
        grid = temp.reshape((nrows,ncols))
        map = ax.imshow(grid, extent=[x.min(),x.max(),y.min(),y.max()], interpolation='nearest')
        cbar = fig.colorbar(map)
        cbar_yticklabel = plt.getp(cbar.ax.axes,'yticklabels')
        plt.setp(cbar_yticklabel, color='white')
        plt.savefig(filename,bbox_inches='tight',transparent=True)
        plt.close()         
        
    def refresh_channel1_stats(self):
        if self.parameters_sr830.isEnabled():
            self.channel1_data.append(self.sr830.x)
            
            y_axis = qtch.QValueAxis()
            axisBrush = qtg.QBrush(qtg.QColor('#ffffff'))
            y_axis.setLabelsBrush(axisBrush)
            gridColor = qtg.QColor('#696969')
            # x_axis.setGridLineColor(gridColor)
            y_axis.setGridLineColor(gridColor)
            
            if self.sr830.channel1 == [0.0, 0.0]:
                self.channel2_data.append(self.sr830.x)
                y_axis.setRange(-self.sr830.sensitivity, self.sr830.sensitivity)
            elif self.sr830.channel1 == [1.0, 0.0]:
                self.channel1_data.append(self.sr830.magnitude)
                y_axis.setRange(-self.sr830.sensitivity, self.sr830.sensitivity)  
            
            self.channel1_chart.setAxisY(y_axis, self.channel1_series)
        
            new_data = [qtc.QPointF(x, y) for x, y in enumerate(self.channel1_data)]
            self.channel1_series.replace(new_data)
            
    def refresh_channel2_stats(self):
        # usage = psutil.cpu_percent()
        # self.data.append(usage)
        
        # new_data = [qtc.QPoint(x, y) for x, y in enumerate(self.data)]
        # self.series.replace(new_data)
        
        if self.parameters_sr830.isEnabled():            
            
            y_axis = qtch.QValueAxis()
            axisBrush = qtg.QBrush(qtg.QColor('#ffffff'))
            y_axis.setLabelsBrush(axisBrush)
            gridColor = qtg.QColor('#696969')
            # x_axis.setGridLineColor(gridColor)
            y_axis.setGridLineColor(gridColor)
        
            if self.sr830.channel2 == [0.0, 0.0]:
                self.channel2_data.append(self.sr830.y)
                y_axis.setRange(-self.sr830.sensitivity, self.sr830.sensitivity)
            elif self.sr830.channel2 == [1.0, 0.0]:
                self.channel2_data.append(self.sr830.theta)
                y_axis.setRange(-180, 180)
                
            self.channel2_chart.setAxisY(y_axis, self.channel2_series)
        
            new_data = [qtc.QPointF(x, y) for x, y in enumerate(self.channel2_data)]
            self.channel2_series.replace(new_data)
            
    def refresh_plots(self):
        # map_dim = np.loadtxt('./map_dimension.txt')
        # n_x = int(map_dim[0])
        # n_y = int(map_dim[1])
        
        # x_map = np.loadtxt('./x_map_temp.txt')
        # y_map = np.loadtxt('./y_map_temp.txt')
        # r_map = np.loadtxt('./r_map_temp.txt')
        # theta_map = np.loadtxt('./theta_map_temp.txt')
        
        # self.generate_display_image(x_map, n_x, n_y, './temp/x_map.png', 'X')
        # self.generate_display_image(y_map, n_x, n_y, './temp/y_map.png', 'Y')
        # self.generate_display_image(r_map, n_x, n_y, './temp/r_map.png', 'R')
        # self.generate_display_image(theta_map, n_x, n_y, './temp/theta_map.png', r'$\theta$')
                
        self.build_image('./temp/x_map.png')
        self.plots_x.setPixmap(qtg.QPixmap(self.image))
        self.build_image('./temp/y_map.png')
        self.plots_y.setPixmap(qtg.QPixmap(self.image))
        self.build_image('./temp/r_map.png')
        self.plots_r.setPixmap(qtg.QPixmap(self.image))
        self.build_image('./temp/theta_map.png')
        self.plots_theta.setPixmap(qtg.QPixmap(self.image))
                   
    
    # def get_to_set_galvo_parameters(self):
        
        
        
    # def get_current_galvo_parameters(self,resource_name):
        
        
        
    # def set_galvo_parameters(self,resource_name):
        
class Mapper(qtc.QObject):
    
    mapping_started = qtc.pyqtSignal()
    mapping_moved = qtc.pyqtSignal()
    mapping_finished = qtc.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.parameters_galvo = None
        self.sr830 = None
        
    @qtc.pyqtSlot(str)    
    def set_sr830(self, sr830):
        self.sr830 = sr830
        
    # def print_sr830(self):
    #     print(self.sr830)
    
    @qtc.pyqtSlot(str)    
    def set_parameters_galvo(self, parameters_galvo):
        self.parameters_galvo = parameters_galvo
        
    # def set_plots(self,plots):
    #     self.plots = plots

    @qtc.pyqtSlot()        
    def do_mapping(self):
        self.mapping_started.emit()
        
        self.max_size = qtc.QSize(300,300)
        self.image = qtg.QImage(self.max_size, qtg.QImage.Format_ARGB32)
        self.image.fill(qtg.QColor('black'))
        
        step = self.parameters_galvo['step']
        n_x = int((self.parameters_galvo['x_max'] - self.parameters_galvo['x_min'])/step) + 1
        n_y = int((self.parameters_galvo['y_max'] - self.parameters_galvo['y_min'])/step) + 1
        
        np.savetxt('./map_dimension.txt',np.array([n_x,n_y]))
   
        x_map = np.zeros([n_x*n_y,3])
        y_map = np.zeros([n_x*n_y,3])
        r_map = np.zeros([n_x*n_y,3])
        theta_map = np.zeros([n_x*n_y,3])
        
        for i in range(n_x):
            x_position = self.parameters_galvo['x_min'] + i*step
            
            for j in range(n_y):
                y_position = self.parameters_galvo['y_min'] + j*step
                
                x_map[i*n_y+j] = [x_position, y_position, 0]
                y_map[i*n_y+j] = [x_position, y_position, 0]
                r_map[i*n_y+j] = [x_position, y_position, 0]
                theta_map[i*n_y+j] = [x_position, y_position, 0]
                
                
        for i in range(n_x):
            x_position = self.parameters_galvo['x_min'] + i*step
            # set_X_mirror(x_position)
                    
            for j in range(n_y): 
                y_position = self.parameters_galvo['y_min'] + j*step
                # set_Y_mirror(y_position)
                # print([x_position,y_position])
                x_map[i*n_y+j] = [x_position, y_position, self.sr830.x]
                y_map[i*n_y+j] = [x_position, y_position, self.sr830.y]
                r_map[i*n_y+j] = [x_position, y_position, self.sr830.magnitude]
                theta_map[i*n_y+j] = [x_position, y_position, self.sr830.theta]
                        
                np.savetxt('./temp/x_map_temp.txt',x_map)
                np.savetxt('./temp/y_map_temp.txt',y_map)
                np.savetxt('./temp/r_map_temp.txt',r_map)
                np.savetxt('./temp/theta_map_temp.txt',theta_map)
               
                self.generate_display_image(x_map, n_x, n_y, './temp/x_map.png', 'X')
                self.generate_display_image(y_map, n_x, n_y, './temp/y_map.png', 'Y')
                self.generate_display_image(r_map, n_x, n_y, './temp/r_map.png', 'R')
                self.generate_display_image(theta_map, n_x, n_y, './temp/theta_map.png', r'$\theta$')
                    
                self.mapping_moved.emit()
                    
                # self.build_image('./temp/x_map.png')
                # self.plots['x'].setPixmap(qtg.QPixmap(self.image))
                # self.build_image('./temp/y_map.png')
                # self.plots['y'].setPixmap(qtg.QPixmap(self.image))
                # self.build_image('./temp/r_map.png')
                # self.plots['r'].setPixmap(qtg.QPixmap(self.image))
                # self.build_image('./temp/theta_map.png')
                # self.plots['theta'].setPixmap(qtg.QPixmap(self.image))
                
        np.savetxt('x_map.txt',x_map)
        np.savetxt('y_map.txt',y_map)
        np.savetxt('r_map.txt',r_map)
        np.savetxt('theta_map.txt',theta_map)
            
        self.mapping_finished.emit()
        
    # def build_image(self, filename):
    #     if False:
    #     # if not data.get('ímage_source'):
    #         self.image.fill(qtg.QColor('black'))
    #     else:
    #         self.image.load(filename)
    #         # if not (self.max_size - self.image.size()).isValid():
    #         #     self.image = self.image.scaled(self.max_size, qtc.Qt.KeepAspectRatio)
            
    def generate_display_image(self, data, nrows, ncols, filename, title):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        title_obj = plt.title(title)
        plt.setp(title_obj, color='white') 
        
        ax.set_xlabel('X (V)')
        ax.set_ylabel('Y (V)')
        
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        # ax.xaxis.ticklabels.set_color('white')
        # ax.yaxis.ticklabels.set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        
        x, y, temp = data.T
        grid = temp.reshape((nrows,ncols))
        map = ax.imshow(grid, extent=[x.min(),x.max(),y.min(),y.max()], interpolation='nearest')
        cbar = fig.colorbar(map)
        cbar_yticklabel = plt.getp(cbar.ax.axes,'yticklabels')
        plt.setp(cbar_yticklabel, color='white')
        plt.savefig(filename,bbox_inches='tight',transparent=True)
        plt.close()
        
class galvo_preview(qtc.QObject):
    
    def __init__(self):
        super().__init__()
    
    def set_sr830(self, sr830):
        self.sr830 = sr830
    
                
# class channel1_view(qtch.QChartView):    
#     num_data_points = 100
    
#     def __init__(self):
#         super().__init__()
#         chart = qtch.QChart()
#         chart.setMargins(qtc.QMargins(0,-50,0,0))
#         chart.setTheme(qtch.QChart.ChartThemeLight)
#         chart.setBackgroundVisible(False)
#         chart.setBackgroundRoundness(0)
#         chart.layout().setContentsMargins(0,0,0,0)
#         self.setChart(chart)
        
#         # self.series = qtch.QSplineSeries(name="Channel 1")
#         self.series = qtch.QSplineSeries()
#         chart.addSeries(self.series)
        
#         self.data = deque([0] * self.num_data_points, maxlen=self.num_data_points)
#         self.series.append([qtc.QPoint(x, y) for x, y in enumerate(self.data)])
        
#         x_axis = qtch.QValueAxis()
#         x_axis.setRange(0, self.num_data_points)
#         x_axis.setLabelsVisible(False)
#         y_axis = qtch.QValueAxis()
#         y_axis.setRange(0, 100)
#         chart.setAxisX(x_axis, self.series)
#         chart.setAxisY(y_axis, self.series)
        
#         # self.setRenderHint(qtg.QPainter.Antialiasing)
        
#         self.timer = qtc.QTimer(interval=200, timeout=self.refresh_stats)
#         self.timer.start()
        
#     def refresh_stats(self):
#         usage = psutil.cpu_percent()
#         self.data.append(usage)
        
#         new_data = [qtc.QPoint(x, y) for x, y in enumerate(self.data)]
#         self.series.replace(new_data)
        
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    mv = MainWindow()
    sys.exit(app.exec())   

# from pymeasure.instruments.srs import SR830

# # To check available resources
# # >>> import pyvisa
# # >>> rm = pyvisa.ResourceManager()
# # >>> print(rm.list_resources())

# lockinamp = SR830("GPIB0::8::INSTR")

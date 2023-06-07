import sys
import os
import platform
import re
import shutil
import dearpygui.dearpygui as dpg

#参量初始化
FONT = "ArialUnicode.ttf"
ICON = "appicon.ico"
PLATFORM = platform.system()

if getattr(sys, "frozen", False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(bundle_dir, FONT)
ICON = os.path.join(bundle_dir, ICON)

JPEG_folder = ""
RAW_folder = ""
tRAW_folder = ""

JPEG_folder_status = 0 #0:未编辑 1:正在选择 2:已选择(文件夹) 3:已选择(文件)
RAW_folder_status = 0
tRAW_folder_status = 0

JPEG_file_name_list = []
RAW_file_name_list = []
jpeg_folder_files = []

#功能模块

def update_table():
    global JPEG_folder,RAW_folder,tRAW_folder
    global JPEG_folder_status,RAW_folder_status,tRAW_folder_status
    global JPEG_file_name_list,jpeg_folder_files
    global RAW_file_name_list

    for file in jpeg_folder_files:
        if dpg.does_item_exist(file):
            dpg.delete_item(file)
    targetSameFileNum = 0
    rawDidNotFound = 0
    #选择JPEG前提
    if JPEG_folder_status == 2:
        jpeg_folder_files = os.listdir(JPEG_folder)
        JPEG_file_name_list = []
        RAW_file_name_list = []
        raw_folder_files = []
        traw_folder_files = []

        #print(jpeg_folder_files)
        re_jpeg_file = re.compile(".*.(jpg|jpeg)", flags=re.I)
        re_jpeg_only = re.compile(".(jpg|jpeg)", flags=re.I)

        if RAW_folder_status == 2:
            raw_folder_files = os.listdir(RAW_folder)

        if tRAW_folder_status == 2:
            traw_folder_files = os.listdir(tRAW_folder)
        #遍历寻找jpeg信息
        for file in jpeg_folder_files:
            #存在jpeg
            if re.match(re_jpeg_file, file):
                #JPEG_file_list.append(file)
                with dpg.table_row(parent="info_table", tag=file):
                    #文件名称(不含后缀)
                    fileName = re.sub(re_jpeg_only, '', file)
                    JPEG_file_name_list.append(fileName)
                    #查找目标重名文件
                    if tRAW_folder_status == 2:
                        re_same_filename = re.compile(str(fileName+'.*'))
                        found = False
                        for trawFile in traw_folder_files:
                            if re.match(re_same_filename, trawFile):
                                found = True
                        if found:
                            dpg.add_text('Has same file!')
                            targetSameFileNum = targetSameFileNum+1
                        else:
                            dpg.add_text('Ready.')
                    else:
                        dpg.add_text('No folder.')
                    #查找RAW文件
                    if RAW_folder_status == 2:
                        re_raw_same_filename = re.compile(str(fileName+'.*'))
                        found = False
                        foundFileCount = 0
                        rawFileName = ""
                        for rawFile in raw_folder_files:
                            matchResult = re.match(re_raw_same_filename, rawFile)
                            #print(matchResult)
                            if matchResult:
                                found = True
                                rawFileName = str(matchResult.group(0))
                                #print(matchResult)
                        if found:
                            RAW_file_name_list.append(rawFileName)
                            dpg.add_text(rawFileName)
                        else:
                            dpg.add_text('Not Found.')
                            rawDidNotFound = rawDidNotFound+1
                    else:
                        dpg.add_text('No folder.')
                    
                    dpg.add_text(fileName)

        if targetSameFileNum != 0:
            dpg.configure_item('table_status', label="Status("+str(targetSameFileNum)+" same files)")
        else:
            dpg.configure_item('table_status', label="Status")
        if rawDidNotFound != 0:
            dpg.configure_item('table_rawfiles', label="RAW Files("+str(rawDidNotFound)+" files not found.)")
        else:
            dpg.configure_item('table_rawfiles', label="RAW Files")

def callback(sender, app_data):
    print('OK was clicked.')
    print("Sender: ", sender)
    print("App Data: ", app_data)
    global JPEG_folder_status,RAW_folder_status,tRAW_folder_status,JPEG_folder,RAW_folder,tRAW_folder
    if JPEG_folder_status == 1:
        dpg.configure_item("JPEG_folder_path", default_value=app_data['current_path'])
        JPEG_folder = app_data['current_path']
        JPEG_folder_status = 2

    elif RAW_folder_status == 1:
        dpg.configure_item("RAW_folder_path", default_value=app_data['current_path'])
        RAW_folder = app_data['current_path']
        RAW_folder_status = 2

    elif tRAW_folder_status == 1:
        dpg.configure_item("tRAW_folder_path", default_value=app_data['current_path'])
        tRAW_folder = app_data['current_path']
        tRAW_folder_status = 2
        traw_folder_files = os.listdir(tRAW_folder)
        print(traw_folder_files)
        if len(traw_folder_files) != 0:
            dpg.configure_item("tRAWfolder_has_file", show=True)

    update_table()

def cancel_callback(sender, app_data):
    print('Cancel was clicked.')
    print("Sender: ", sender)
    print("App Data: ", app_data)

def JpegSelectCallback(sender, app_data):
    global JPEG_folder_status
    JPEG_folder_status = 1
    dpg.show_item("file_dialog_id")

def RawSelectCallback(sender, app_data):
    global RAW_folder_status
    RAW_folder_status = 1
    dpg.show_item("file_dialog_id")

def tRawSelectCallback(sender, app_data):
    global tRAW_folder_status
    tRAW_folder_status = 1
    dpg.show_item("file_dialog_id")

def showProceedWindow(sender, app_data):
    global JPEG_folder_status,RAW_folder_status,tRAW_folder_status
    if JPEG_folder_status != 2:
        dpg.configure_item('proceed_message', default_value='Please select JPEG folder.')
        dpg.configure_item('proceed_confirm', show=False)
        dpg.configure_item('proceed_cancel', label='OK')
    elif RAW_folder_status != 2:
        dpg.configure_item('proceed_message', default_value='Please select RAW folder.')
        dpg.configure_item('proceed_confirm', show=False)
        dpg.configure_item('proceed_cancel', label='OK')
    elif tRAW_folder_status != 2:
        dpg.configure_item('proceed_message', default_value='Please select target RAW folder.')
        dpg.configure_item('proceed_confirm', show=False)
        dpg.configure_item('proceed_cancel', label='OK')
    else:
        pass
    dpg.show_item("proceed")

def confirmProceedData(sender, app_data):
    dpg.configure_item('proceed_sep', show=True)
    dpg.configure_item('proceed_progress', show=True)
    dpg.configure_item('proceed_currentfile', show=True)
    global JPEG_folder,RAW_folder,tRAW_folder
    global RAW_file_name_list
    global PLATFORM
    fileCount = len(RAW_file_name_list)
    proceedFile = 0
    for name in RAW_file_name_list:
        shutil.copyfile(os.path.join(RAW_folder,name), os.path.join(tRAW_folder,name))
        proceedFile = proceedFile+1
        dpg.configure_item('proceed_currentfile', default_value='('+str(proceedFile)+'/'+str(fileCount)+') Copy '+name)
        currentProgress = proceedFile/fileCount
        dpg.configure_item('proceed_progress', default_value=currentProgress)
    
    dpg.configure_item('proceed_message', default_value='Raw file has been successfully copied.')
    dpg.configure_item('proceed_confirm', show=False)
    dpg.configure_item('proceed_cancel', label='OK')

    update_table()

#UI初始化
dpg.create_context()

with dpg.font_registry():
    #default_font = dpg.add_font("/Users/caizekun/蔡泽坤要干的事儿/selectRAWfile/ArialUnicode.ttf", 20)
    with dpg.font(FONT, 20) as font1:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
    dpg.bind_font(font1)

#dpg.show_font_manager()

dpg.add_file_dialog(
    directory_selector=True, show=False, callback=callback, tag="file_dialog_id",
    cancel_callback=cancel_callback, width=700 ,height=400)

with dpg.window(label="Warning", modal=True, show=False, tag="tRAWfolder_has_file", no_title_bar=True):
    dpg.add_text("Not empty folder!")
    dpg.add_separator()
    dpg.add_text("All the files that have same name will be replaced.")
    dpg.add_button(label="OK", width=75, callback=lambda: dpg.configure_item("tRAWfolder_has_file", show=False))

with dpg.window(label="Proceed", modal=True, show=False, tag="proceed", no_title_bar=True, width=400):
    dpg.add_text("Are you sure?", tag="proceed_message")
    dpg.add_button(label="Yes", width=75, tag='proceed_confirm', show=True, callback=confirmProceedData)
    dpg.add_same_line()
    dpg.add_button(label="No", width=75, tag='proceed_cancel', callback=lambda: dpg.configure_item("proceed", show=False))
    dpg.add_separator(show=False, tag='proceed_sep')
    dpg.add_progress_bar(show=False, tag='proceed_progress')
    dpg.add_text(show=False, tag='proceed_currentfile')

#GUI主页面

with dpg.window(label="Main", width=800, height=600):
    dpg.add_button(label="Select JPEG folder", callback=JpegSelectCallback)
    dpg.add_input_text(readonly=True, tag="JPEG_folder_path")
    dpg.add_button(label="Select RAW folder", callback=RawSelectCallback)
    dpg.add_input_text(readonly=True, tag="RAW_folder_path")
    dpg.add_button(label="Select target RAW folder", callback=tRawSelectCallback)
    dpg.add_input_text(readonly=True, tag="tRAW_folder_path")
    dpg.add_button(label="Proceed", callback=showProceedWindow)
    dpg.add_separator()
    with dpg.table(header_row=True, tag="info_table"):
        dpg.add_table_column(label="Status", tag="table_status") #复制状态
        dpg.add_table_column(label="RAW Files", tag="table_rawfiles") #RAW文件列表
        dpg.add_table_column(label="JPEG Files", tag="table_jpegfiles") #JPEG文件列表

dpg.create_viewport(title="selectRAWfile", width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
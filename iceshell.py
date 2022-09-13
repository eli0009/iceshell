import sys, subprocess
import breeze_resources
from platform import system
from pathlib import Path
from ddlabel import DdLabel
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QFile, QTextStream
from PyQt5 import QtGui, uic


#get current working dir because this program can be run from anywhere
root = Path(__file__).parent

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        #load the UI files
        uic.loadUi(str(root / 'ui/main_window.ui'), self)

        '''
        Menubar
        '''
        menubar = self.findChild(QMenuBar, "menuBar")

        #upscale menu
        self.upscale_group = QActionGroup(self)
        self.upscale_actions = [
            self.findChild(QAction, action) for action in
            ("action1_3", "action2_3", "action3_3", "action4_2")
        ]
        for i in self.upscale_actions:
            self.upscale_group.addAction(i)

        #denoise menu
        self.denoise_group = QActionGroup(self)
        self.denoise_actions = [
            self.findChild(QAction, action) for action in
            ("action_2", "action0_2", "action1_4", "action2_4", "action3_4")
        ]
        for i in self.denoise_actions:
            self.denoise_group.addAction(i)

        #output extension menu
        self.ext_group = QActionGroup(self)
        ext_actions = [
            self.findChild(QAction, action) for action in
            ("actionSame", "actionjpg_2", "actionpng_2", "actionwebp_2")
        ]
        for i in ext_actions:
            self.ext_group.addAction(i)

        #output folder menu
        self.folder_group = QActionGroup(self)
        folder_actions = [
            self.findChild(QAction, action) for action in
            ("actionSame_as_input_2", "actionSelect_2")
        ]
        for i in folder_actions:
            self.folder_group.addAction(i)
        
        self.same_as_input = folder_actions[0]
        self.outfolder = None
        self.folder_group.triggered.connect(self.folder_selector)

        #upscaler selection menu
        self.upscaler_group = QActionGroup(self)
        upscaler_actions = [
            self.findChild(QAction, action) for action in
            ("actionReal_CUGAN", "actionReal_ESRGAN", "actionWaifu2X")
        ]
        for i in upscaler_actions:
            self.upscaler_group.addAction(i)
        self.upscaler_group.triggered.connect(self.selectable_options)

        #about menu
        about = self.findChild(QAction, "actionAbout_2")
        about.triggered.connect(self.popup)

        # #progress bar
        # self.progress_bar = QProgressBar(self)
        # self.progress_bar.setValue(100)

        """
        file input
        """
        self.label_file_input = self.findChild(DdLabel, "label_file_input")
        self.label_file_input.signal.dropped.connect(self.image_upscale)
        
    def popup(self):
        '''
        Handle the popup window that shows up when you click About
        '''
        popup = PopupWindow()
        popup.setWindowIcon(QtGui.QIcon(str(root / 'ui/res/logo.png')))
        popup.exec()

    def display_values(self):
        '''Return the current value of various option menus as a dict'''
        return {
            'upscale': self.upscale_group.checkedAction().text(),
            'denoise': self.denoise_group.checkedAction().text(),
            'outext': self.ext_group.checkedAction().text(),
            'upscaler': self.upscaler_group.checkedAction().text().replace('-', '').lower()
        }

    def folder_selector(self):
        '''
        Launch a file selector and set outfolder to the user selected folder
        set outfolder to None if selected folder is not valid
        '''
        if self.folder_group.checkedAction().text() == 'Select...':
            folder = QFileDialog.getExistingDirectory(self,
                                                        "Select Output Folder")

            if folder:
                self.outfolder = Path(folder)
            else:
                self.outfolder = None
                self.same_as_input.setChecked(True)
        else:
            self.outfolder = None

        print(self.outfolder)

    def get_upscaler(self, upscaler):
        '''
        Get the path of the selected upscaler
        '''
        os = system().lower()
        if os == 'linux':
            os = 'ubuntu'
        upscale_folder = list((root / 'upscalers').glob(f'{upscaler}*{os}'))[0]
        return (upscale_folder /
                (upscaler + '-ncnn-vulkan' + ['', '.exe'][os == 'windows']))

    def selectable_options(self):
        '''
        Change selectable options depending on the upscaler
        '''
        options = self.upscale_actions + self.denoise_actions
        # list of disabled options for each upscaler
        config = {
            'realcugan': [],
            'realesrgan': [0] + list(range(4, 9)),
            'waifu2x': [2],
        }
        disabled_options = config.get(self.display_values().get('upscaler'))

        for index, option in enumerate(options):
            option.setDisabled(index in disabled_options)

        #error checking by changing the current selected option to 2x 
        if not self.upscale_group.checkedAction().isEnabled():
            options[1].setChecked(True)

    def image_upscale(self):
        '''
        Image processing through an upscaler
        '''
        #get all the data previously obtained
        values = self.display_values()
        images = self.label_file_input.files
        
        # #prepare progressbar for processing
        # self.progress_bar.setValue(0)
        # increment = 100 // len(images)

        for image in images:
            """
            get the image's extension, name without extension, and the folder 
            where it resides
            /home/user/test.jpg should give:
            jpg (ext)
            test (name)
            /home/user/ (folder)
            """
            image = Path(image)
            image_ext = image.suffix
            image_name = image.stem
            image_folder = image.parent
            image = str(image)

            #get the right output extension
            outext = values['outext']
            if outext == 'Same as Input':
                outext = image_ext
            #get the right output folder
            if self.outfolder is None:
                outfolder = image_folder
            else:
                outfolder = self.outfolder


            upscaler = values.get('upscaler')
            upscaler_path = self.get_upscaler(upscaler)

            outupscale, outdenoise = values.get('upscale'), values.get('denoise')
            #get complete path of output image
            outimage = str(
                outfolder / (
                    image_name + '_' + 
                    self.upscaler_group.checkedAction().text().replace("Real-", "") + (f"_x{outupscale}" if outupscale != "1" else "") +
                    (f'_n{outdenoise}' if outdenoise != '-1' and upscaler != 'realesrgan' else '') + outext
                    )
            )

            #start the conversion! run the program in the shell
            args = [str(upscaler_path), "-i",
                    image, '-o', outimage, '-s', outupscale, '-n', 
                    'realesr-animevideov3' if upscaler == 'realesrgan' else outdenoise]
            print(args)
            subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print(outimage) 
            # # self.progress_bar.setValue(self.progress_bar.value() + increment)
        
        # self.progress_bar.setValue(100)


class PopupWindow(QDialog):
    """This class is for the popup window used in MainWindow"""
    def __init__(self):
        super(PopupWindow, self).__init__()
        uic.loadUi(str(root / 'ui/popup.ui'), self)


if __name__ == '__main__':
    #run the program
    app = QApplication(sys.argv)
    window = MainWindow()

    #styling
    file = QFile(":/light-green/stylesheet.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())    
    window.setWindowIcon(QtGui.QIcon(str(root / 'ui/res/logo.png')))
    
    window.show()
    app.exec()
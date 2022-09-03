import sys, subprocess
from platform import system
from pathlib import Path
from ddlabel import DdLabel
from PyQt5.QtWidgets import (QComboBox, QPushButton, QFileDialog, QDialog,
                             QMainWindow, QApplication, QProgressBar)
from PyQt5 import QtGui, uic


#get current working dir because this program can be run from anywhere
root = Path(__file__).parent
if system() == 'Linux':
    cugan = Path('realcugan-ncnn-vulkan-linux/realcugan-ncnn-vulkan')
elif system() == 'Windows':
    cugan = Path('realcugan-ncnn-vulkan-windows/realcugan-ncnn-vulkan.exe')


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        #load the UI files
        uic.loadUi(str(root / 'ui/main_window.ui'), self)

        #define widgets from the UI file
        self.comboBox_upscale = self.findChild(QComboBox, "comboBox_upscale")
        self.comboBox_upscale.setCurrentText("2") #fix the default value
        self.comboBox_denoise = self.findChild(QComboBox, "comboBox_denoise")
        self.comboBox_outext = self.findChild(QComboBox, "comboBox_outext")

        #about button
        button_about = self.findChild(QPushButton, "pushButton_about")
        button_about.clicked.connect(self.popup)

        """
        file output
        """
        self.comboBox_outdir = self.findChild(QComboBox, "comboBox_outdir")
        self.button_selector_out = self.findChild(QPushButton,
                                                  "pushButton_selector_out")
        self.comboBox_outdir.activated.connect(self.file_selector)
        self.button_selector_out.clicked.connect(self.file_selector)
        #placeholder output folder
        self.outfolder = None

        """
        file input
        """
        self.label_file_input = self.findChild(DdLabel, "label_file_input")
        self.label_file_input.signal.dropped.connect(self.image_upscale)
        self.progress_bar = self.findChild(QProgressBar, "progressBar")
        
    def popup(self):
        '''
        Handle the popup window that shows up when you click About
        '''
        popup = PopupWindow()
        popup.setWindowIcon(QtGui.QIcon(str(root / 'ui/res/logo.png')))
        popup.exec()

    def display_values(self):
        '''Return the current value of various comboboxes as a dict'''
        return {
            'upscale': self.comboBox_upscale.currentText(),
            'denoise': self.comboBox_denoise.currentText(),
            'outext': self.comboBox_outext.currentText(),
            'outdir': self.comboBox_outdir.currentText(),
        }

    def file_selector(self):
        '''
        Launch a file selector if the output dir combobox is on the right option
        Otherwise disable
        '''
        if self.display_values().get('outdir') == 'Select...':
            self.button_selector_out.setDisabled(False)
            folder = QFileDialog.getExistingDirectory(self,
                                                      "Select Output Folder")
            #reset outfolder to none if not valid
            self.outfolder = Path(folder) if folder else None

            if self.outfolder:
                self.button_selector_out.setText("Output Folder Selected!")
                self.button_selector_out.setToolTip(str(self.outfolder))
            else:
                self.button_selector_out.setText("Click to Select Output Folder!")
                self.button_selector_out.setToolTip(
                    "No output folder selected! Using same folder as input"
                    )

        #if the outdir combobox is on the wrong option disable output button
        else:
            self.button_selector_out.setDisabled(True)
            self.button_selector_out.setText("Same Folder as Input")
            self.button_selector_out.setToolTip("Using same folder as input")
            self.outfolder = None

    def image_upscale(self):
        '''
        Image processing through Real-Cugan
        '''
        #get all the data previously obtained
        values = self.display_values()
        images = self.label_file_input.files

        
        #error checking and fixing
        if values.get('outdir') != 'Same' and self.outfolder is None:
            values['outdir'] = 'Same'
        
        #prepare progressbar for processing
        self.progress_bar.setValue(0)
        increment = 100 // len(images)

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
            image_ext = image.suffix[1:]
            image_name = image.stem
            image_folder = image.parent
            image = str(image)

            #get the right output extension
            outext = values['outext']
            if outext == 'Same':
                outext = image_ext
            #get the right output folder
            if values.get('outdir') == 'Same':
                outfolder = image_folder
            else:
                outfolder = self.outfolder

            outupscale, outdenoise = values.get('upscale'), values.get('denoise')
            #get complete path of output image
            outimage = str(
                outfolder / (
                    image_name +
                    (f'_CUGAN{"_x" + outupscale if outupscale != "1" else ""}') +
                    (f'_n{outdenoise}' if outdenoise != '-1' else '') + 
                    '.' + outext
                    )
            )

            #start the conversion! run the program in the shell
            args = [str(root / cugan), "-i",
                    image, '-o', outimage, '-s', outupscale, '-n', outdenoise]
            subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print(outimage) 
            self.progress_bar.setValue(self.progress_bar.value() + increment)
        
        self.progress_bar.setValue(100)


class PopupWindow(QDialog):
    """This class is for the popup window used in MainWindow"""
    def __init__(self):
        super(PopupWindow, self).__init__()
        uic.loadUi(str(root / 'ui/popup.ui'), self)


if __name__ == '__main__':
    #run the program
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowIcon(QtGui.QIcon(str(root / 'ui/res/logo.png'))) #add logo
    window.show()
    app.exec()
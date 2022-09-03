from PyQt5.QtWidgets import QLabel, QFileDialog
from PyQt5.QtCore import pyqtSignal, QObject
from platform import system

class DroppedSignal(QObject):
    '''
    Custom signal for DdLabel
    '''
    dropped = pyqtSignal()

    
class DdLabel(QLabel):
    '''
    Drag and drop Label:
    Custom QLabel widget to promote in Qt Designer to enable 
    drag and drop

    Emit dropped signal if it receives the correct filetypes (png, jpg, jpeg, webp)
    '''
    def __init__(self, parent):
        super(QLabel, self).__init__(parent)
        self.setAcceptDrops(True)
        #list of all files to be sent to Real CUGAN
        self.files = []
        #connection to the custom signal
        self.signal = DroppedSignal()

    def dragEnterEvent(self, event):
        '''
        Decide whether or not to accept the drag and drop though file extension
        This program assumes that the user's filenames extension accurately
        represent the file type
        '''
        for file in event.mimeData().urls():
            ext = file.path().lower().split('.')[-1]
            if not ext in ('png', 'jpg', 'jpeg', 'webp'): return
        event.accept()

    def dropEvent(self, event):
        '''
        Handle what happens after the user drops the files in the window
        Emit signal for CUGAN processing if files are valid
        The error check is handled in dragEnterEvent
        '''
        self.files = [
            file.path()[system() == 'Windows':] #strip first char if on windows
            for file in event.mimeData().urls()
        ]
        event.accept()
        self.signal.dropped.emit()

    def mousePressEvent(self, event):
        '''
        Open a file dialogue when the user click on the program to prompt
        the input of image files for the processing
        '''
        files = QFileDialog().getOpenFileNames(self, "Select Input Images", 
            filter="Image Files (*.png *.jpg *.jpeg *.webp)"
        )[0]
        #Handle error(do nothing when there is no file selected)
        if files:
            self.files = files
            self.signal.dropped.emit()
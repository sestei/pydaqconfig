from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

import time

def get_login(realm, username, may_save):
    return True, 'jifuser', 'LA5ER3urn', True

def wait_cursor(fn):
    def decorator(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        retval = None
        try:
            retval = fn(*args, **kwargs)
        finally:
            QApplication.restoreOverrideCursor()
        return retval
    return decorator


class ArchivedIni(object):
    def __init__(self, modelname, inifile, log):
        self._inifile = inifile
        self.modelname = modelname
        self._log = log
        self.revision = log.revision.number
        self.date = time.ctime(log.date)

    def __str__(self):
        return '{a.modelname} @ {a.date} [rev #{a.revision}]'.format(a=self)

    def contents(self):
        try:
            import pysvn
        except ImportError:
            return None

        client = pysvn.Client()
        return client.cat(self._inifile, revision=self._log.revision)
            
class ArchiveDialog(QDialog):
    def __init__(self, parent, inifile, modelname):
        super(ArchiveDialog, self).__init__(parent)
        uic.loadUi('ui/archive.ui', self)
        self._archive = []
        self._modelname = modelname
        
        self.lblArchive.setText(self.lblArchive.text() + modelname + ':')
        self.load_archive(inifile)
        self.update_list()

    @wait_cursor
    def load_archive(self, inifile):
        try:
            import pysvn
        except ImportError:
            return

        client = pysvn.Client()
        try:
            for log in client.log(inifile):
                self._archive.append(ArchivedIni(self._modelname, inifile, log))
        except pysvn.ClientError, e:
            self.lstArchive.addItem('No archived versions available')
            self.lstArchive.setEnabled(False)

    def update_list(self):
        self.lstArchive.addItems([str(s) for s in self._archive])
        self.lstArchive.setCurrentRow(0)

    @wait_cursor
    def get_archived_ini(self):
        row = self.lstArchive.currentRow()
        if row < 0 or not self.lstArchive.isEnabled():
            return None
        else:
            return self._archive[row]

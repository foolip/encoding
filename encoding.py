# -*- coding: utf-8 -*-

PLUGIN_NAME = u"Convert Encoding"
PLUGIN_AUTHOR = u"Philip Jägenstedt"
PLUGIN_DESCRIPTION = "Convert the tags of individual files or clusters between different character encodings. This is often necessary with files that have only ID3v1 tags in a non-Latin encoding."
PLUGIN_VERSION = "0.2"
PLUGIN_API_VERSIONS = ["0.9.0", "0.10"]

import codecs

from PyQt4 import QtCore, QtGui
from picard.cluster import Cluster
from picard.file import File
from picard.ui.itemviews import BaseAction, register_file_action, register_cluster_action
from picard.ui.util import StandardButton

encodings = ["Arabic (ISO-8859-6)",
             "Arabic (Windows-1256)",
             "Baltic (ISO-8859-4)",
             "Baltic (ISO-8859-13)",
             "Baltic (Windows-1257)",
             "Celtic (ISO-8859-14)",
             "Central European (ISO-8859-2)",
             "Central European (ISO-8859-16)",
             "Central European (Windows-1250)",
             "Chinese Simplified (GB2312)",
             "Chinese Simplified (GBK)",
             "Chinese Simplified (GB18030)",
             "Chinese Traditional (Big5)",
             "Chinese Traditional (Big5-HKSCS)",
             "Cyrillic (ISO-8859-5)",
             "Cyrillic (KOI8-R)",
             "Cyrillic (KOI8-U)",
             "Cyrillic (Windows-1251)",
             "Greek (ISO-8859-7)",
             "Greek (Windows-1253)",
             "Hebrew (ISO-8859-8)",
             "Hebrew (Windows-1255)",
             "Japanese (Shift-JIS)",
             "Japanese (EUC-JP)",
             "Japanese (ISO-2022-JP)",
             "Korean (EUC-KR)",
             "Korean (UHC)",
             "Korean (JOHAB)",
             "Korean (ISO-2022-KR)",
             "Nordic (ISO-8859-10)",
             "South European (ISO-8859-3)",
             "Thai (TIS-620)",
             "Thai (ISO-8859-11)",
             "Turkish (ISO-8859-9)",
             "Turkish (Windows-1254)",
             "Vietnamese (Windows-1258)",
             "Western (ISO-8859-1)",
             "Western (ISO-8859-15)",
             "Western (Windows-1251)"]

class ConvertFileEncoding(BaseAction):
    NAME = "Convert Encoding..."

    def convert(self, source, target, file):
        for field in ['title', 'artist', 'album']:
            f = file.metadata[field]
            f = f.encode(source, 'backslashreplace')
            f = f.decode(target, 'replace')
            file.metadata[field] = f
        file.update()

    def callback(self, objs):
        dialog = EncodingDialog(self.tagger.window)
        if dialog.exec_():
            for o in objs:
                if isinstance(o, File):
                    self.convert(dialog.source, dialog.target, o)

register_file_action(ConvertFileEncoding())

class ConvertClusterEncoding(ConvertFileEncoding):
    def convert(self, source, target, cluster):
        for file in cluster.files:
            ConvertFileEncoding.convert(self, source, target, file)

        for field in ['artist', 'album']:
            f = cluster.metadata[field]
            f = f.encode(source, 'backslashreplace')
            f = f.decode(target, 'replace')
            cluster.metadata[field] = f
        cluster.update()

    def callback(self, objs):
        dialog = EncodingDialog(self.tagger.window)
        if dialog.exec_():
            for o in objs:
                if isinstance(o, Cluster):
                    self.convert(dialog.source, dialog.target, o)

register_cluster_action(ConvertClusterEncoding())

class ResetFileEncoding(BaseAction):
    NAME = "Reset Encoding..."

    def reset(self, file):
        for field in ['title', 'artist', 'album']:
            file.metadata[field] = file.orig_metadata[field]
        file.update()

    def callback(self, objs):
        for o in objs:
            if isinstance(o, File):
                self.reset(o)

register_file_action(ResetFileEncoding())

class ResetClusterEncoding(ResetFileEncoding):
    def reset(self, cluster):
        for file in cluster.files:
            ResetFileEncoding.reset(self, file)

        # FIXME: unsupported
        #for field in ['artist', 'album']:
        #    cluster.metadata[field] = cluster.orig_metadata[field]

    def callback(self, objs):
        for o in objs:
            if isinstance(o, Cluster):
                self.reset(o)

register_cluster_action(ResetClusterEncoding())

class EncodingDialog(QtGui.QDialog):
    sourceText = "Western (ISO-8859-1)"
    targetText = ""

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.ui = Ui_EncodingDialog()
        self.ui.setupUi(self)

        self.ui.buttonbox.addButton(StandardButton(StandardButton.OK), QtGui.QDialogButtonBox.AcceptRole)
        self.ui.buttonbox.addButton(StandardButton(StandardButton.CANCEL), QtGui.QDialogButtonBox.RejectRole)
        self.connect(self.ui.buttonbox, QtCore.SIGNAL('accepted()'), self, QtCore.SLOT('accept()'))
        self.connect(self.ui.buttonbox, QtCore.SIGNAL('rejected()'), self, QtCore.SLOT('reject()'))

        self.ui.sourceEncoding.addItems(encodings)
        self.ui.sourceEncoding.setEditText(self.sourceText)
        self.ui.targetEncoding.addItems(encodings)
        self.ui.targetEncoding.setEditText(self.targetText)

    def encoding(self, enc):
        try:
            return codecs.lookup(enc.split('(')[-1].split(')')[0]).name
        except LookupError:
            return None

    def unsupported(self, which):
        dialog = QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Unsupported Encoding",
                                   "Unsupported %s encoding." % which,
                                   QtGui.QMessageBox.Ok, self.tagger.window)
        dialog.exec_()

    def accept(self):
        EncodingDialog.sourceText = unicode(self.ui.sourceEncoding.currentText())
        EncodingDialog.targetText = unicode(self.ui.targetEncoding.currentText())
        self.source = self.encoding(self.sourceText)
        self.target = self.encoding(self.targetText)

        if not self.source:
            self.unsupported('source')
        elif not self.target:
            self.unsupported('target')
        else:
            QtGui.QDialog.accept(self)

# Form implementation generated from reading ui file 'encoding.ui'
#
# Created: Sun Dec  9 10:36:26 2007
#      by: PyQt4 UI code generator 4.3
#
# WARNING! All changes made below will be lost!

class Ui_EncodingDialog(object):
    def setupUi(self, EncodingDialog):
        EncodingDialog.setObjectName("EncodingDialog")

        self.vboxlayout = QtGui.QVBoxLayout(EncodingDialog)
        self.vboxlayout.setMargin(9)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.sourceLabel = QtGui.QLabel(EncodingDialog)
        self.sourceLabel.setObjectName("sourceLabel")
        self.vboxlayout.addWidget(self.sourceLabel)

        self.sourceEncoding = QtGui.QComboBox(EncodingDialog)
        self.sourceEncoding.setEditable(True)
        self.sourceEncoding.setObjectName("sourceEncoding")
        self.vboxlayout.addWidget(self.sourceEncoding)

        self.targetLabel = QtGui.QLabel(EncodingDialog)
        self.targetLabel.setObjectName("targetLabel")
        self.vboxlayout.addWidget(self.targetLabel)

        self.targetEncoding = QtGui.QComboBox(EncodingDialog)
        self.targetEncoding.setEditable(True)
        self.targetEncoding.setObjectName("targetEncoding")
        self.vboxlayout.addWidget(self.targetEncoding)

        self.buttonbox = QtGui.QDialogButtonBox(EncodingDialog)
        self.buttonbox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonbox.setObjectName("buttonbox")
        self.vboxlayout.addWidget(self.buttonbox)
        self.sourceLabel.setBuddy(self.sourceEncoding)
        self.targetLabel.setBuddy(self.targetEncoding)

        self.retranslateUi(EncodingDialog)
        QtCore.QMetaObject.connectSlotsByName(EncodingDialog)
        EncodingDialog.setTabOrder(self.buttonbox,self.sourceEncoding)
        EncodingDialog.setTabOrder(self.sourceEncoding,self.targetEncoding)

    def retranslateUi(self, EncodingDialog):
        EncodingDialog.setWindowTitle(QtGui.QApplication.translate("EncodingDialog", "Convert Encoding", None, QtGui.QApplication.UnicodeUTF8))
        self.sourceLabel.setText(QtGui.QApplication.translate("EncodingDialog", "Source encoding:", None, QtGui.QApplication.UnicodeUTF8))
        self.targetLabel.setText(QtGui.QApplication.translate("EncodingDialog", "Target encoding:", None, QtGui.QApplication.UnicodeUTF8))

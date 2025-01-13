# Radial Symmetry Tool
# Bryn Shellenback
# ANGM 3311

import maya.cmds as cmds
import maya.mel as mel

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as OmUI


def get_maya_main_win():
    """Return Maya main window widget"""
    main_window = OmUI.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QWidget)

# CREATING THE UI


class RSymmetryToolWin(QtWidgets.QDialog):
    def __init__(self):
        super().__init__(parent=get_maya_main_win())
        self.axes_setup_exists = False
        self.rsymmetrytool = RadialSymmetryTool()

        self.setWindowTitle('Radial Symmetry Toolkit')
        self.resize(300, 225)
        self._make_main_layout()
        self._connect_signals()
        self.is_activated = False

# Main Layout:
    def _make_main_layout(self):
        self.main_vlt = QtWidgets.QVBoxLayout()
        self._make_btn_layout()
        self._make_vert_layout()
        self.main_vlt.addLayout(self.vert_vlt)
        self.main_vlt.addLayout(self.btn_hlt)
        self.setLayout(self.main_vlt)

    def _make_vert_layout(self):
        self.vert_vlt = QtWidgets.QVBoxLayout()
        self._make_select_btn()
        self._lt_pivot_options()
        self._lt_axes_options()
        self._lt_obj_options()

        self.vert_vlt.addWidget(self.select_geo_button)
        for lt in [self.pivot_vlt, self.axes_vlt,
                   self.obj_vlt]:
            self.vert_vlt.addLayout(lt)

    def _make_btn_layout(self):
        self.btn_hlt = QtWidgets.QHBoxLayout()
        self.activate_btn = QtWidgets.QPushButton("Activate Tool")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.btn_hlt.addWidget(self.activate_btn)
        self.btn_hlt.addWidget(self.cancel_btn)

# Select and Pivot Options:
    def _make_select_btn(self):
        self.select_geo_button = QtWidgets.QPushButton("Select Current"
                                                       " Geo")

    def _make_pivot_btns(self):
        self.piv_opt_label = QtWidgets.QLabel("Pivot Controls:")
        self.ori_pivot = QtWidgets.QCheckBox("Pivot on Origin")
        self.obj_pivot = QtWidgets.QCheckBox("Pivot on Object")
        self.comp_pivot = QtWidgets.QCheckBox("Pivot on Selected"
                                              " Component")
        self.move_pivot = QtWidgets.QPushButton("Move Pivot")

    def _lt_pivot_options(self):
        self.pivot_options = QtWidgets.QHBoxLayout()
        self.pivot_vlt = QtWidgets.QVBoxLayout()
        self.pivot_opts_group = QtWidgets.QButtonGroup()
        self._make_pivot_btns()

        for box in [self.ori_pivot, self.obj_pivot, self.comp_pivot]:
            self.pivot_opts_group.addButton(box)
            self.pivot_options.addWidget(box)

        self.pivot_vlt.addWidget(self.piv_opt_label)
        self.pivot_vlt.addLayout(self.pivot_options)
        self.pivot_vlt.addWidget(self.move_pivot)

# Axes Options:
    def _setup_axes_lsts(self):
        self.axis_btn_lst = []
        self.asb_lt_lst = []
        self.ncopy_sld_lst = []
        self.ncopy_lt_lst = []

    def _setup_axes_options(self):
        self._lt_num_axes()
        self._setup_axes_lsts()
        self.axes_vlt = QtWidgets.QVBoxLayout()

        self.prev_axes_value = 1
        self.axes_vlt.addLayout(self.num_axes_hlt)
        self.axes_setup_exists = True

    def _make_numaxes_btn(self):
        self.axes_label = QtWidgets.QLabel("Number of Axes")
        self.axes_number = QtWidgets.QSpinBox()
        self.axes_number.setValue(1)
        self.axes_number.setMaximum(12)

    def _lt_num_axes(self):
        self._make_numaxes_btn()
        self.num_axes_hlt = QtWidgets.QHBoxLayout()
        self.num_axes_hlt.addWidget(self.axes_label)
        self.num_axes_hlt.addWidget(self.axes_number)

    def _make_ncopy_btn(self):
        sld_ori = QtCore.Qt.Orientation.Horizontal
        self.ncopy = QtWidgets.QSlider(orientation=sld_ori)
        self.ncopy.setMinimum(1)
        self.ncopy.setMaximum(99)
        self.ncopy.setValue(3)
        self.ncopy.valueChanged.connect(self.update_symmetry)
        self.ncopy.valueChanged.connect(self.update_ncopy_ui)

    def _lt_ncopy(self):
        self._make_ncopy_btn()
        self.ncopies_hlt = QtWidgets.QHBoxLayout()
        self.ncopies_lbl = QtWidgets.QLabel("Number of Copies")
        self.ncopies_val = QtWidgets.QLabel("3")
        for btn in [self.ncopies_lbl, self.ncopy, self.ncopies_val]:
            self.ncopies_hlt.addWidget(btn)

    def _make_axis_btns(self):
        self.xbox = QtWidgets.QDoubleSpinBox()
        self.ybox = QtWidgets.QDoubleSpinBox()
        self.zbox = QtWidgets.QDoubleSpinBox()
        for box in [self.xbox, self.ybox, self.zbox]:
            box.setMaximum(360.00)
            box.valueChanged.connect(self.update_symmetry)

    def _lt_axes_btns(self):
        self._make_axis_btns()
        self.axis_sb_lt = QtWidgets.QHBoxLayout()
        for box in [self.xbox, self.ybox, self.zbox]:
            self.axis_sb_lt.addWidget(box)

    def _lt_axes_options(self):
        if self.axes_setup_exists is False:
            self._setup_axes_options()
        self._lt_ncopy()
        self._lt_axes_btns()

        self.axis_btn_lst.append([self.xbox, self.ybox, self.zbox])
        self.asb_lt_lst.append(self.axis_sb_lt)
        self.ncopy_sld_lst.append([self.ncopies_lbl, self.ncopy,
                                   self.ncopies_val])
        self.ncopy_lt_lst.append(self.ncopies_hlt)

        self.axes_vlt.addLayout(self.axis_sb_lt)
        self.axes_vlt.addLayout(self.ncopies_hlt)

# Object Options:
    def _make_obj_name_btn(self):
        self.name_lbl = QtWidgets.QLabel("New Object Name")
        self.name_edit = QtWidgets.QLineEdit()

    def _make_sep_comb_btns(self):
        self.sep_box = QtWidgets.QCheckBox("Keep Separate Geometry")
        self.sep_box.setChecked(True)
        self.combine_box = QtWidgets.QCheckBox("Combine Geometry")

    def _make_fuse_btns(self):
        self.fuse_box = QtWidgets.QCheckBox("Fuse Geometry")
        self.fuse_lbl = QtWidgets.QLabel("Fuse Threshold")
        self.fuse_val = QtWidgets.QLabel("3")
        sld_ori = QtCore.Qt.Orientation.Horizontal
        self.fuse_sld = QtWidgets.QSlider(orientation=sld_ori)
        self.fuse_sld.setMinimum(1)
        self.fuse_sld.setMaximum(100)
        self.fuse_sld.setValue(3)

    def _make_obj_lts(self):
        self.obj_vlt = QtWidgets.QVBoxLayout()
        self.name_hlt = QtWidgets.QHBoxLayout()
        self.merge_opts_hlt = QtWidgets.QHBoxLayout()
        self.merge_opts_grp = QtWidgets.QButtonGroup()
        self.fuse_opts_hlt = QtWidgets.QHBoxLayout()

    def _add_obj_lts(self):
        for box in [self.sep_box, self.combine_box, self.fuse_box]:
            self.merge_opts_grp.addButton(box)
            self.merge_opts_hlt.addWidget(box)

        for btn in [self.name_lbl, self.name_edit]:
            self.name_hlt.addWidget(btn)

        for btn in [self.fuse_lbl, self.fuse_sld, self.fuse_val]:
            self.fuse_opts_hlt.addWidget(btn)

        for lt in [self.name_hlt, self.merge_opts_hlt,
                   self.fuse_opts_hlt]:
            self.obj_vlt.addLayout(lt)

    def _lt_obj_options(self):
        self._make_obj_name_btn()
        self._make_sep_comb_btns()
        self._make_fuse_btns()
        self._make_obj_lts()
        self._add_obj_lts()

# Retrieving Values and Connecting Functions:
    def _create_axis_values_lst(self):
        self.axis_vals = []
        for btn_ary in self.axis_btn_lst:
            self.axis_vals.append([btn_ary[0].value(),
                                   btn_ary[1].value(),
                                   btn_ary[2].value()])

    def _create_ncopy_lst(self):
        self.ncopy_vals = []
        self.ncopy_lbls = []
        for val in self.ncopy_sld_lst:
            self.ncopy_vals.append(val[1].value())
            self.ncopy_lbls.append(val[2])

    def _connect_signals(self):
        self.cancel_btn.clicked.connect(self.cancel)
        self.activate_btn.clicked.connect(self.activate)
        self.move_pivot.clicked.connect(self.update_pivot)
        self.axes_number.valueChanged.connect(self.update_ui)
        self.select_geo_button.clicked.connect(self.select_geo)
        self.fuse_sld.valueChanged.connect(self.update_symmetry)
        self.merge_opts_grp.buttonClicked.connect(self.update_symmetry)
        self.fuse_sld.valueChanged.connect(self.update_fuse_ui)

    @QtCore.Slot()
    def cancel(self):
        self.close()

    @QtCore.Slot()
    def activate(self):
        self.is_activated = True
        self._create_axis_values_lst()
        self._create_ncopy_lst()
        self.is_fused = self.fuse_box.isChecked()
        self.is_combined = self.combine_box.isChecked()

        self.rsymmetrytool.generate_instances(self.ncopy_vals,
                                              self.axis_vals)
        if self.is_fused:
            self.rsymmetrytool._fuse_instances(self.fuse_sld.value(),
                                               self.name_edit.text())

        if self.is_combined:
            self.rsymmetrytool._combine_instances(self.name_edit.text())

# Update UI Functions
    @QtCore.Slot()
    def update_fuse_ui(self):
        self.fuse_val.setText(f"{self.fuse_sld.value()}")

    @QtCore.Slot()
    def update_ncopy_ui(self):
        for i in range(len(self.ncopy_sld_lst)):
            self.ncopy_sld_lst[i][2].setText(
                f"{self.ncopy_sld_lst[i][1].value()}")

    def _delete_axis_lt(self, value_changed):
        """ CITATION: After I realized that creating and removing a
        bunch of widgets without properly deleting them could cause
        a memory leak, I used the link below to find a function
        I could use to prevent memory leaks. """
        """https://www.geeksforgeeks.org/deletelater-method-in-pyqt5/"""
        for n in range(abs(value_changed)):

            for widget in [[self.asb_lt_lst, self.axis_btn_lst],
                           [self.ncopy_lt_lst, self.ncopy_sld_lst]]:
                for i in range(3):
                    widget[0][-1].removeWidget(widget[1][-1][i])
                    widget[1][-1][i].deleteLater()

            self.asb_lt_lst[-1].deleteLater()
            self.ncopy_lt_lst[-1].deleteLater()

            self.axes_vlt.removeItem(self.asb_lt_lst[-1])
            self.axes_vlt.removeItem(self.ncopy_lt_lst[-1])
            for lst in [self.asb_lt_lst, self.axis_btn_lst,
                        self.ncopy_lt_lst, self.ncopy_sld_lst]:
                lst.pop()

    @QtCore.Slot()
    def update_ui(self):
        value_changed = self.axes_number.value() - self.prev_axes_value
        self.prev_axes_value = self.axes_number.value()

        if (value_changed > 0):  # pos change, add layer
            for i in range(value_changed):
                self._lt_axes_options()

        elif (value_changed < 0):  # if negative, remove layer
            self._delete_axis_lt(value_changed)
        self.update_symmetry()

    @QtCore.Slot()
    def update_pivot(self):
        if self.ori_pivot.isChecked():
            pivottype = 0
        elif self.comp_pivot.isChecked():
            pivottype = 2
        else:
            pivottype = 1

        self.rsymmetrytool._move_pivot(pivottype)
        self.update_symmetry()

# Selecting Geo and Updating Symmetry
    @QtCore.Slot()
    def select_geo(self):
        self.is_activated = False
        self.rsymmetrytool._select_curr_geo()

    @QtCore.Slot()
    def update_symmetry(self):
        if self.is_activated:
            self.rsymmetrytool._delete_instances()
            self._create_ncopy_lst()
            self._create_axis_values_lst()
            self.is_fused = self.fuse_box.isChecked()
            self.is_combined = self.combine_box.isChecked()

            self.rsymmetrytool.generate_instances(self.ncopy_vals,
                                                  self.axis_vals)
            if self.is_fused:
                self.rsymmetrytool._fuse_instances(
                    self.fuse_sld.value(), self.name_edit.text())

            if self.is_combined:
                self.rsymmetrytool._combine_instances(
                    self.name_edit.text())

# RADIAL SYMMETRY TOOL


class RadialSymmetryTool():
    def __init__(self):
        self.instance_lst = []
        self.axis_grp_lst = []
        self.combgeo_lst = []
        self.fusegeo_lst = []
        self.apivot = [0, 0, 0]

    def _select_curr_geo(self):
        self.geo = cmds.ls(selection=True)[0]
        if not cmds.objectType(self.geo, isType="transform"):
            print("Invalid object type selected. Please select a "
                  "polygon surface.")
            self.geo = 0
        else:
            print(f"{self.geo} is selected.")
            # these are cleared so that new selections
            # don't delete finished geometry!
            self.axis_grp_lst = []
            self.instance_lst = []
            self.combgeo_lst = []
            self.fusegeo_lst = []

    def _delete_instances(self):
        cmds.select(deselect=True)
        #  ^ this stops user from accidentally deleting geometry
        for instance in self.instance_lst:
            if cmds.objExists(instance):
                cmds.select(instance, add=True)
                cmds.delete()
        for axis in self.axis_grp_lst:
            if cmds.objExists(axis):
                cmds.select(axis, add=True)
                cmds.delete()
        self.axis_grp_lst = []

    def _origin_pivot(self):
        """ CITATION: I used this source to help me understand how to
        move a pivot point on an object. The command manipPivot
        did not work as expected, but using xform on the rotatePivot
        component worked: """
        """ https://www.reddit.com/r/Maya/comments/q1nn1/how_do_you_
        move_pivots_in_maya_using_python/"""
        cmds.xform(f"{self.geo}.rotatePivot", translation=[0, 0, 0],
                   absolute=True, worldSpace=True)
        cmds.xform(f"{self.geo}.rotatePivot", rotation=[0, 0, 0],
                   worldSpace=True)
        self.apivot = [0, 0, 0]

    def _component_pivot(self):
        sl_comp = cmds.ls(selection=True)
        comp_transform = cmds.xform(sl_comp, translation=True,
                                    query=True, worldSpace=True)

        numpts = int(len(comp_transform) / 3)
        xsum, ysum, zsum = 0, 0, 0
        for val in range(numpts):
            xsum += comp_transform[3 * val]
            ysum += comp_transform[(3 * val) + 1]
            zsum += comp_transform[(3 * val) + 2]

        self.apivot = [xsum/numpts, ysum/numpts, zsum/numpts]
        # need to average the transform vals, because edges and faces
        # return multiple points
        cmds.xform(f"{self.geo}.rotatePivot", translation=self.apivot,
                   worldSpace=True)

    def _obj_pivot(self):
        self.apivot = cmds.objectCenter(self.geo)
        cmds.xform(f"{self.geo}.rotatePivot", translation=self.apivot,
                   worldSpace=True)

    def _move_pivot(self, pivottype):
        if pivottype == 0:
            self._origin_pivot()
        elif pivottype == 2:
            self._component_pivot()
        else:
            self._obj_pivot()  # pivot defaults to object space

    def _create_new_instances(self, ncopy, rotation, axisinstance, i):
        for num in range(ncopy[i]):
            instance = cmds.instance(self.geo,
                                     name=f"{self.geo}{num}_ax{i}")
            cmds.xform(instance,
                       rotation=[0, (rotation * (num + 1)), 0])

            axisinstance.append(instance[0])
            self.instance_lst.append(instance[0])

    def _generate_new_axes(self, axis_val_lst, ncopy):
        # This generates the instances around the Y axis first, groups
        # the instances, and then rotates the group
        i = 0
        for axis in axis_val_lst:
            rotation = 360.0 / (ncopy[i])
            axisinstance = []
            self._create_new_instances(ncopy, rotation, axisinstance, i)
            axis_grp = cmds.group(axisinstance,
                                  name=f"axisgrp_{self.geo}_{i}")
            self.axis_grp_lst.append(axis_grp)
            cmds.xform(f"{axis_grp}.rotatePivot",
                       translation=self.apivot,
                       absolute=True, worldSpace=True)

            cmds.xform(axis_grp, rotation=[axis[0], axis[1], axis[2]])
            axisinstance = []
            i += 1

    def generate_instances(self, ncopy, axis_val_lst):
        if (self.combgeo_lst != [] or self.fusegeo_lst != []):
            for lst in [self.combgeo_lst, self.fusegeo_lst]:
                # need to delete both lists
                for geo in lst:
                    if cmds.objExists(lst[-1]):
                        cmds.select(lst[-1])
                        cmds.delete()
        self.instance_lst = []
        self._generate_new_axes(axis_val_lst, ncopy)

    def _delete_merge_geo(self):
        for lst in [self.combgeo_lst, self.fusegeo_lst]:
            print(lst)
            # need to delete both lists to prevent duplicates
            for geo in lst:
                if cmds.objExists(lst[-1]):
                    cmds.select(lst[-1])
                    cmds.delete()
        self.combgeo_lst = []
        self.fusegeo_lst = []

    def _combine_instances(self, name):
        self._delete_merge_geo()
        objname = f"{self.geo}"
        dupobj = cmds.duplicate(self.geo)
        # needs to be duplicated because of instancing issues, will
        # otherwise delete the original geo

        self.combgeo, self.combshape = cmds.polyUnite(self.instance_lst,
                                                      centerPivot=True)

        if name != "":
            self.combgeo = cmds.rename(name)

        mel.eval("DeleteHistory;")
        # there is no deleteHistory command in Python yet :(
        self._delete_instances()
        cmds.rename(dupobj, objname)
        self.combgeo_lst.append(self.combgeo)

    def _fuse_instances(self, fuse_thresh, name):
        self._delete_merge_geo()
        objname = f"{self.geo}"
        dupobj = cmds.duplicate(self.geo)
        self.fusegeo, self.fuseshape = cmds.polyUnite(self.instance_lst,
                                                      centerPivot=True)

        if name != "":
            self.fusegeo = cmds.rename(name)

        mel.eval("DeleteHistory;")
        self._delete_instances()
        cmds.rename(dupobj, objname)

        cmds.select(f"{self.fusegeo}.vtx[0:]")
        cmds.polyMergeVertex(distance=fuse_thresh*0.01)
        self.fusegeo_lst.append(self.fusegeo)


if __name__ == "__main__":
    win = RSymmetryToolWin()
    win.show()

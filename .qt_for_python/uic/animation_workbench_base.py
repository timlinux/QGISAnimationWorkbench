# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/timlinux/dev/python/QGISAnimationWorkbench/ui/animation_workbench_base.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_animation_workbench_base(object):
    def setupUi(self, animation_workbench_base):
        animation_workbench_base.setObjectName("animation_workbench_base")
        animation_workbench_base.resize(1080, 830)
        self.gridLayout_9 = QtWidgets.QGridLayout(animation_workbench_base)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.frame = QtWidgets.QFrame(animation_workbench_base)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.render_mode_group = QtWidgets.QGroupBox(self.frame)
        self.render_mode_group.setObjectName("render_mode_group")
        self.gridLayout = QtWidgets.QGridLayout(self.render_mode_group)
        self.gridLayout.setObjectName("gridLayout")
        self.radio_sphere = QtWidgets.QRadioButton(self.render_mode_group)
        self.radio_sphere.setObjectName("radio_sphere")
        self.gridLayout.addWidget(self.radio_sphere, 0, 0, 1, 1)
        self.radio_planar = QtWidgets.QRadioButton(self.render_mode_group)
        self.radio_planar.setChecked(True)
        self.radio_planar.setObjectName("radio_planar")
        self.gridLayout.addWidget(self.radio_planar, 0, 1, 1, 1)
        self.radio_extent = QtWidgets.QRadioButton(self.render_mode_group)
        self.radio_extent.setObjectName("radio_extent")
        self.gridLayout.addWidget(self.radio_extent, 0, 2, 1, 1)
        self.gridLayout_7.addWidget(self.render_mode_group, 1, 0, 1, 1)
        self.settings_stack = QtWidgets.QStackedWidget(self.frame)
        self.settings_stack.setObjectName("settings_stack")
        self.non_fixed_extent_settings = QtWidgets.QWidget()
        self.non_fixed_extent_settings.setObjectName("non_fixed_extent_settings")
        self.gridLayout_15 = QtWidgets.QGridLayout(self.non_fixed_extent_settings)
        self.gridLayout_15.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_15.setSpacing(6)
        self.gridLayout_15.setObjectName("gridLayout_15")
        self.zoom_range_group = QtWidgets.QGroupBox(self.non_fixed_extent_settings)
        self.zoom_range_group.setEnabled(True)
        self.zoom_range_group.setObjectName("zoom_range_group")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.zoom_range_group)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.scale_range = gui.QgsScaleRangeWidget(self.zoom_range_group)
        self.scale_range.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.scale_range.setObjectName("scale_range")
        self.gridLayout_10.addWidget(self.scale_range, 0, 0, 1, 1)
        self.gridLayout_15.addWidget(self.zoom_range_group, 1, 0, 1, 1)
        self.animation_frames_group = QtWidgets.QGroupBox(self.non_fixed_extent_settings)
        self.animation_frames_group.setObjectName("animation_frames_group")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.animation_frames_group)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.hover_frames_label = QtWidgets.QLabel(self.animation_frames_group)
        self.hover_frames_label.setObjectName("hover_frames_label")
        self.gridLayout_8.addWidget(self.hover_frames_label, 2, 0, 1, 1)
        self.feature_frames_label = QtWidgets.QLabel(self.animation_frames_group)
        self.feature_frames_label.setObjectName("feature_frames_label")
        self.gridLayout_8.addWidget(self.feature_frames_label, 1, 0, 1, 1)
        self.feature_frames_spin = QtWidgets.QSpinBox(self.animation_frames_group)
        self.feature_frames_spin.setMaximum(999)
        self.feature_frames_spin.setProperty("value", 15)
        self.feature_frames_spin.setObjectName("feature_frames_spin")
        self.gridLayout_8.addWidget(self.feature_frames_spin, 1, 1, 1, 1)
        self.hover_frames_spin = QtWidgets.QSpinBox(self.animation_frames_group)
        self.hover_frames_spin.setMaximum(999)
        self.hover_frames_spin.setProperty("value", 15)
        self.hover_frames_spin.setObjectName("hover_frames_spin")
        self.gridLayout_8.addWidget(self.hover_frames_spin, 2, 1, 1, 1)
        self.framerate_spin = QtWidgets.QSpinBox(self.animation_frames_group)
        self.framerate_spin.setProperty("value", 30)
        self.framerate_spin.setObjectName("framerate_spin")
        self.gridLayout_8.addWidget(self.framerate_spin, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.animation_frames_group)
        self.label.setObjectName("label")
        self.gridLayout_8.addWidget(self.label, 0, 0, 1, 1)
        self.gridLayout_15.addWidget(self.animation_frames_group, 2, 0, 1, 1)
        self.easings_group = QtWidgets.QGroupBox(self.non_fixed_extent_settings)
        self.easings_group.setObjectName("easings_group")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.easings_group)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.layer_combo = gui.QgsMapLayerComboBox(self.easings_group)
        self.layer_combo.setObjectName("layer_combo")
        self.gridLayout_2.addWidget(self.layer_combo, 0, 0, 1, 2)
        self.gridLayout_15.addWidget(self.easings_group, 0, 0, 1, 1)
        self.settings_stack.addWidget(self.non_fixed_extent_settings)
        self.fixed_extent_settings = QtWidgets.QWidget()
        self.fixed_extent_settings.setObjectName("fixed_extent_settings")
        self.gridLayout_16 = QtWidgets.QGridLayout(self.fixed_extent_settings)
        self.gridLayout_16.setObjectName("gridLayout_16")
        self.extent_label = QtWidgets.QLabel(self.fixed_extent_settings)
        self.extent_label.setObjectName("extent_label")
        self.gridLayout_16.addWidget(self.extent_label, 0, 0, 1, 1)
        self.extent_group_box = gui.QgsExtentGroupBox(self.fixed_extent_settings)
        self.extent_group_box.setObjectName("extent_group_box")
        self.gridLayout_16.addWidget(self.extent_group_box, 1, 0, 1, 2)
        self.extent_frames_label = QtWidgets.QLabel(self.fixed_extent_settings)
        self.extent_frames_label.setObjectName("extent_frames_label")
        self.gridLayout_16.addWidget(self.extent_frames_label, 2, 0, 1, 1)
        self.extent_frames_spin = QtWidgets.QSpinBox(self.fixed_extent_settings)
        self.extent_frames_spin.setMaximum(9000000)
        self.extent_frames_spin.setSingleStep(30)
        self.extent_frames_spin.setObjectName("extent_frames_spin")
        self.gridLayout_16.addWidget(self.extent_frames_spin, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 117, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_16.addItem(spacerItem, 3, 1, 1, 1)
        self.settings_stack.addWidget(self.fixed_extent_settings)
        self.gridLayout_7.addWidget(self.settings_stack, 2, 0, 1, 1)
        self.output_options_group = QtWidgets.QGroupBox(self.frame)
        self.output_options_group.setObjectName("output_options_group")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.output_options_group)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.reuse_cache = QtWidgets.QCheckBox(self.output_options_group)
        self.reuse_cache.setObjectName("reuse_cache")
        self.gridLayout_5.addWidget(self.reuse_cache, 0, 0, 1, 2)
        self.radio_gif = QtWidgets.QRadioButton(self.output_options_group)
        self.radio_gif.setObjectName("radio_gif")
        self.gridLayout_5.addWidget(self.radio_gif, 1, 0, 1, 1)
        self.rad_movie = QtWidgets.QRadioButton(self.output_options_group)
        self.rad_movie.setChecked(True)
        self.rad_movie.setObjectName("rad_movie")
        self.gridLayout_5.addWidget(self.rad_movie, 1, 1, 1, 1)
        self.gridLayout_7.addWidget(self.output_options_group, 3, 0, 1, 1)
        self.output_destination_group = QtWidgets.QGroupBox(self.frame)
        self.output_destination_group.setObjectName("output_destination_group")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.output_destination_group)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.file_label = QtWidgets.QLabel(self.output_destination_group)
        self.file_label.setObjectName("file_label")
        self.gridLayout_6.addWidget(self.file_label, 0, 0, 1, 1)
        self.file_edit = QtWidgets.QLineEdit(self.output_destination_group)
        self.file_edit.setObjectName("file_edit")
        self.gridLayout_6.addWidget(self.file_edit, 0, 1, 1, 1)
        self.file_button = QtWidgets.QToolButton(self.output_destination_group)
        self.file_button.setObjectName("file_button")
        self.gridLayout_6.addWidget(self.file_button, 0, 2, 1, 1)
        self.gridLayout_7.addWidget(self.output_destination_group, 4, 0, 1, 1)
        self.gridLayout_9.addWidget(self.frame, 0, 0, 1, 1)
        self.preview_frame = QtWidgets.QFrame(animation_workbench_base)
        self.preview_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.preview_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.preview_frame.setLineWidth(0)
        self.preview_frame.setObjectName("preview_frame")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.preview_frame)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.output_log_label = QtWidgets.QLabel(self.preview_frame)
        self.output_log_label.setObjectName("output_log_label")
        self.gridLayout_3.addWidget(self.output_log_label, 2, 0, 1, 1)
        self.preview_stack = QtWidgets.QStackedWidget(self.preview_frame)
        self.preview_stack.setObjectName("preview_stack")
        self.preview_page = QtWidgets.QWidget()
        self.preview_page.setObjectName("preview_page")
        self.gridLayout_11 = QtWidgets.QGridLayout(self.preview_page)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.current_frame_preview_label = QtWidgets.QLabel(self.preview_page)
        self.current_frame_preview_label.setObjectName("current_frame_preview_label")
        self.gridLayout_11.addWidget(self.current_frame_preview_label, 0, 0, 1, 1)
        self.current_frame_preview = QtWidgets.QLabel(self.preview_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.current_frame_preview.sizePolicy().hasHeightForWidth())
        self.current_frame_preview.setSizePolicy(sizePolicy)
        self.current_frame_preview.setMinimumSize(QtCore.QSize(250, 150))
        self.current_frame_preview.setMaximumSize(QtCore.QSize(9999999, 999999))
        self.current_frame_preview.setText("")
        self.current_frame_preview.setScaledContents(True)
        self.current_frame_preview.setAlignment(QtCore.Qt.AlignCenter)
        self.current_frame_preview.setObjectName("current_frame_preview")
        self.gridLayout_11.addWidget(self.current_frame_preview, 1, 0, 1, 1)
        self.preview_stack.addWidget(self.preview_page)
        self.video_page = QtWidgets.QWidget()
        self.video_page.setObjectName("video_page")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.video_page)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.video_preview_label = QtWidgets.QLabel(self.video_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.video_preview_label.sizePolicy().hasHeightForWidth())
        self.video_preview_label.setSizePolicy(sizePolicy)
        self.video_preview_label.setObjectName("video_preview_label")
        self.gridLayout_12.addWidget(self.video_preview_label, 0, 0, 1, 3)
        self.play_button = QtWidgets.QToolButton(self.video_page)
        self.play_button.setObjectName("play_button")
        self.gridLayout_12.addWidget(self.play_button, 2, 0, 1, 1)
        self.video_preview_widget = QtWidgets.QWidget(self.video_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.video_preview_widget.sizePolicy().hasHeightForWidth())
        self.video_preview_widget.setSizePolicy(sizePolicy)
        self.video_preview_widget.setObjectName("video_preview_widget")
        self.gridLayout_12.addWidget(self.video_preview_widget, 1, 0, 1, 3)
        self.video_slider = QtWidgets.QSlider(self.video_page)
        self.video_slider.setOrientation(QtCore.Qt.Horizontal)
        self.video_slider.setObjectName("video_slider")
        self.gridLayout_12.addWidget(self.video_slider, 2, 1, 1, 1)
        self.preview_stack.addWidget(self.video_page)
        self.gridLayout_3.addWidget(self.preview_stack, 1, 0, 1, 2)
        self.status_stack = QtWidgets.QStackedWidget(self.preview_frame)
        self.status_stack.setObjectName("status_stack")
        self.easing_status_page = QtWidgets.QWidget()
        self.easing_status_page.setObjectName("easing_status_page")
        self.gridLayout_13 = QtWidgets.QGridLayout(self.easing_status_page)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.pan_easing_widget = EasingPreview(self.easing_status_page)
        self.pan_easing_widget.setMinimumSize(QtCore.QSize(250, 150))
        self.pan_easing_widget.setObjectName("pan_easing_widget")
        self.gridLayout_13.addWidget(self.pan_easing_widget, 1, 0, 1, 1)
        self.zoom_easing_widget = EasingPreview(self.easing_status_page)
        self.zoom_easing_widget.setMinimumSize(QtCore.QSize(250, 150))
        self.zoom_easing_widget.setObjectName("zoom_easing_widget")
        self.gridLayout_13.addWidget(self.zoom_easing_widget, 1, 1, 1, 1)
        self.label_easings = QtWidgets.QLabel(self.easing_status_page)
        self.label_easings.setObjectName("label_easings")
        self.gridLayout_13.addWidget(self.label_easings, 0, 0, 1, 1)
        self.status_stack.addWidget(self.easing_status_page)
        self.job_progress_page = QtWidgets.QWidget()
        self.job_progress_page.setObjectName("job_progress_page")
        self.gridLayout_14 = QtWidgets.QGridLayout(self.job_progress_page)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.remaining_features_label = QtWidgets.QLabel(self.job_progress_page)
        self.remaining_features_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.remaining_features_label.setObjectName("remaining_features_label")
        self.gridLayout_14.addWidget(self.remaining_features_label, 3, 0, 1, 1)
        self.total_tasks_lcd = QtWidgets.QLCDNumber(self.job_progress_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.total_tasks_lcd.sizePolicy().hasHeightForWidth())
        self.total_tasks_lcd.setSizePolicy(sizePolicy)
        self.total_tasks_lcd.setObjectName("total_tasks_lcd")
        self.gridLayout_14.addWidget(self.total_tasks_lcd, 0, 0, 1, 1)
        self.completed_label = QtWidgets.QLabel(self.job_progress_page)
        self.completed_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.completed_label.setObjectName("completed_label")
        self.gridLayout_14.addWidget(self.completed_label, 3, 2, 1, 1)
        self.completed_lcd = QtWidgets.QLCDNumber(self.job_progress_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.completed_lcd.sizePolicy().hasHeightForWidth())
        self.completed_lcd.setSizePolicy(sizePolicy)
        self.completed_lcd.setObjectName("completed_lcd")
        self.gridLayout_14.addWidget(self.completed_lcd, 2, 2, 1, 1)
        self.remaining_features_lcd = QtWidgets.QLCDNumber(self.job_progress_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.remaining_features_lcd.sizePolicy().hasHeightForWidth())
        self.remaining_features_lcd.setSizePolicy(sizePolicy)
        self.remaining_features_lcd.setObjectName("remaining_features_lcd")
        self.gridLayout_14.addWidget(self.remaining_features_lcd, 2, 0, 1, 1)
        self.active_lcd = QtWidgets.QLCDNumber(self.job_progress_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.active_lcd.sizePolicy().hasHeightForWidth())
        self.active_lcd.setSizePolicy(sizePolicy)
        self.active_lcd.setObjectName("active_lcd")
        self.gridLayout_14.addWidget(self.active_lcd, 2, 1, 1, 1)
        self.active_label = QtWidgets.QLabel(self.job_progress_page)
        self.active_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.active_label.setObjectName("active_label")
        self.gridLayout_14.addWidget(self.active_label, 3, 1, 1, 1)
        self.total_tasks_label = QtWidgets.QLabel(self.job_progress_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.total_tasks_label.sizePolicy().hasHeightForWidth())
        self.total_tasks_label.setSizePolicy(sizePolicy)
        self.total_tasks_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.total_tasks_label.setObjectName("total_tasks_label")
        self.gridLayout_14.addWidget(self.total_tasks_label, 1, 0, 1, 1)
        self.completed_tasks_lcd = QtWidgets.QLCDNumber(self.job_progress_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.completed_tasks_lcd.sizePolicy().hasHeightForWidth())
        self.completed_tasks_lcd.setSizePolicy(sizePolicy)
        self.completed_tasks_lcd.setObjectName("completed_tasks_lcd")
        self.gridLayout_14.addWidget(self.completed_tasks_lcd, 0, 2, 1, 1)
        self.completed_tasks_label = QtWidgets.QLabel(self.job_progress_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.completed_tasks_label.sizePolicy().hasHeightForWidth())
        self.completed_tasks_label.setSizePolicy(sizePolicy)
        self.completed_tasks_label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.completed_tasks_label.setObjectName("completed_tasks_label")
        self.gridLayout_14.addWidget(self.completed_tasks_label, 1, 2, 1, 1)
        self.status_stack.addWidget(self.job_progress_page)
        self.gridLayout_3.addWidget(self.status_stack, 0, 0, 1, 2)
        self.output_log_text_edit = QtWidgets.QTextEdit(self.preview_frame)
        self.output_log_text_edit.setObjectName("output_log_text_edit")
        self.gridLayout_3.addWidget(self.output_log_text_edit, 3, 0, 1, 2)
        self.gridLayout_9.addWidget(self.preview_frame, 0, 1, 1, 1)
        self.progress_bar = QtWidgets.QProgressBar(animation_workbench_base)
        self.progress_bar.setProperty("value", 24)
        self.progress_bar.setObjectName("progress_bar")
        self.gridLayout_9.addWidget(self.progress_bar, 1, 0, 1, 2)
        self.button_box = QtWidgets.QDialogButtonBox(animation_workbench_base)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Close|QtWidgets.QDialogButtonBox.Help|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")
        self.gridLayout_9.addWidget(self.button_box, 2, 0, 1, 2)
        self.hover_frames_label.setBuddy(self.hover_frames_spin)
        self.feature_frames_label.setBuddy(self.feature_frames_spin)

        self.retranslateUi(animation_workbench_base)
        self.settings_stack.setCurrentIndex(0)
        self.preview_stack.setCurrentIndex(0)
        self.status_stack.setCurrentIndex(0)
        self.button_box.accepted.connect(animation_workbench_base.accept) # type: ignore
        self.button_box.rejected.connect(animation_workbench_base.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(animation_workbench_base)
        animation_workbench_base.setTabOrder(self.scale_range, self.radio_sphere)
        animation_workbench_base.setTabOrder(self.radio_sphere, self.radio_planar)
        animation_workbench_base.setTabOrder(self.radio_planar, self.feature_frames_spin)
        animation_workbench_base.setTabOrder(self.feature_frames_spin, self.hover_frames_spin)
        animation_workbench_base.setTabOrder(self.hover_frames_spin, self.reuse_cache)
        animation_workbench_base.setTabOrder(self.reuse_cache, self.radio_gif)
        animation_workbench_base.setTabOrder(self.radio_gif, self.rad_movie)
        animation_workbench_base.setTabOrder(self.rad_movie, self.file_edit)
        animation_workbench_base.setTabOrder(self.file_edit, self.file_button)
        animation_workbench_base.setTabOrder(self.file_button, self.output_log_text_edit)

    def retranslateUi(self, animation_workbench_base):
        _translate = QtCore.QCoreApplication.translate
        animation_workbench_base.setWindowTitle(_translate("animation_workbench_base", "Dialog"))
        self.render_mode_group.setToolTip(_translate("animation_workbench_base", "The render mode determines the behaviour and type of the animation. \n"
"For \'Sphere\' the coordinate reference system (CRS) will \n"
"be manipulated to create a spinning globe effect. \n"
"For \'Plane\', the CRS will not be altered, but will pan and \n"
"zoom to each point."))
        self.render_mode_group.setTitle(_translate("animation_workbench_base", "Render Mode"))
        self.radio_sphere.setText(_translate("animation_workbench_base", "Sphere"))
        self.radio_planar.setText(_translate("animation_workbench_base", "Planar"))
        self.radio_extent.setText(_translate("animation_workbench_base", "Fixed Extent"))
        self.zoom_range_group.setToolTip(_translate("animation_workbench_base", "The scale range that the animation should \n"
"move through. The smallest scale will be \n"
"the zenith of the animation when it zooms \n"
"out while travelling between points, and the \n"
"largest scale will be the scale used when \n"
"we arrive at each point."))
        self.zoom_range_group.setTitle(_translate("animation_workbench_base", "Zoom Range"))
        self.animation_frames_group.setTitle(_translate("animation_workbench_base", "Animation Frames"))
        self.hover_frames_label.setText(_translate("animation_workbench_base", "Hover frames at each feature"))
        self.feature_frames_label.setText(_translate("animation_workbench_base", "Frames between feature"))
        self.feature_frames_spin.setToolTip(_translate("animation_workbench_base", "This is the number of frames that will be used during\n"
" animation of the dwell period at each feature. \n"
"Video generation is done at 30 frames per \n"
"second, so a value of 30 here would result in a 1 second \n"
"dwell time. \n"
"Set to zero to disable."))
        self.hover_frames_spin.setToolTip(_translate("animation_workbench_base", "This is the number of frames that will \n"
"be used during animation of the motion from \n"
"one point to the next. Video generation \n"
"is done at 30 frames per second, so a value \n"
"of 30 here would result in a 1 second flight time \n"
"between two consecutive points. \n"
"Set to zero to disable."))
        self.framerate_spin.setToolTip(_translate("animation_workbench_base", "When writing to video or gif, \n"
"how many frames per second to use."))
        self.framerate_spin.setSuffix(_translate("animation_workbench_base", " fps"))
        self.label.setText(_translate("animation_workbench_base", "Frame rate per second"))
        self.easings_group.setTitle(_translate("animation_workbench_base", "Animation Layer"))
        self.extent_label.setText(_translate("animation_workbench_base", "Extent"))
        self.extent_frames_label.setText(_translate("animation_workbench_base", "Frames"))
        self.output_options_group.setToolTip(_translate("animation_workbench_base", "Select which output format you would like. \n"
"Regardless of which you choose, a folder \n"
"of images will be created, one image per frame. \n"
"For the GIF export to work, you will \n"
"need to have the ImageMagick \'convert\'  application \n"
"available on your system. For the MP4 option to work, \n"
"you need to have the \'ffmpeg\' application on \n"
"your system."))
        self.output_options_group.setTitle(_translate("animation_workbench_base", "Output Options"))
        self.reuse_cache.setToolTip(_translate("animation_workbench_base", "Will not erase cached images on disk \n"
"and will resume processing from last cached image."))
        self.reuse_cache.setText(_translate("animation_workbench_base", "Re-use cached images where possible"))
        self.radio_gif.setText(_translate("animation_workbench_base", "Animated GIF"))
        self.rad_movie.setText(_translate("animation_workbench_base", "Movie (MP4)"))
        self.output_destination_group.setTitle(_translate("animation_workbench_base", "Output Destination"))
        self.file_label.setText(_translate("animation_workbench_base", "File"))
        self.file_edit.setToolTip(_translate("animation_workbench_base", "The output folder will be populated with \n"
"all of the frames of the animation, and \n"
"the GIF or MP4 as selected above."))
        self.file_button.setText(_translate("animation_workbench_base", "..."))
        self.output_log_label.setText(_translate("animation_workbench_base", "Output Logs"))
        self.current_frame_preview_label.setText(_translate("animation_workbench_base", "Current Frame Preview"))
        self.video_preview_label.setText(_translate("animation_workbench_base", "Video Preview"))
        self.play_button.setText(_translate("animation_workbench_base", ">"))
        self.label_easings.setText(_translate("animation_workbench_base", "Pan and Zoom Easings"))
        self.remaining_features_label.setText(_translate("animation_workbench_base", "Remaining Features"))
        self.completed_label.setText(_translate("animation_workbench_base", "Features Completed"))
        self.active_label.setText(_translate("animation_workbench_base", "Active Tasks"))
        self.total_tasks_label.setText(_translate("animation_workbench_base", "Total Tasks"))
        self.completed_tasks_label.setText(_translate("animation_workbench_base", "Completed Tasks"))
        self.output_log_text_edit.setHtml(_translate("animation_workbench_base", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Cantarell\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
from qgis import gui
from QGISAnimationWorkbench.easing_preview import EasingPreview

# Installing the QGIS Animation Workbench plugin

In this section we explain how to install the plugin.

## Install from plugin manager

To access the QGIS Plugin Manager you simply need to select
`Plugins` ➡ `Manage and Install Plugins...` (**`1`**) in the Menu Toolbar.

![Plugin Repository](img/001_PluginManager_1.png)

Once the QGIS Plugin Manager loads, you need to navigate to the `All` (**`2`**)
tab and type "animation" into the search bar (**`3`**). Select QGIS Animation
Workbench from the list of available plugins and then select `Install Plugin`
(**`4`**).

![Search For and Install Plugin](img/002_SearchForPlugin_1.png)

Once the Animation Workbench is installed, you can access it by clicking on the
`Animation Workbench` icon (**`5`**) in the Plugin Toolbar.

![Launch the Workbench](img/003_AWLaunch_1.png)

> Note if you are on Ubuntu, you may need to install the Qt5 multimedia
libraries.

```bash
sudo apt install PyQt5.QtMultimedia
```

## Manual install from GitHub (tagged release)

To install, visit the [Github
Repository](https://github.com/timlinux/QGISAnimationWorkbench), click on the
`Actions` tab, and click on the `Make QGIS Plugin Zip For Manual Installs`
workflow (the bottom one).

![Install 0000](img/install_0000.png)

Click on the most recent workflow run (the top one).

![Install 0001](img/install_0001.png)

Scroll down on the on the page.

![Install 0002](img/install_0002.png)

And click on `animation_workbench` to download the most recent build of the plugin

![Install 0003](img/install_0003.png)

Download the `animation_workbench.zip` file and open it in QGIS using the plugin
manager as described below.

1. Open QGIS
2. **Plugins ➡ Manage and install plugins ...**
3. Choose the **Install from zip** tab
![image](https://user-images.githubusercontent.com/178003/173777449-a1ddd01e-421a-4dcc-ab98-bb32144de618.png)
4. Select the **animation_workbench.zip** download
5. Click the Install **Plugin button**.

> Note if you are on Ubuntu, you may need to install the Qt5 multimedia
libraries.

```bash
sudo apt install PyQt5.QtMultimedia
```

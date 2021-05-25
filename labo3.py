#!/usr/bin/env python

import vtk


bone_iso_value = 72
skin_iso_value = 50

viewport11 = [0.0, 0.0, 0.5, 0.5]
viewport12 = [0.0, 0.5, 0.5, 1.0]
viewport21 = [0.5, 0.0, 1.0, 0.5]
viewport22 = [0.5, 0.5, 1.0, 1.0]

colors = vtk.vtkNamedColors()

# Reference: https://kitware.github.io/vtk-examples/site/Python/IO/ReadSLC/
reader = vtk.vtkSLCReader()
reader.SetFileName("vw_knee.slc")
reader.Update()


def kneePipeline(viewport):
    boneContourFilter = vtk.vtkContourFilter()
    boneContourFilter.SetInputConnection(reader.GetOutputPort())
    boneContourFilter.SetValue(0, bone_iso_value)

    skinContourFilter = vtk.vtkContourFilter()
    skinContourFilter.SetInputConnection(reader.GetOutputPort())
    skinContourFilter.SetValue(0, skin_iso_value)

    outliner = vtk.vtkOutlineFilter()
    outliner.SetInputConnection(reader.GetOutputPort())
    outliner.Update()

    boxMapper = vtk.vtkPolyDataMapper()
    boxMapper.SetInputConnection(outliner.GetOutputPort())
    boxMapper.SetScalarVisibility(0)

    boneMapper = vtk.vtkPolyDataMapper()
    boneMapper.SetInputConnection(boneContourFilter.GetOutputPort())
    boneMapper.SetScalarVisibility(0)

    skinMapper = vtk.vtkPolyDataMapper()
    skinMapper.SetInputConnection(skinContourFilter.GetOutputPort())
    skinMapper.SetScalarVisibility(0)

    boneActor = vtk.vtkActor()
    boneActor.SetMapper(boneMapper)
    boneActor.GetProperty().SetDiffuse(0.8)
    boneActor.GetProperty().SetDiffuseColor(colors.GetColor3d('Ivory'))
    boneActor.GetProperty().SetSpecular(0.8)
    boneActor.GetProperty().SetSpecularPower(120.0)

    boxActor = vtk.vtkActor()
    boxActor.SetMapper(boxMapper)

    skinActor = vtk.vtkActor()
    skinActor.SetMapper(skinMapper)
    skinActor.GetProperty().SetDiffuse(0.8)
    skinActor.GetProperty().SetDiffuseColor(colors.GetColor3d('Ivory'))
    skinActor.GetProperty().SetSpecular(0.8)
    skinActor.GetProperty().SetSpecularPower(120.0)

    # Create a rendering window and renderer.
    renderer = vtk.vtkRenderer()
    renderer.AddActor(boneActor)
    renderer.AddActor(skinActor)
    renderer.AddActor(boxActor)
    renderer.SetBackground(colors.GetColor3d('SlateGray'))
    renderer.SetViewport(viewport)
    return renderer

ren11 = kneePipeline(viewport11)
ren12 = kneePipeline(viewport12)
ren21 = kneePipeline(viewport21)
ren22 = kneePipeline(viewport22)

renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(ren11)
renderWindow.AddRenderer(ren12)
renderWindow.AddRenderer(ren21)
renderWindow.AddRenderer(ren22)
renderWindow.SetSize(500, 500)

# Create a renderwindowinteractor.
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Pick a good view
cam1 = ren11.GetActiveCamera()
cam1.SetFocalPoint(0.0, 0.0, 0.0)
cam1.SetPosition(0.0, -1.0, 0.0)
cam1.SetViewUp(0.0, 0.0, -1.0)
cam1.Azimuth(-90.0)
ren11.ResetCamera()
ren11.ResetCameraClippingRange()

ren12.SetActiveCamera(cam1)
ren21.SetActiveCamera(cam1)
ren22.SetActiveCamera(cam1)

renderWindow.SetSize(640, 512)
renderWindow.Render()

# Enable user interface interactor.
renderWindowInteractor.Initialize()
renderWindow.Render()
renderWindowInteractor.Start()

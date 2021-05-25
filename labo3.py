#!/usr/bin/env python

import vtk

bone_iso_value = 72
skin_iso_value = 50

viewport11 = [0.0, 0.5, 0.5, 1.0]
viewport12 = [0.5, 0.5, 1.0, 1.0]
viewport21 = [0.0, 0.0, 0.5, 0.5]
viewport22 = [0.5, 0.0, 1.0, 0.5]

colors = vtk.vtkNamedColors()

# Reference: https://kitware.github.io/vtk-examples/site/Python/IO/ReadSLC/
reader = vtk.vtkSLCReader()
reader.SetFileName("vw_knee.slc")
reader.Update()

boneContourFilter = vtk.vtkContourFilter()
boneContourFilter.SetInputConnection(reader.GetOutputPort())
boneContourFilter.SetValue(0, bone_iso_value)

skinContourFilter = vtk.vtkContourFilter()
skinContourFilter.SetInputData(reader.GetOutput())
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

boxActor = vtk.vtkActor()
boxActor.SetMapper(boxMapper)

def create_renderer(viewport, bg_color, *actors):
    renderer = vtk.vtkRenderer()
    for actor in actors:
        renderer.AddActor(actor)
    renderer.AddActor(actor)
    renderer.SetBackground(*bg_color)
    renderer.SetViewport(viewport)
    return renderer

def upper_left(viewport):
    # Create the bone actor
    boneActor = vtk.vtkActor()
    boneActor.SetMapper(boneMapper)
    boneActor.GetProperty().SetDiffuseColor(colors.GetColor3d('Ivory'))

    # Create the plane to cut the skin
    plane = vtk.vtkPlane()
    plane.SetNormal(0, 0, 1)
    plane.SetOrigin(0, 0, 0)

    # Cut the skin with the plan
    cutter = vtk.vtkCutter()
    cutter.SetInputData(skinMapper.GetInput())
    cutter.SetCutFunction(plane)
    cutter.GenerateValues(25, 0, 200)

    # Strip the output of the cutter
    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(cutter.GetOutputPort())

    # Pass the output of the stripper through a tube filter
    tubeFilter = vtk.vtkTubeFilter()
    tubeFilter.SetRadius(1)
    tubeFilter.SetInputConnection(stripper.GetOutputPort())

    # Create the lines mapper
    linesMapper = vtk.vtkPolyDataMapper()
    linesMapper.ScalarVisibilityOff()
    linesMapper.SetInputConnection(tubeFilter.GetOutputPort())

    # Create the lines actor
    linesActor = vtk.vtkActor()
    linesActor.SetMapper(linesMapper)
    linesActor.GetProperty().SetColor([0.81,0.63,0.62])    

    return create_renderer(viewport, [1.00,0.82,0.82], boneActor, linesActor)

def upper_right(viewport):
    boneActor = vtk.vtkActor()
    boneActor.SetMapper(boneMapper)
    boneActor.GetProperty().SetColor(colors.GetColor3d('White'))

    skinActor = vtk.vtkActor()
    skinActor.SetMapper(skinMapper)
    skinActor.GetProperty().SetDiffuse(0.8)
    skinActor.GetProperty().SetDiffuseColor(colors.GetColor3d('Ivory'))
    skinActor.GetProperty().SetSpecular(0.8)
    skinActor.GetProperty().SetSpecularPower(120.0)
    return create_renderer(viewport, [0.82,1.00,0.82], boneActor, skinActor)

def lower_left(viewport):
    pass

def lower_right(viewport):
    pass

def kneePipeline(viewport, test):
    boneActor = vtk.vtkActor()
    boneActor.SetMapper(boneMapper)
    boneActor.GetProperty().SetDiffuse(test)
    boneActor.GetProperty().SetDiffuseColor(colors.GetColor3d('Ivory'))
    boneActor.GetProperty().SetSpecular(test)
    boneActor.GetProperty().SetSpecularPower(120.0)

    skinActor = vtk.vtkActor()
    skinActor.SetMapper(skinMapper)
    skinActor.GetProperty().SetDiffuse(test)
    skinActor.GetProperty().SetDiffuseColor(colors.GetColor3d('Ivory'))
    skinActor.GetProperty().SetSpecular(test)
    skinActor.GetProperty().SetSpecularPower(120.0)

    # Create a rendering window and renderer.
    return create_renderer(viewport, colors.GetColor3d('SlateGray'), boneActor, skinActor, boxActor)
    

ren11 = upper_left(viewport11)
ren12 = upper_right(viewport12)
ren21 = kneePipeline(viewport21,0.55)
ren22 = kneePipeline(viewport22,0.8)

# Pour le dernier, utiliser vtkImplicitPolyDataDistance (https://youtu.be/gBdo2OrVAyk?t=362)

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

renderWindow.SetSize(800, 800)
renderWindow.Render()

# Enable user interface interactor.
renderWindowInteractor.Initialize()
renderWindow.Render()
renderWindowInteractor.Start()

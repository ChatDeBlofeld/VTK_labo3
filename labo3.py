#!/usr/bin/env python

import vtk

bone_iso_value = 72
skin_iso_value = 50

(0.0, 0.5, 0.0, 0.5, 0.0, 1.0)
# (xmin, ymin, xmax, ymax)
viewport11 = [0.0, 0.5, 0.5, 1.0]
viewport12 = [0.5, 0.5, 1.0, 1.0]
viewport21 = [0.0, 0.0, 0.5, 0.5]
viewport22 = [0.5, 0.0, 1.0, 0.5]

colors = vtk.vtkNamedColors()

skinColor = [0.81,0.63,0.62]

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

skinClipFunction = vtk.vtkSphere()
skinClipFunction.SetRadius(45)
skinClipFunction.SetCenter(70,30,110)

skinClip = vtk.vtkClipPolyData()
skinClip.SetClipFunction(skinClipFunction)
skinClip.SetInputConnection(skinContourFilter.GetOutputPort())

skinClipMapper = vtk.vtkPolyDataMapper()
skinClipMapper.SetInputConnection(skinClip.GetOutputPort())
skinClipMapper.SetScalarVisibility(0)

boxActor = vtk.vtkActor()
boxActor.SetMapper(boxMapper)

def create_renderer(viewport, bg_color, *actors):
    renderer = vtk.vtkRenderer()
    for actor in actors:
        renderer.AddActor(actor)
    renderer.AddActor(boxActor)
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
    skinActor.SetMapper(skinClipMapper)
    skinActor.GetProperty().SetColor(skinColor)
    skinActor.GetProperty().SetOpacity(0.5)
    skinActor.SetBackfaceProperty(skinActor.MakeProperty())
    skinActor.GetBackfaceProperty().SetColor(skinColor)

    return create_renderer(viewport, [0.82,1.00,0.82], boneActor, skinActor)

def lower_left(viewport):
    # Create the bone actor
    boneActor = vtk.vtkActor()
    boneActor.SetMapper(boneMapper)
    boneActor.GetProperty().SetColor(colors.GetColor3d('White'))

    # Create the skin actor
    skinActor = vtk.vtkActor()
    skinActor.SetMapper(skinClipMapper)
    skinActor.GetProperty().SetColor(skinColor)

    # Create a sample function from the implicit function
    sampleFunction = vtk.vtkSampleFunction()
    sampleFunction.SetImplicitFunction(skinClipFunction)
    sampleFunction.SetModelBounds(0.0, 200, -30, 200, 0.0, 200)

    # Pass the sample function through a contourFilter to create a polydata
    contourFilter = vtk.vtkContourFilter()
    contourFilter.SetInputConnection(sampleFunction.GetOutputPort())

    # Create a mapper for the sphere actor
    sphereMapper = vtk.vtkPolyDataMapper()
    sphereMapper.SetInputConnection(contourFilter.GetOutputPort())
    sphereMapper.ScalarVisibilityOff()

    # Create the sphere actor
    sphereActor = vtk.vtkActor()
    sphereActor.SetMapper(sphereMapper)
    sphereActor.GetProperty().SetColor(colors.GetColor3d('PaleGoldenrod'))
    sphereActor.GetProperty().SetOpacity(0.3)

    return create_renderer(viewport, [0.82,0.82,1.00], boneActor, skinActor, sphereActor)

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
    return create_renderer(viewport, colors.GetColor3d('SlateGray'), boneActor, skinActor)
    

ren11 = upper_left(viewport11)
ren12 = upper_right(viewport12)
ren21 = lower_left(viewport21)
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

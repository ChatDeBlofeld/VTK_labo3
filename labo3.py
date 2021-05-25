#!/usr/bin/env python

import vtk


iso_value = 72

colors = vtk.vtkNamedColors()

# vtkSLCReader to read.
reader = vtk.vtkSLCReader()
reader.SetFileName("vw_knee.slc")
reader.Update()

# Create a mapper.
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(reader.GetOutputPort())

# Implementing Marching Cubes Algorithm to create the surface using vtkContourFilter object.
contourFilter = vtk.vtkContourFilter()
contourFilter.SetInputConnection(reader.GetOutputPort())
# Change the range(2nd and 3rd Paramater) based on your
# requirement. recomended value for 1st parameter is above 1
# contourFilter.GenerateValues(5, 80.0, 100.0)
contourFilter.SetValue(0, iso_value)

outliner = vtk.vtkOutlineFilter()
outliner.SetInputConnection(reader.GetOutputPort())
outliner.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(contourFilter.GetOutputPort())
mapper.SetScalarVisibility(0)

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetDiffuse(0.8)
actor.GetProperty().SetDiffuseColor(colors.GetColor3d('Ivory'))
actor.GetProperty().SetSpecular(0.8)
actor.GetProperty().SetSpecularPower(120.0)

# Create a rendering window and renderer.
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(500, 500)

# Create a renderwindowinteractor.
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Assign actor to the renderer.
renderer.AddActor(actor)
renderer.SetBackground(colors.GetColor3d('SlateGray'))

# Pick a good view
cam1 = renderer.GetActiveCamera()
cam1.SetFocalPoint(0.0, 0.0, 0.0)
cam1.SetPosition(0.0, -1.0, 0.0)
cam1.SetViewUp(0.0, 0.0, -1.0)
cam1.Azimuth(-90.0)
renderer.ResetCamera()
renderer.ResetCameraClippingRange()

renderWindow.SetWindowName('ReadSLC')
renderWindow.SetSize(640, 512)
renderWindow.Render()

# Enable user interface interactor.
renderWindowInteractor.Initialize()
renderWindow.Render()
renderWindowInteractor.Start()




""" import vtk as vtk



renderer = vtk.vtkRenderer()
#renderer.GetActiveCamera().SetFocalPoint(*FOCAL_POINT)
#renderer.GetActiveCamera().SetPosition(*CAMERA_POSITION)
renderer.GetActiveCamera().SetClippingRange(0.1, 1_000_000) 

renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(renderer)
renWin.SetSize(800, 800)


reader = vtk.vtkSLCReader()
reader.SetFileName("vw_knee.slc")

mc = vtk.vtkMarchingCubes()
mc.SetInput(reader.GetOutput())

mapper = vtk.vtkPolyDataMapper()
mapper.SetInput(mc.GetOutput())
mapper.ScalarVisibilityOff()

actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer.AddActor(actor)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

style = vtk.vtkInteractorStyleTrackballCamera()
iren.SetInteractorStyle(style)

iren.Initialize()
iren.Render()
iren.Start() """
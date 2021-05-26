#!/usr/bin/env python

import vtk
import os.path

# Constants

BONE_ISO_VALUE = 72
SKIN_ISO_VALUE = 50

BONE_DISTANCES_PATH = "bone_distances.vtk"

# (xmin, ymin, xmax, ymax)
VIEWPORT11 = [0.0, 0.5, 0.5, 1.0]
VIEWPORT12 = [0.5, 0.5, 1.0, 1.0]
VIEWPORT21 = [0.0, 0.0, 0.5, 0.5]
VIEWPORT22 = [0.5, 0.0, 1.0, 0.5]

UPPER_LEFT_BG_COLOR = [1.00,0.82,0.82]
UPPER_RIGHT_BG_COLOR = [0.82,1.00,0.82]
LOWER_LEFT_BG_COLOR = [0.82,0.82,1.00]
LOWER_RIGHT_BG_COLOR = [0.82,0.82,0.82]

COLORS = vtk.vtkNamedColors()

SKIN_COLOR = [0.81,0.63,0.62]
BONE_COLOR = COLORS.GetColor3d('Ivory')



# Set of functions to create the specific renderers

def create_renderer(viewport, bg_color, *actors):
    renderer = vtk.vtkRenderer()
    for actor in actors:
        renderer.AddActor(actor)
    renderer.AddActor(boxActor)
    renderer.SetBackground(*bg_color)
    renderer.SetViewport(viewport)
    return renderer

def upper_left(viewport):
    # Create the mapper
    skinMapper = vtk.vtkPolyDataMapper()
    skinMapper.SetInputConnection(skinContourFilter.GetOutputPort())
    skinMapper.SetScalarVisibility(0)

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
    linesActor.GetProperty().SetColor(SKIN_COLOR)    

    return create_renderer(viewport, UPPER_LEFT_BG_COLOR, boneActor, linesActor)

def upper_right(viewport):
    # Create a skin actor with custom properties (transparency, backfaceCullingOff)
    skinActor = vtk.vtkActor()
    skinActor.SetMapper(skinClipMapper)
    skinActor.GetProperty().SetColor(SKIN_COLOR)
    skinActor.GetProperty().SetOpacity(0.5)
    skinActor.SetBackfaceProperty(skinActor.MakeProperty())
    skinActor.GetBackfaceProperty().SetColor(SKIN_COLOR)

    return create_renderer(viewport, UPPER_RIGHT_BG_COLOR, boneActor, skinActor)

def lower_left(viewport):
    # Create the skin actor
    skinActor = vtk.vtkActor()
    skinActor.SetMapper(skinClipMapper)
    skinActor.GetProperty().SetColor(SKIN_COLOR)

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
    sphereActor.GetProperty().SetColor(COLORS.GetColor3d('PaleGoldenrod'))
    sphereActor.GetProperty().SetOpacity(0.3)

    return create_renderer(viewport, LOWER_LEFT_BG_COLOR, boneActor, skinActor, sphereActor)

def lower_right(viewport):
    distanceMapper = vtk.vtkDataSetMapper()
    distanceMapper.SetInputConnection(boneOutputPort)
    # Comment connaître la range ? Possible d'update mais performance ?
    # + warning thread-safe je sais pas quoi
    distanceMapper.SetScalarRange(0,50)

    boneActor = vtk.vtkActor()
    boneActor.SetMapper(distanceMapper)
    return create_renderer(viewport, LOWER_RIGHT_BG_COLOR, boneActor)



# Reading and creating common assets
# Reference: https://kitware.github.io/vtk-examples/site/Python/IO/ReadSLC/
reader = vtk.vtkSLCReader()
reader.SetFileName("vw_knee.slc")

skinContourFilter = vtk.vtkContourFilter()
skinContourFilter.SetInputConnection(reader.GetOutputPort())
skinContourFilter.SetValue(0, SKIN_ISO_VALUE)

boneOutputPort = 0
if os.path.isfile(BONE_DISTANCES_PATH):
    grid = vtk.vtkUnstructuredGrid()

    boneReader = vtk.vtkUnstructuredGridReader()
    boneReader.SetFileName(BONE_DISTANCES_PATH)
    boneReader.SetOutput(grid)
    boneReader.ReadAllScalarsOn()

    boneOutputPort = boneReader.GetOutputPort()    
else:
    # Getting bone mesh
    boneContourFilter = vtk.vtkContourFilter()
    boneContourFilter.SetInputConnection(reader.GetOutputPort())
    boneContourFilter.SetValue(0, BONE_ISO_VALUE)

    # Compute distance to skin
    distanceFilter = vtk.vtkDistancePolyDataFilter()
    distanceFilter.SignedDistanceOff()
    distanceFilter.SetInputConnection(0, boneContourFilter.GetOutputPort())
    distanceFilter.SetInputConnection(1, skinContourFilter.GetOutputPort())

    # Remove ugly pipe
    range = vtk.vtkIntArray()
    range.InsertNextTuple1(2.5)
    range.InsertNextTuple1(60)

    filterCells = vtk.vtkSelectionNode()
    filterCells.SetContentType(7)
    filterCells.SetFieldType(0)
    filterCells.SetSelectionList(range)

    sel = vtk.vtkSelection()
    sel.SetNode("cells", filterCells)

    cleaner = vtk.vtkExtractSelection()
    cleaner.SetInputConnection(0, distanceFilter.GetOutputPort())
    cleaner.SetInputData(1, sel)
    cleaner.Update()

    # Write to file for later launch
    writer = vtk.vtkUnstructuredGridWriter()
    writer.SetFileName(BONE_DISTANCES_PATH)
    writer.SetFileTypeToBinary()
    writer.SetInputData(cleaner.GetOutput())
    writer.Write()

    boneOutputPort = cleaner.GetOutputPort()

# Create bounding box actor for the scan data
outliner = vtk.vtkOutlineFilter()
outliner.SetInputConnection(reader.GetOutputPort())

boxMapper = vtk.vtkPolyDataMapper()
boxMapper.SetInputConnection(outliner.GetOutputPort())
boxMapper.SetScalarVisibility(0)

boxActor = vtk.vtkActor()
boxActor.SetMapper(boxMapper)
boxActor.GetProperty().SetColor(COLORS.GetColor3d('Black'))

# Create a bone actor with the default mapper
boneDefaultMapper = vtk.vtkDataSetMapper()
boneDefaultMapper.SetInputConnection(boneOutputPort)
boneDefaultMapper.SetScalarVisibility(0)

boneActor = vtk.vtkActor()
boneActor.SetMapper(boneDefaultMapper)
boneActor.GetProperty().SetColor(BONE_COLOR)

# Create a skin mapper clipping the knee area with a sphere
skinClipFunction = vtk.vtkSphere()
skinClipFunction.SetRadius(45)
skinClipFunction.SetCenter(70,30,110)

skinClip = vtk.vtkClipPolyData()
skinClip.SetClipFunction(skinClipFunction)
skinClip.SetInputConnection(skinContourFilter.GetOutputPort())

skinClipMapper = vtk.vtkPolyDataMapper()
skinClipMapper.SetInputConnection(skinClip.GetOutputPort())
skinClipMapper.SetScalarVisibility(0)



# Display !

ren11 = upper_left(VIEWPORT11)
ren12 = upper_right(VIEWPORT12)
ren22 = lower_right(VIEWPORT22)
ren21 = lower_left(VIEWPORT21)

renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(ren11)
renderWindow.AddRenderer(ren12)
renderWindow.AddRenderer(ren21)
renderWindow.AddRenderer(ren22)
renderWindow.SetSize(800, 800)

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

# Enable user interface interactor.
renderWindowInteractor.Initialize()
renderWindow.Render()
renderWindowInteractor.Start()

#!/usr/bin/env python

import vtk
import os.path
import itertools

# Constants

BONE_ISO_VALUE = 72
SKIN_ISO_VALUE = 50
BONE_MIN_DIST_TO_SKIN = 2.5

DATA_PATH = "vw_knee.slc"
BONE_DISTANCES_PATH = "bone_distances.vtk"
SCALAR_RANGE_PATH = "scalar_range"

WINDOW_SIZE = (800, 800)

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
BOUNDING_BOX_COLOR = COLORS.GetColor3d('Black')

CLIP_SPHERE_RADIUS = 45
CLIP_SPHERE_CENTER = [70,30,110]

UP_L_NB_LINES = 25
UP_L_TUBE_RADIUS = 1
UP_R_SKIN_OPACITY = 0.5
LO_L_SPHERE_COLOR = COLORS.GetColor3d('PaleGoldenrod')
LO_L_SPHERE_OPACITY = 0.3


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
    skinMapper.ScalarVisibilityOff()

    # Create the plane to cut the skin
    plane = vtk.vtkPlane()
    plane.SetNormal(0, 0, 1)
    plane.SetOrigin(0, 0, 0)

    # Cut the skin with the plan
    cutter = vtk.vtkCutter()
    cutter.SetInputData(skinMapper.GetInput())
    cutter.SetCutFunction(plane)
    cutter.GenerateValues(UP_L_NB_LINES, 0, 200)

    # Strip the output of the cutter
    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(cutter.GetOutputPort())

    # Pass the output of the stripper through a tube filter
    tubeFilter = vtk.vtkTubeFilter()
    tubeFilter.SetRadius(UP_L_TUBE_RADIUS)
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
    skinActor.GetProperty().SetOpacity(UP_R_SKIN_OPACITY)
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
    bounds = map(lambda x: (x - CLIP_SPHERE_RADIUS * 1.1, x + CLIP_SPHERE_RADIUS * 1.1), CLIP_SPHERE_CENTER)
    bounds = list(itertools.chain(*bounds))
    sampleFunction.SetModelBounds(bounds)

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
    sphereActor.GetProperty().SetColor(LO_L_SPHERE_COLOR)
    sphereActor.GetProperty().SetOpacity(LO_L_SPHERE_OPACITY)

    return create_renderer(viewport, LOWER_LEFT_BG_COLOR, boneActor, skinActor, sphereActor)

def lower_right(viewport):
    distanceMapper = vtk.vtkDataSetMapper()
    distanceMapper.SetInputConnection(boneOutputPort)
    distanceMapper.SetScalarRange(scalarRange)

    boneActor = vtk.vtkActor()
    boneActor.SetMapper(distanceMapper)
    return create_renderer(viewport, LOWER_RIGHT_BG_COLOR, boneActor)



# Reading and creating common assets
# Reference: https://kitware.github.io/vtk-examples/site/Python/IO/ReadSLC/
reader = vtk.vtkSLCReader()
reader.SetFileName(DATA_PATH)

skinContourFilter = vtk.vtkContourFilter()
skinContourFilter.SetInputConnection(reader.GetOutputPort())
skinContourFilter.SetValue(0, SKIN_ISO_VALUE)

# Output port of the vtk pipeline for the bone mesh
# Comes either from a reader if a pre-computed file
# exists or from the pipeline to compute it on the fly
boneOutputPort = 0

# Since we don't want to break the pipeline with unnecessary
# updates, we store the range for the lower left renderer LUT
# in file. So it comes either from a file or is computed on
# the fly as 'boneOutputPort'
scalarRange = (0,1)

# Pre-computed files exist for bones, we just need to read them.
if os.path.isfile(BONE_DISTANCES_PATH) and os.path.isfile(SCALAR_RANGE_PATH):
    # Reading mesh
    mesh = vtk.vtkPolyData()

    boneReader = vtk.vtkPolyDataReader()
    boneReader.SetFileName(BONE_DISTANCES_PATH)
    boneReader.SetOutput(mesh)
    boneReader.ReadAllScalarsOn()

    boneOutputPort = boneReader.GetOutputPort()

    # Reading scalar range for the lower right viewport LUT
    with open(SCALAR_RANGE_PATH) as file:
        # WARNING: USING EVAL AS SUCH IS A HUGE SECURITY BREACH
        #
        # But we don't care. This is an academic work not focusing on security
        # nor intended to be used in production and eval clearly is
        # the easiest way to read a tuple from a file we've generated.
        # 
        # Just don't accept our 'scalar_range' file (if provided)
        # without checking its content, it may contain some malicious code
        # to set a '6' to every VTK students.
        #
        # If you want to have some fun and see how bad this is, replace 
        # the generated 'scalar_range' file content with this line:
        # exec("from tkinter import Tk, messagebox; root = Tk(); root.withdraw(); messagebox.showinfo('This is a cryptolocker', 'You ve been hacked. Sad life isn t it?')")
        scalarRange = eval(file.readline().strip())
# No pre-computed files, we need to compute the mesh on the fly
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
    range = vtk.vtkDoubleArray()
    range.SetNumberOfComponents(2)
    range.SetNumberOfTuples(1)
    range.FillComponent(0, BONE_MIN_DIST_TO_SKIN)
    range.FillComponent(1, float("inf"))

    filterCells = vtk.vtkSelectionNode()
    filterCells.SetContentType(7) # 7 is enum id for Threshold selection
    filterCells.SetFieldType(0)  # 0 is enum id for Cell type
    filterCells.SetSelectionList(range)

    selector = vtk.vtkSelection()
    selector.SetNode("cells", filterCells)

    cleaner = vtk.vtkExtractSelection()
    cleaner.SetInputConnection(0, distanceFilter.GetOutputPort())
    cleaner.SetInputData(1, selector)

    # Getting polydata back
    converter = vtk.vtkGeometryFilter()
    converter.SetInputConnection(cleaner.GetOutputPort())
    converter.Update()

    # Write to file for later launches
    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(BONE_DISTANCES_PATH)
    writer.SetFileTypeToBinary()
    writer.SetInputData(converter.GetOutput())
    writer.Write()

    # Write the scalar range of the distances
    # for a later usage in the LUT parameters
    with open(SCALAR_RANGE_PATH, "w") as file:
        scalarRange = converter.GetOutput().GetScalarRange()
        file.write(str(scalarRange))

    boneOutputPort = converter.GetOutputPort()

# Create bounding box actor for the scan data
outliner = vtk.vtkOutlineFilter()
outliner.SetInputConnection(reader.GetOutputPort())

boxMapper = vtk.vtkPolyDataMapper()
boxMapper.SetInputConnection(outliner.GetOutputPort())
boxMapper.ScalarVisibilityOff()

boxActor = vtk.vtkActor()
boxActor.SetMapper(boxMapper)
boxActor.GetProperty().SetColor(BOUNDING_BOX_COLOR)

# Create a bone actor with the default mapper
boneDefaultMapper = vtk.vtkPolyDataMapper()
boneDefaultMapper.SetInputConnection(boneOutputPort)
boneDefaultMapper.ScalarVisibilityOff()

boneActor = vtk.vtkActor()
boneActor.SetMapper(boneDefaultMapper)
boneActor.GetProperty().SetColor(BONE_COLOR)

# Create a skin mapper clipping the knee area with a sphere
skinClipFunction = vtk.vtkSphere()
skinClipFunction.SetRadius(CLIP_SPHERE_RADIUS)
skinClipFunction.SetCenter(CLIP_SPHERE_CENTER)

skinClip = vtk.vtkClipPolyData()
skinClip.SetClipFunction(skinClipFunction)
skinClip.SetInputConnection(skinContourFilter.GetOutputPort())

skinClipMapper = vtk.vtkPolyDataMapper()
skinClipMapper.SetInputConnection(skinClip.GetOutputPort())
skinClipMapper.ScalarVisibilityOff()



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
renderWindow.SetSize(WINDOW_SIZE)

# Create a renderwindowinteractor.
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Pick a good view
cam1 = ren11.GetActiveCamera()
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

import vtk
import random


def get_unique_colors(num_colors):
    # Generate unique colors
    colors = []
    for i in range(num_colors):
        colors.append((random.random(), random.random(), random.random()))
    return colors


def save_rendering(filename, triangles, regions):
    # Initialize rendering window and renderer
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    # Enable off-screen rendering
    render_window.SetOffScreenRendering(1)
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    unique_colors = get_unique_colors(len(regions))

    # deal with each region
    for region_id, region_triangles in enumerate(regions):
        points = vtk.vtkPoints()
        polys = vtk.vtkCellArray()

        # deal with each triangle in the region
        for tri_id in region_triangles:
            tri = triangles[tri_id]
            triangle = vtk.vtkTriangle()

            for i in range(3):
                point_id = points.InsertNextPoint(tri[i][:3])
                triangle.GetPointIds().SetId(i, point_id)

            polys.InsertNextCell(triangle)

        # Create a polydata object
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetPolys(polys)

        # Create a mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(unique_colors[region_id])
        renderer.AddActor(actor)

    # Set background color, e.g., dark blue
    renderer.SetBackground(0.1, 0.2, 0.4)
    # Perform off-screen rendering
    render_window.Render()

    # Capture the render window
    window_to_image_filter = vtk.vtkWindowToImageFilter()
    window_to_image_filter.SetInput(render_window)
    window_to_image_filter.Update()

    # Save the rendering result
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(filename)
    writer.SetInputConnection(window_to_image_filter.GetOutputPort())
    writer.Write()

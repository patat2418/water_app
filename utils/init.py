
def init (acad):

    grid_layer = acad.ActiveDocument.Layers.Add("grid")
    grid_text_layer = acad.ActiveDocument.Layers.Add("grid_text")
    pipe_layer = acad.ActiveDocument.Layers.Add("pipe")
    pipe_guideline_layer = acad.ActiveDocument.Layers.Add("pipe_guideline")
    pipe_text_layer = acad.ActiveDocument.Layers.Add("pipe_text")
    energy_line_layer = acad.ActiveDocument.Layers.Add("energy_line")

    grid_layer.color = 7
    grid_text_layer.color = 7
    pipe_layer.color = 5
    pipe_guideline_layer.color = 8
    pipe_text_layer.color = 7
    energy_line_layer.color = 6
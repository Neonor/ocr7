from bokeh.layouts import column, row, layout
import bokeh.models as mb

class Dashboard(object):
    def __init__(self,doc):

        heading = mb.Div(text="""<h2 title="by rloriot">Home</h2>""", sizing_mode="stretch_width")
        self.footing = mb.Div(text="""<i style="right=0">by rloriot</i>""", sizing_mode="stretch_width")
        doc.add_root(column(heading,mb.Button(label="Test"),sizing_mode="stretch_width"))

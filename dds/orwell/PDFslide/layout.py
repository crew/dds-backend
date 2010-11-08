import clutter
import baseslide
import config
import logging
import json

class PDFSlide(baseslide.BaseSlide):
    def __init__(self):

        baseslide.BaseSlide.__init__(self)

        pdf_img = clutter.Texture( 'pdf.png' )
        pdf_img.set_position(0,0)
        pdf_img.set_size(1920,1080)
        self.group.add(pdf_img)

app = PDFSlide()
slide = app.group

    

# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
import clutter
import baseslide
import config
import logging
import json

class ACMTalks(baseslide.BaseSlide):
    def __init__(self):

        file = open('data.js', 'r')
        data = json.load(open('data.js'))

        desc_text = data.get('body', 'body should be here')
        date = data.get('date', 'date should be here')
        title_text = data.get('name', 'title should be here')
        time = data.get('time', 'time should be here')

        baseslide.BaseSlide.__init__(self)
        bg = clutter.Rectangle()
        bg.set_color(clutter.color_from_string('#6a9cd2'))
        bg.set_size(1920, 1080)
        bg.set_position(0, 0)
        bg.set_depth(1)
        self.group.add(bg)

        sunbeams = clutter.Texture('sunbeams.png')
        sunbeams.set_position(-800, -500)
        sunbeams.set_depth(2)
        self.group.add(sunbeams)

        acmlogo = clutter.Texture('nuacmlogo.png')
        acmlogo.set_position(50, 50)
        acmlogo.set_depth(3)
        self.group.add(acmlogo)

        skyline = clutter.Texture('skyline_blue.png')
        skyline.set_size(952, 436)
        skyline.set_position(1920-952, 1080-436)
        skyline.set_depth(3)
        self.group.add(skyline)

        stripe = clutter.Rectangle()
        stripe.set_color(clutter.color_from_string('#ffffff'))
        stripe.set_size(1920, 200)
        stripe.set_position(0, 250)
        stripe.set_opacity(30)
        stripe.set_depth(3)
        self.group.add(stripe)

        eventtitle = clutter.Text()
        eventtitle.set_text(title_text);
        eventtitle.set_font_name('serif 58')
        eventtitle.set_color(clutter.color_from_string('#ffffff'))
        eventtitle.set_size(1920, 200)
        eventtitle.set_position(50, 290)
        eventtitle.set_depth(3)
        self.group.add(eventtitle)

        descblock = clutter.Text()
        descblock.set_text(desc_text)
        descblock.set_font_name('serif 24')
        descblock.set_color(clutter.color_from_string('#ffffff'))
        descblock.set_position(20, 470)
        descblock.set_size(1200, 500)
        descblock.set_depth(3)
        descblock.set_line_wrap(True)
        self.group.add(descblock)

        dateline = clutter.Text()
        dateline.set_text(date);
        dateline.set_font_name('serif 60')
        dateline.set_color(clutter.color_from_string('#ffffff'))
        dateline.set_position(1000, 40)
        dateline.set_size(820, 300)
        dateline.set_depth(3)
        self.group.add(dateline)

        timeline = clutter.Text()
        timeline.set_text(time);
        timeline.set_font_name('serif 48')
        timeline.set_color(clutter.color_from_string('#ffffff'))
        timeline.set_position(1000, 150)
        timeline.set_size(1200, 300)
        timeline.set_depth(3)
        self.group.add(timeline)

        
        
    
app = ACMTalks()
slide = app.group

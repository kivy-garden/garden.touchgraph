# !/usr/bin/env python
# -*- coding: utf-8 -*-

from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.graphics.scissor_instructions import ScissorPush, ScissorPop
from kivy.properties import ListProperty, NumericProperty
from kivy.core.text import Label as CoreLabel
from kivy.clock import Clock

__all__ = 'TouchGraph'


class TouchGraph(FloatLayout):
    pointColor = ListProperty([.5, 1, .5, 1])
    lineColor = ListProperty([1, 1, .5, 1])
    backColor = ListProperty([.3, .3, .3, 1])
    points = ListProperty()
    font_size = NumericProperty()
    line_width = NumericProperty()
    y_ticks = ListProperty()
    x_ticks = ListProperty()
    y_labels = ListProperty()
    x_labels = ListProperty()
    max_y = NumericProperty(0)
    tickWidthFactor = 0.5
    circleDiameterFactor = 6

    @staticmethod
    def y_for_x(x, points):
        if points:
            pts = []
            pts.extend(points)
            for i, p in enumerate(zip(pts[::2], pts[1::2])):
                if p[0] > x:
                    r = (pts[::2][i - 1], pts[1::2][i - 1])
                    slope = (p[1] - r[1]) / (p[0] - r[0])
                    y = r[1] + slope * (x - r[0])
                    return y
            slope = (pts[-1] - pts[-3]) / (pts[-2] - pts[-4])
            y = pts[-3] + slope * (x - pts[-4])
            return y

    def __init__(self, **kwargs):
        super(TouchGraph, self).__init__(**kwargs)
        if len(self.points) > 0:
            self.late_init()
        else:
            self.bind(points=self.late_init)

    def late_init(self, *args):
        del args
        if self.canvas is None:
            Clock.schedule_once(self.late_init(), 0)
            return
        self.padding_x = .5 * self.line_width * TouchGraph.circleDiameterFactor
        self.padding_y = 0
        if len(self.points[::2]) < 2:
            raise ValueError('Need more than 1 point')
        for i, p in enumerate(self.points[2::2]):
            if p < self.points[::2][i]:
                raise ValueError('self.Points must be ascending on x-Axis')
        self.max = [max(self.points[::2]), max(self.points[1::2])]
        if self.max_y > 0:
            if self.max[1] > self.max_y:
                raise ValueError('not all points are visible on y axis')
            else:
                self.max[1] = self.max_y
        self.current_point = None  # index of point being dragged
        with self.canvas:
            self.scissor = ScissorPush(x=int(round(self.to_window(*self.pos)[0])),
                                       y=int(round(self.to_window(*self.pos)[1])),
                                       width=int(round(self.width)),
                                       height=int(round(self.height)))
            Color(*self.backColor)
            self.back = Rectangle(pos=self.pos, size=self.size)
            self.xTickRects = []
            self.xTickLabels = []
            Color(*self.lineColor)
            for i, p in enumerate(self.x_ticks):
                x = self.graph_x_for_x(p)
                self.xTickRects.append(Rectangle(pos=(x - (TouchGraph.tickWidthFactor / 2) * self.line_width, 0), size=(
                    TouchGraph.tickWidthFactor * self.line_width, 4 * TouchGraph.tickWidthFactor * self.line_width)))
                # use text on canvas https://groups.google.com/forum/#!topic/kivy-users/zRCjfhBcX4c
                text = p if not self.x_labels else self.x_labels[i]
                tick_label = CoreLabel(text=text, font_size=self.font_size, color=self.lineColor)
                tick_label.refresh()
                texture = tick_label.texture
                texture_size = list(texture.size)
                self.xTickLabels.append(
                    Rectangle(pos=(x - texture_size[0] / 2, 6 * TouchGraph.tickWidthFactor * self.line_width),
                              texture=texture, size=texture_size))
            self.yTickRects = []
            self.yTickLabels = []
            for i, p in enumerate(self.y_ticks):
                y = self.graph_y_for_y(p)
                self.yTickRects.append(Rectangle(pos=(0, y - (TouchGraph.tickWidthFactor / 2) * self.line_width), size=(
                    4 * TouchGraph.tickWidthFactor * self.line_width, TouchGraph.tickWidthFactor * self.line_width)))
                # use text on canvas https://groups.google.com/forum/#!topic/kivy-users/zRCjfhBcX4c
                text = p if not self.y_labels else self.y_labels[i]
                tick_label = CoreLabel(text=text, font_size=self.font_size, color=self.lineColor)
                tick_label.refresh()
                texture = tick_label.texture
                texture_size = list(texture.size)
                self.yTickLabels.append(
                    Rectangle(pos=(6 * TouchGraph.tickWidthFactor * self.line_width, y - texture_size[1] / 2),
                              texture=texture, size=texture_size))
            Color(*self.lineColor)
            self.line = Line(points=self.point_coords, width=self.line_width)
            Color(*self.pointColor)
            self.circles = []
            for i, p in enumerate(zip(self.point_coords[::2], self.point_coords[1::2])):
                self.circles.append(Ellipse(pos=(p[0] - 0.5 * TouchGraph.circleDiameterFactor * self.line_width,
                                                 p[1] - 0.5 * TouchGraph.circleDiameterFactor * self.line_width), size=(
                    self.line_width * TouchGraph.circleDiameterFactor,
                    self.line_width * TouchGraph.circleDiameterFactor)))
            ScissorPop()
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.unbind(points=self.late_init)

    def update_canvas(self, *args):
        del args
        self.scissor.x = int(round(self.to_window(*self.pos)[0]))
        self.scissor.y = int(round(self.to_window(*self.pos)[1]))
        self.scissor.width = int(round(self.width))
        self.scissor.height = int(round(self.height))
        self.back.pos = self.pos
        self.back.size = self.size
        self.line.points = self.point_coords
        for i, p in enumerate(zip(self.point_coords[::2], self.point_coords[1::2])):
            self.circles[i].pos = (p[0] - 0.5 * TouchGraph.circleDiameterFactor * self.line_width,
                                   p[1] - 0.5 * TouchGraph.circleDiameterFactor * self.line_width)
        for i, p in enumerate(self.x_ticks):
            x = self.graph_x_for_x(p)
            self.xTickRects[i].pos = (self.x + x - 0.25 * self.line_width, self.y)
            self.xTickLabels[i].pos = (self.x + x - self.xTickLabels[i].size[0] / 2, self.y + 3 * self.line_width)
        for i, p in enumerate(self.y_ticks):
            y = self.graph_y_for_y(p)
            self.yTickRects[i].pos = (self.x, self.y + y - 0.25 * self.line_width)
            self.yTickLabels[i].pos = (self.x + 3 * self.line_width, self.y + y - self.yTickLabels[i].size[1] / 2)

    @property
    def point_coords(self):
        norm_x = [float(x) / self.max[0] for x in self.points[::2]]
        norm_y = [float(y) / self.max[1] for y in self.points[1::2]]
        x = [x * (self.width - 2 * self.padding_x) + self.x + self.padding_x for x in norm_x]
        y = [y * (self.height - 2 * self.padding_y) + self.y + self.padding_y for y in norm_y]
        coords = x + y
        coords[::2] = x
        coords[1::2] = y
        return coords

    def on_touch_down(self, touch):
        if self.collide_point(*self.to_local(*touch.pos)):
            for i, p in enumerate(zip(self.point_coords[::2], self.point_coords[1::2])):
                pos_touch = touch.pos
                if p[0] - 5 * self.line_width < pos_touch[0] < p[0] + 5 * self.line_width \
                        and p[1] - 5 * self.line_width < pos_touch[1] < p[1] + 5 * self.line_width:
                    self.current_point = i + 1
                    return True
            return super(TouchGraph, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*self.to_local(*touch.pos)):
            if self.current_point:
                self.current_point = None
                return True
            return super(TouchGraph, self).on_touch_up(touch)

    def on_touch_move(self, touch):
        # do not check collision here since the move path could be outside of our widget
        if self.current_point:
            c = self.current_point
            if c:
                if 0 < self.y_for_graph_y(touch.pos[1] - self.pos[1]) < self.max[1]:
                    self.points[(c - 1) * 2 + 1] = self.y_for_graph_y(touch.pos[1] - self.pos[1])
                    self.update_canvas()
                    return True
            return super(TouchGraph, self).on_touch_move(touch)

    def x_for_graph_x(self, x):
        return (x - self.padding_x) / float(self.width - 2 * self.padding_x) * self.max[0]

    def graph_x_for_x(self, x):
        try:
            graph_x = x / float(self.max[0]) * (self.width - 2 * self.padding_x) + self.padding_x
            return graph_x
        except AttributeError:
            return -10

    def y_for_graph_y(self, y):
        return (y - self.padding_y) / float(self.height - 2 * self.padding_y) * self.max[1]

    def graph_y_for_y(self, y):
        return y / float(self.max[1]) * (self.height - 2 * self.padding_y) + self.padding_y


if __name__ == "__main__":
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout


    class DemoGraph(TouchGraph):
        # this draws a circle on the graph on a touch_down event using the static y_for_x function
        def on_touch_down(self, touch):
            super(DemoGraph, self).on_touch_down(touch)
            with self.canvas:
                Color(1, 0, 0, 1)
                x = touch.pos[0] - self.pos[0]
                y = TouchGraph.y_for_x(self.x_for_graph_x(x), self.points)
                Ellipse(pos=(self.x + x, self.y + self.graph_y_for_y(y)), size=(10, 10))


    class StandaloneApp(App):
        def build(self):
            box = BoxLayout()
            graph = DemoGraph(points=[0, .2, 1, 0.25, 2, .4, 5, .5, 10, .6, 30, .5],
                              font_size=30,
                              line_width=5,
                              x_labels=['A', 'B', 'C', 'D'],
                              x_ticks=[0, 10, 20, 30],
                              y_ticks=[.1, .2, .5, .9],
                              max_y=1)
            box.add_widget(graph)
            return box


    StandaloneApp().run()

import re
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class Colors(Gtk.Window):
    def __init__(self):
        super().__init__(title="Miscellaneous")
        self.set_size_request(0, 300)

        self.vbx = Gtk.VBox()
        self.add(self.vbx)

        self.hbx1 = Gtk.HBox()
        self.vbx.pack_start(self.hbx1, False, True, 20)
        self.hbx2 = Gtk.HBox()
        self.vbx.pack_start(self.hbx2, False, True, 0)
        self.hbx3 = Gtk.HBox()
        self.vbx.pack_start(self.hbx3, False, True, 15)
        self.hbx4 = Gtk.HBox()
        self.vbx.pack_start(self.hbx4, False, True, 0)
        self.hbx5 = Gtk.HBox()
        self.vbx.pack_start(self.hbx5, False, True, 0)

        self.rgb_to_hex = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
                           10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F'}

        self.frame = self.create(Gtk.Frame(), self.hbx5, (0, 0, 1, 1), hbox_vals=(True, True, 10))
        self.scrolly = Gtk.ScrolledWindow()
        self.frame.add(self.scrolly)
        self.frame.set_property('height_request', 110)

        self.grid_in_layout = Gtk.Grid()

        self.scrolly.add(self.grid_in_layout)
        # Creating widgets as the program goes along doesn't seem to be working, so this creates labels from the start,
        # and their text will just be changing repeatedly:
        self.list_of_labels = [Gtk.Label(label=f'{i}') for i in range(300)]
        for i, e in enumerate(self.list_of_labels):
            self.grid_in_layout.attach(e, 1, i, 1, 1)
            e.set_opacity(0)

        self.create(Gtk.Label(), self.hbx1, (0, .5, 0, 0), (False, True, 5))
        self.file_en = self.create(Gtk.Entry(), self.hbx1, (0, 0, 1, 1))
        # Currently, a pointless button. This /\ is used instead:
        self.create(Gtk.FileChooserButton(), self.hbx1, hbox_vals=(False, True, 5))

        self.scale = self.create(Gtk.HScale(), self.hbx2, hbox_vals=(False, True, 8))
        self.scale.set_range(1, 100)
        self.scale.set_digits(0)
        self.scale.set_size_request(235, 0)

        self.color_entry = self.create(Gtk.Entry(), self.hbx3, (0, 0, 0, 1), hbox_vals=(False, True, 10))
        self.color_entry.set_width_chars(15)
        self.search_button = self.create(Gtk.Button(label='search'), self.hbx3, (0, 0, 0, 1))
        self.search_button.connect('clicked', self.search)

        self.result_message = self.create(Gtk.Label(label='File Not Found'), self.hbx4, hbox_vals=(True, True, 10))
        self.result_message.set_opacity(0)

    # Creates a widget with custom properties in a chosen box on call:
    @staticmethod
    def create(item, chosen_hbox, vals=(0, 0, 0, 0), hbox_vals=(True, True, 0)):
        al = Gtk.Alignment(xalign=vals[0], yalign=vals[1], xscale=vals[2], yscale=vals[3])
        al.add(item)
        chosen_hbox.pack_start(al, hbox_vals[0], hbox_vals[1], hbox_vals[2])
        return item

    @staticmethod
    def convert_to_rgb(color):
        result = []
        if len(color) == 1:
            for i in range(0, 6, 2):
                result.append(int(color[0][i], 16) * 16 + int(color[0][i + 1], 16))
            return result, True
        else:
            result = color.copy()
            for i, e in enumerate(result):
                result[i] = int(e)
            return result, True

    def search(self, x):
        try:
            file = open(self.file_en.get_text())
        except:
            self.result_message.set_label('File Not Found')
        else:
            unique_colors = []
            unique_colors_len = 0
            all_colors_len = 0
            entry_color = []
            entry_color.append(self.color_entry.get_text())
            entry_color = self.convert_to_rgb(entry_color)
            if entry_color[1]:
                allowed = int(self.scale.get_value())
                entry_color = entry_color[0]
                f = file.read()

                pattern = re.compile(r'#([a-fA-F\d]{6})|rgba?\( *(\d+) *, *(\d+) *, *(\d+)')

                for i in pattern.findall(f):
                    pre_converted_color = []
                    for j in i:
                        if j != '':
                            pre_converted_color.append(j)
                    rgb_vals = self.convert_to_rgb(pre_converted_color)[0]

                    how_similar = 0
                    for j in [[entry_color[0], rgb_vals[0]], [entry_color[1], rgb_vals[1]],
                              [entry_color[2], rgb_vals[2]]]:
                        if j[0] > j[1]:
                            p = -1
                        else:
                            p = 1
                        for k in range(j[0] + p, j[1] + p, +p):
                            if k <= 127.5:
                                how_similar += 50 * k / 127.5 + 50
                            else:
                                how_similar += 50 * (127.5 - k) / 127.5 + 100
                    how_similar = 100 - int(how_similar) * 100 / 57374.70588235294
                    colors_and_similarity = [rgb_vals, how_similar]
                    if colors_and_similarity[1] >= allowed - 10:
                        colors_and_similarity.pop()
                        hex_val = ''
                        for j in colors_and_similarity[0]:
                            val1 = (self.rgb_to_hex[int(j / 16)])
                            val2 = (self.rgb_to_hex[j % 16])
                            hex_val += val1 + val2
                        colors_and_similarity.append(hex_val)
                        all_colors_len += 1
                        if colors_and_similarity not in unique_colors:
                            unique_colors.append(colors_and_similarity)
                            unique_colors_len += 1

                self.result_message.set_label(f'{unique_colors_len} unique colors. {all_colors_len} all.')
            file.close()
        self.result_message.set_opacity(1)
        self.show_colors(unique_colors)

    # The labels are changed depending on the found colors:
    def show_colors(self, unique_colors):
        for i in self.list_of_labels:
            i.set_opacity(0)
        for i, e in enumerate(unique_colors):
            self.list_of_labels[i].set_label(e[1])
            self.list_of_labels[i].set_opacity(1)


if __name__ == '__main__':
    win = Colors()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

import taichi as ti
import numpy as np
import os
import SimpleITK as sitk


ti.init(arch=ti.gpu)


@ti.data_oriented
class VolumeRendering:
    def __init__(
        self, image_path, render_mode, project_direction, window_center, window_width
    ):
        # read image
        image_sitk = sitk.ReadImage(image_path)
        self.image_np = sitk.GetArrayFromImage(image_sitk)
        image_shape = self.image_np.shape

        self.image_width = image_shape[0]
        self.image_height = image_shape[1]
        self.image_depth = image_shape[2]

        # convert numpy to taichi data
        self.image_ti = ti.field(
            ti.i16, shape=(self.image_width, self.image_height, self.image_depth)
        )
        self.image_ti.from_numpy(self.image_np)

        # set render mode
        self.render_mode = render_mode

        # set project_direction
        self.project_direction = project_direction

        # init canvas
        if self.project_direction == 1:
            self.canvas = ti.field(
                dtype=ti.u8, shape=(self.image_width, self.image_height)
            )
        elif self.project_direction == 2:
            self.canvas = ti.field(
                dtype=ti.u8, shape=(self.image_width, self.image_depth)
            )
        elif self.project_direction == 3:
            self.canvas = ti.field(
                dtype=ti.u8, shape=(self.image_height, self.image_depth)
            )
        self.canvas.fill(0)

        # calculate window level para
        self.window_level_min = (2 * window_center - window_width) / 2.0 + 0.5
        self.window_level_max = (2 * window_center + window_width) / 2.0 + 0.5

    def get_window_width_height(self):
        window_width = self.image_width
        window_height = self.image_height
        if self.project_direction == 1:
            window_width = self.image_width
            window_height = self.image_height
        elif self.project_direction == 2:
            window_width = self.image_width
            window_height = self.image_depth
        elif self.project_direction == 3:
            window_width = self.image_height
            window_height = self.image_depth

        return window_width, window_height

    def display(self, gui):
        gui.set_image(self.canvas.to_numpy())

    def render(self):
        if self.render_mode == 1:
            self.render_max()
        elif self.render_mode == 2:
            self.render_min()

    @ti.kernel
    def render_max(self):
        for i, j in self.canvas:
            gray = ti.i16(0)
            max_value = self.get_max_value(i, j)
            gray = self.apply_window_level(max_value)

            self.canvas[i, j] = gray

    @ti.kernel
    def render_min(self):
        for i, j in self.canvas:
            gray = ti.i16(0)
            max_value = self.get_min_value(i, j)
            gray = self.apply_window_level(max_value)

            self.canvas[i, j] = gray

    @ti.func
    def get_max_value(self, i, j):
        max_value = ti.i16(-10000)
        if self.project_direction == 1:
            for k in range(self.image_depth):
                temp_value = self.image_ti[i, j, k]
                if temp_value > max_value:
                    max_value = temp_value

        elif self.project_direction == 2:
            for k in range(self.image_height):
                temp_value = self.image_ti[i, k, j]
                if temp_value > max_value:
                    max_value = temp_value

        elif self.project_direction == 3:
            for k in range(self.image_width):
                temp_value = self.image_ti[k, i, j]
                if temp_value > max_value:
                    max_value = temp_value

        return max_value

    @ti.func
    def get_min_value(self, i, j):
        min_value = ti.i16(10000)
        if self.project_direction == 1:
            for k in range(self.image_depth):
                temp_value = self.image_ti[i, j, k]
                if temp_value < min_value:
                    min_value = temp_value

        elif self.project_direction == 2:
            for k in range(self.image_height):
                temp_value = self.image_ti[i, k, j]
                if temp_value < min_value:
                    min_value = temp_value

        elif self.project_direction == 3:
            for k in range(self.image_width):
                temp_value = self.image_ti[k, i, j]
                if temp_value < min_value:
                    min_value = temp_value

        return min_value

    @ti.func
    def apply_window_level(self, value):
        after_value = (
            (value - self.window_level_min)
            * 255.0
            / (self.window_level_max - self.window_level_min)
        )

        if after_value < 0:
            after_value = 0
        elif after_value > 255:
            after_value = 255

        return after_value


def test():
    # head data
    image_path = os.path.join(
        os.path.split(os.path.realpath(__file__))[0], "data/FullHead.mhd"
    )

    render_mode = 1  # 1: max mode, 2: min mode
    window_center = 1500
    window_width = 3000

    project_direction = 1  # 1:coronal, 冠状面  2:Sagittal, 矢状面, 3:Axial, 横断面 

    volume_render = VolumeRendering(
        image_path, render_mode, project_direction, window_center, window_width
    )
    volume_render.render()

    win_width, win_height = volume_render.get_window_width_height()

    gui = ti.GUI("Volume Rendering", res=(win_width, win_height))
    while gui.running:
        volume_render.display(gui)
        gui.show()


if __name__ == "__main__":
    test()

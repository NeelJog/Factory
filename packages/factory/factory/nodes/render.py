# Copyright 2019-2022 DADoES, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the root directory in the "LICENSE" file or at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from turtle import right
import bpy
import anatools.lib.context as ctx
from anatools.lib.node import Node
from anatools.lib.scene import AnaScene
import logging
import imageio
import math
import os
import numpy
import glob

logger = logging.getLogger(__name__)


class RenderNode(Node):
    """
    A class to represent a the Render node, a node that renders an image of the given scene.
    Executing the Render node creates an image, annotation, and metadata file.
    """
    # Sets up 3 lamps at equidistand points in the center of the warehouse along the y axis.
    #   Pre: The intensity of the lamps, the scene object to which the lamps are to be
    #        added, and the warehouse object in which the lamps are going to be placed
    #        is provided.
    #   Post: Creates 3 lamps with the provided intensity and adds the lamps to the scene.
    def set_up_lamps(self, intensity, scene, warehouse):
        # There will be 3 lamps placed at 3 equidistant points in the warehouse along the 
        # y axis. The intensity of the lights is up to the user.
        x_axis = warehouse.root.dimensions.x
        x_placement = (x_axis / 2) * -1 + (x_axis / 8)
        y_axis = warehouse.root.dimensions.y
        y_placement = [(y_axis / 2 * -1) + (y_axis / 4),
                       0,
                       y_axis / 2 - (y_axis / 4)]
        z_placement = warehouse.root.dimensions.z / 2

        # Make the 3 lamps with the given intensity
        lamp_1_data = bpy.data.lights.new("light",type='SPOT')
        lamp_1_data.energy = intensity
        lamp_1 = bpy.data.objects.new("Light 1",lamp_1_data)
        lamp_1.location = (x_placement, y_placement[0], z_placement)
        scene.collection.objects.link(lamp_1)

        lamp_2_data = bpy.data.lights.new("light",type='SPOT')
        lamp_2_data.energy = intensity
        lamp_2 = bpy.data.objects.new("Light 2",lamp_2_data)
        lamp_2.location = (x_placement, y_placement[1], z_placement)
        scene.collection.objects.link(lamp_2)

        lamp_3_data = bpy.data.lights.new("light",type='SPOT')
        lamp_3_data.energy = intensity
        lamp_3 = bpy.data.objects.new("Light 3",lamp_3_data)
        lamp_3.location = (x_placement, y_placement[2], z_placement)
        
        # Add the 3 lamps to the scene
        scene.collection.objects.link(lamp_3)
    
    # Sets up the appropriate camera based on the "type" chosen by the user.
    #   Pre: A valid type (Central, Left, or Right), the scene to which the camera is to be
    #        added, and the warehouse object is provided.
    #   Post: Based on the type passed in, the appropriate camera is set up. If the type is
    #         left, the camera is on the left wall in the center. If the type is right, the
    #         camera is on the right wall, and if the type is central, the camera is in the
    #         middle of the warehouse.  
    def set_up_camera(self, type, warehouse, scene):
        cam1 = bpy.data.cameras.new("Camera 1")
        cam_obj1 = bpy.data.objects.new("Camera 1", cam1)
        cam_obj1.rotation_mode = "XYZ"
        cam_obj1.rotation_euler[0] = math.radians(75)
        cam_obj1.rotation_euler[1] = math.radians(0)

        warehouse_height = warehouse.root.dimensions.z
        camera_height = warehouse_height * 3 / 4

        wall_to_wall = warehouse.root.dimensions.y
        left_wall = (wall_to_wall / 2) * -1
        right_wall = (wall_to_wall / 2)

        if (type == "Central"):
            cam_obj1.location = (0, 0, camera_height)
            cam_obj1.rotation_euler[2] = math.radians(90)
        elif (type == "Left"):
            cam_obj1.location = (0, left_wall, camera_height)
            cam_obj1.rotation_euler[2] = math.radians(65)
        elif (type == "Right"):
            cam_obj1.location = (0, right_wall, camera_height)
            cam_obj1.rotation_euler[2] = math.radians(115)
        else:
            logger.error("Invalid Camera Selection")
        
        scene.collection.objects.link(cam_obj1)
        scene.camera = cam_obj1

    def exec(self):
        """Execute node"""
        #return {}  # testing the time to bake the physics
        logger.info("Executing {}".format(self.name))

        try:
            # We do not expect more than one ObjectPlacement node to be ported to here, but 
            # the input is still a list.
            objects = self.inputs["Objects"][0]
            warehouse = objects[0]
            print("HERERERERERERE")
            # Start setting up the scene
            scn = bpy.context.scene
            bpy.ops.object.visual_transform_apply()

            sizeMax = 3000
            scn.render.resolution_x = min(sizeMax, int(self.inputs["Width (px)"][0]))
            scn.render.resolution_y = min(sizeMax, int(self.inputs["Height (px)"][0]))


            #Let's add a few lamps...This could be done in a separate node if desired.
            # The locations of the lamps will change based on the dimensions of the warehouse,
            # so make sure to explore the warehouse in your blend file and choose scales
            # that make sense.
            bpy.context.scene.world.light_settings.use_ambient_occlusion = True
            
            intensity = int(self.inputs["Light Intensity"][0])
            self.set_up_lamps(intensity, scn, warehouse)

            # Set up the camera by placing it in the right place and rotating it the right way.
            # The location of the camera will change based on the dimensions of the warehouse,
            # so make sure to explore the warehouse in your blend file and choose the location
            # /angle that make sense.
            type = self.inputs["Camera"][0]
            self.set_up_camera(type, warehouse, scn)

            #Initialize an AnaScene.  This configures the Blender compositor and provides object annotations and metadata.
            #To create an AnaScene we need to send a blender scene and a view layer for annotations
            sensor_name = 'RGBCamera'
            scene = AnaScene(
                blender_scene=scn,
                annotation_view_layer=bpy.context.view_layer,
                objects=objects,
                sensor_name=sensor_name)

            #Add denoise node to compositor
            s = bpy.data.scenes[ctx.channel.name]
            c_rl = s.node_tree.nodes['Render Layers']
            c_c = s.node_tree.nodes['Composite']
            c_dn = s.node_tree.nodes.new('CompositorNodeDenoise')
            s.node_tree.nodes.remove(s.node_tree.nodes['imgout'])
            c_of = s.node_tree.nodes.new('CompositorNodeOutputFile')
            c_of.base_path = os.path.join(ctx.output,'images')
            c_of.file_slots.clear()
            c_of.file_slots.new(f'{ctx.interp_num:010}-#-{sensor_name}.png')
            s.node_tree.links.new(c_rl.outputs[0], c_dn.inputs[0])
            s.node_tree.links.new(c_dn.outputs[0], c_c.inputs[0])
            s.node_tree.links.new(c_dn.outputs[0], c_of.inputs[0])
                        
            #OK. Now it's time to render.
            if ctx.preview:
                logger.info("LOW RES Render for Preview")
                render(resolution='preview')
                imgfilename = f"{ctx.interp_num:010}-{scn.frame_current}-{sensor_name}.png"
                preview = imageio.imread(os.path.join(ctx.output,'images',imgfilename))
                imageio.imsave(os.path.join(ctx.output,'preview.png'), preview)
                return{}
            else:
                # bpy.ops.wm.save_as_mainfile(filepath="scene4render.blend")
                render()

            #Prepare for annotataions: Remove link to image output file, update objects, (re)write masks
            s = bpy.data.scenes[ctx.channel.name]
            c_of = s.node_tree.nodes['File Output']
            c_of.file_slots.clear()
            for obj in objects:
                obj.setup_mask()
            render(resolution='masks')
            c_of.file_slots.new(f'{ctx.interp_num:010}-#-{sensor_name}.png')
            s.node_tree.links.new(c_dn.outputs[0], c_of.inputs[0])

            calculate_obstruction = self.inputs["Calculate Obstruction"][0]
            
            if calculate_obstruction == 'F':
                # Create annotations 
                scene.write_ana_annotations()
                scene.write_ana_metadata()
                return {}
            
            #Render masks for each object.
            #only render a mask file for objects in the image

            #Unlink all the object masks in the compositor
            links = scn.node_tree.links
            masknodes = [node for node in scn.node_tree.nodes if node.name.split('_')[-1]=='mask']
            masklinks = {}
            for masknode in masknodes:
                masklinks[masknode.index] = {
                    'masknode': masknode,
                    'socketinput': masknode.outputs[0].links[0].to_socket
                }
                links.remove(masknode.outputs[0].links[0])
            #Unlink the image from the compositor
            for link in scn.node_tree.nodes['Render Layers'].outputs['Image'].links:
                links.remove(link)

            masktemplate = os.path.join(scene.maskout.base_path,
                                        scene.maskout.file_slots[0].path + '.' + scene.maskout.format.file_format.lower())

            #Only render a mask file for objects in the image
            compositemaskfile = masktemplate.replace('#', str(scn.frame_current))
            compimg = imageio.imread(compositemaskfile)
            allmasks = compimg[numpy.nonzero(compimg)]
            renderedobjectidxs = numpy.unique(allmasks)
            renderedobjects = [obj for obj in objects if obj.instance in renderedobjectidxs]

            #Hide all but a single object and render a mask
            for obj in objects:
                obj.root.hide_render = True
                if obj not in renderedobjects:
                    obj.rendered = False

            imgpath = scene.imgout.file_slots[0].path
            maskpath = scene.maskout.file_slots[0].path
            for obj in renderedobjects:
                obj.solo_mask_id = f'obj{obj.instance:03}'
                scene.maskout.file_slots[0].path = '{}-{}'.format(maskpath, obj.solo_mask_id)
                scene.imgout.file_slots[0].path = '{}-{}'.format(imgpath, obj.solo_mask_id)

                obj.root.hide_render = False

                # link the ID mask node to it's divide node
                masknode = masklinks[obj.instance]['masknode']
                socketinput = masklinks[obj.instance]['socketinput']
                links.new(masknode.outputs['Alpha'], socketinput)

                render(resolution='low')

                # rehide object
                obj.root.hide_render = True
                links.remove(masknode.outputs[0].links[0])

            #Create annotations
            scene.write_ana_annotations(calculate_obstruction=calculate_obstruction)
            scene.write_ana_metadata()

            print("Number Objects Rendered: {}".format(len([o for o in objects if o.rendered])))

            #Clean up extra rendered files
            maskpattern = os.path.join(scene.maskout.base_path, maskpath.replace('#', str(scn.frame_current)))
            for filepath in glob.glob('{}-*'.format(maskpattern)):
                os.remove(filepath)
            imgpattern = os.path.join(scene.imgout.base_path, imgpath.replace('#', str(scn.frame_current)))
            for filepath in glob.glob('{}-*'.format(imgpattern)):
                os.remove(filepath)

        except Exception as e:
            logger.error("{} in \"{}\": \"{}\"".format(type(e).__name__, type(self).__name__, e).replace("\n", ""))
            raise

        return {}


def render(resolution='high'):
    # The render patch size, 256 is best for GPU
    bpy.context.scene.render.tile_x = 256
    bpy.context.scene.render.tile_y = 256

    if resolution == 'preview':
        if bpy.context.scene.render.resolution_x >1000:
            # For speed, set the resolution to a common multiple of the tile size
            bpy.context.scene.render.resolution_x = 640
            bpy.context.scene.render.resolution_y = 384
        bpy.context.scene.render.tile_x = 64
        bpy.context.scene.render.tile_y = 64

        bpy.context.scene.cycles.samples = 8
        bpy.context.scene.cycles.max_bounces = 6

    elif resolution == 'high':
        # Higher samples and bounces diminishes speed for higher quality images
        bpy.context.scene.cycles.samples = 15
        bpy.context.scene.cycles.max_bounces = 12

    else: # masks
        bpy.context.scene.cycles.samples = 1
        bpy.context.scene.cycles.max_bounces = 1

    bpy.ops.render.render('INVOKE_DEFAULT')

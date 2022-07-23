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
import math
from anatools.lib.node import Node
from anatools.lib.generator import CreateBranchGenerator
import anatools.lib.context as ctx
import numpy as np
import logging
import bpy

logger = logging.getLogger(__name__)

class RandomPlacementClass(Node):
    """
    A class to represent the RandomPlacement node, a node that places objects in a scene.
    """

    def exec(self):
        """Execute node"""
        logger.info("Executing {}".format(self.name))

        try:
            # First we set up the warehouse
            warehouse_generator = CreateBranchGenerator(self.inputs["Warehouse Generator"])
            warehouse = warehouse_generator.exec()

            # Set the scene to the current frame
            sc = bpy.context.scene
            sc.frame_current = 0

            # We then grab the object generator method from the inputs
            branch_generator = CreateBranchGenerator(self.inputs["Object Generators"])

            # Decide how many objects we want in the scene
            object_number = min(200, int(self.inputs["Number of Objects"][0]))
            object_list = []
            
            # Valid x/y locations where we can place boxes. This will change based on the
            # dimensions of the blend file you are working with, so make sure to explore
            # your 3D blend file and determine which x/y locations make sense in your context.
            valid_x_locations = [-30, -28]
            valid_y_locations = [-10, -7.5, -5, -2.5, 0, 2.5, 5, 7.5, 10]

            # Locations that have been picked so far and how many we have available in total.
            locations_picked = []
            num_locations_available = len(valid_x_locations) * len(valid_y_locations)

            # Render the desired number of objects (max 200)
            for ii in np.arange(object_number):
                this_object = branch_generator.exec() #Picks a new branch from the inputs and executes it
                object_list.append(this_object)
                #.root is the actual blender object
                
                # Decide which x/y location to place the box in.
                pick_x = np.random.choice(valid_x_locations)
                pick_y = np.random.choice(valid_y_locations)

                # If that particular x/y location has been picked, randomly keep choosing
                # new ones until we find a location that has not been picked.
                while ((pick_x, pick_y) in locations_picked):
                    pick_x = np.random.choice(valid_x_locations)
                    pick_y = np.random.choice(valid_y_locations)
                
                # Add the chosen location to the list of picked locations.
                locations_picked.append((pick_x, pick_y))
                
                # "Place" the object in the scene based on the x/y that were randomly chosen. The
                # z value will always be zero – can be modified if we want to stack boxes.
                this_object.root.location[0] = pick_x
                this_object.root.location[1] = pick_y
                this_object.root.location[2] = 0

                # If all available locations have now already been picked, stop rendering objects.
                if (len(locations_picked) == num_locations_available):
                    logger.error("More objects than spots available")
                    break
        except Exception as e:
            logger.error("{} in \"{}\": \"{}\"".format(type(e).__name__, type(self).__name__, e).replace("\n", ""))
            raise

        return {"Objects": object_list}

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
from anatools.lib.node import Node
from anatools.lib.ana_object import AnaObject
from anatools.lib.generator import get_blendfile_generator
import anatools.lib.context as ctx
import logging

logger = logging.getLogger(__name__)

class ExampleChannelObject(AnaObject):
    """
    A class to represent the Example Channel AnaObjects.
    Add a 'color' method for the objects of interest.
    """

    def color(self, color_type=None):
        pass

    def setup_mask(self):
        pass

class Box1Object(ExampleChannelObject):
    """
    A class to represent the Box1 ExampleChannelObject
    """

class WarehouseObject(ExampleChannelObject):
    """
    A class to represent the Warehouse ExampleChannelObject.
    """

class Box1Node(Node):
    """
    A class to represent the Box1 node, a node that instantiates a generator for the Box1 object.
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))
        return {"Box1 Generator": get_blendfile_generator("factory", ExampleChannelObject, "Box1")}

class WarehouseNode(Node):
    """
    A class to represent the Warehouse node, a node that instantiates a generator for the warehouse object.
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))
        return {"Warehouse Generator": get_blendfile_generator("factory", ExampleChannelObject, "Warehouse")}
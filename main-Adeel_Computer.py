from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from direct.controls.InputState import InputState
from panda3d.core import WindowProperties
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerPusher, CollisionBox, Point3, CollisionSphere, LVector3
from panda3d.physics import *


class CameraControllerBehaviour(DirectObject):
    _instances = 0
    
    def __init__(self, camera, velocity=9, mouse_sensitivity=0.01,initial_pos=(0, 0, 5), showbase=None):
        self._camera = camera
        self._velocity = velocity
        self._mouse_sensitivity = mouse_sensitivity
        self._keys = None
        self._input_state = InputState()
        self._heading = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._roll = 0.0
        self._showbase = base if showbase is None else showbase
        self._gravity = LVector3(0, 0, -3.8)  # Set gravity vector pointing downward
        self._instance = CameraControllerBehaviour._instances
        CameraControllerBehaviour._instances += 1
        self._camera.setPos(*initial_pos)
        # Set the initial position of the camera

    def setup(self, keys={
        'w':"forward", 
        's':"backward",
        'a':"left",
        'd':"right",
        'space':"up",
        'lshift':"down"
    }):
        self._keys = keys
        for key in self._keys:
            self._input_state.watchWithModifiers(self._keys[key], key)

        self._showbase.disableMouse()

        props = WindowProperties()
        props.setCursorHidden(True)

        self._showbase.win.requestProperties(props)

        self._showbase.taskMgr.add(self.update, "UpdateCameraTask" + str(self._instance))
    
    def destroy(self):
        self.disable()
        self._input_state.delete()

        del self

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, velocity):
        self._velocity = velocity

    @property
    def mouse_sensitivity(self):
        return self._mouse_sensitivity

    @mouse_sensitivity.setter
    def mouse_sensitivity(self, sensitivity):
        self._mouse_sensitivity = sensitivity

    def disable(self):
        self._showbase.taskMgr.remove("UpdateCameraTask" + str(self._instance))

        props = WindowProperties()
        props.setCursorHidden(False)

        self._showbase.win.requestProperties(props)            

    def update(self, task):
        dt = globalClock.getDt()
        
        # Get mouse movement for rotation
        md = self._showbase.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        center_x = self._showbase.win.getXSize() // 2
        center_y = self._showbase.win.getYSize() // 2

        if self._showbase.win.movePointer(0, center_x, center_y):
            self._yaw = self._yaw - (x - center_x) * self._mouse_sensitivity
            self._pitch = self._pitch - (y - center_y) * self._mouse_sensitivity

        # Clamp the pitch to prevent camera flipping over
        self._pitch = max(-89, min(89, self._pitch))
        
        # Set the camera's orientation
        self._showbase.camera.setHpr(self._yaw, self._pitch, self._roll)
        
        # Access the camera's lens and set the focal length
        lens = self._showbase.cam.node().getLens()
        lens.setFocalLength(0.25)
        
        # Get the camera's position
        
        # Calculate the position increment
        pos_increment = self._velocity * dt
        
        # Handle keyboard input for movement
        if  self._input_state.isSet('forward'):
            self._showbase.camera.setY(self._showbase.camera, pos_increment)

        if  self._input_state.isSet('backward'):
            self._showbase.camera.setY(self._showbase.camera, -pos_increment)

        if  self._input_state.isSet('left'):
            self._showbase.camera.setX(self._showbase.camera, -pos_increment)

        if  self._input_state.isSet('right'):
            self._showbase.camera.setX(self._showbase.camera, pos_increment)

        if  self._input_state.isSet('up'):
            self._showbase.camera.setZ(self._showbase.camera, pos_increment)

        if  self._input_state.isSet('down'):
            self._showbase.camera.setZ(self._showbase.camera, -pos_increment)
        
        cam_pos = self._showbase.camera.getPos(self._showbase.render)
        # Apply gravity to the camera's position
        (cam_pos) += self._gravity * dt
        
        # Update the camera's position
        self._showbase.camera.setPos(cam_pos)
        return Task.cont
        
class MyApp(ShowBase):
    
    def createwalls(self):
        wall_collision_node = CollisionNode('wall')
        wall_collision_node.addSolid(CollisionBox(Point3(22, -6.5, 32), 19, .5, 27))
        wall_collision_node.addSolid(CollisionBox(Point3(-23.5, -6.5, 32), 19, .5, 27))
        wall_collision_node.addSolid(CollisionBox(Point3(0, -6.5, 35), 10, .5, 25))
        wall_collision_node.addSolid(CollisionBox(Point3(0, -63, 30), 48, .5, 27))
        wall_collision_node.addSolid(CollisionBox(Point3(41, -35, 32), .5, 28, 27))
        wall_collision_node.addSolid(CollisionBox(Point3(-43, -35, 32), .5, 28, 27))
        wall_collision_node.addSolid(CollisionBox(Point3(0, -35, 0), 43, 28, 5))
        wall_collision_node.addSolid(CollisionBox(Point3(0, 0, 0), 15, 5, 2))
        wall_collision_node.addSolid(CollisionBox(Point3(14, -25.5, 9), .3, 8.5, 4))
        wall_collision_node.addSolid(CollisionBox(Point3(-15.75, -12.5, 9), .3, 6, 4))
        wall_collision_node.addSolid(CollisionBox(Point3(-15.75, -40, 9), .3, 16, 4))
        wall_collision_node.addSolid(CollisionBox(Point3(7, -35, 9), 6, .3, 4))
        wall_collision_node_path = self.render.attachNewNode(wall_collision_node)
        wall_collision_node_path.show()
        
    def __init__(self):
        super().__init__()
        
        Manor = self.loader.loadModel(r"models/HauntedMansion.glb")
        Manor.reparentTo(self.render)
        Manor.setHpr(90, 90, 90)
        
        cam_controller = CameraControllerBehaviour(self.camera)
        cam_controller.setup(keys={'w':"forward",
            's':"backward",
            'a':"left",
            'd':"right",
            'space':"up",
            'lshift':"down"})

        # Create a collision traverser
        self.cTrav = CollisionTraverser()

        # Create a collision handler
        self.pusher = CollisionHandlerPusher()

        # Create a collision node for the camera
        camera_collision_node = CollisionNode('camera')
        camera_collision_node.addSolid(CollisionSphere(0, 0, 0, 1))
        camera_collision_node_path = self.camera.attachNewNode(camera_collision_node)
        self.cTrav.addCollider(camera_collision_node_path, self.pusher)
        self.pusher.addCollider(camera_collision_node_path, self.camera)

        # Create a collision node for a wall
        MyApp.createwalls(self)

if __name__ == "__main__":
    app = MyApp()
    app.run()
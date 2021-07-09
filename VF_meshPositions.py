bl_info = {
	"name": "VF Mesh Positions",
	"author": "John Einselen - Vectorform LLC",
	"version": (0, 1),
	"blender": (2, 80, 0),
	"location": "Scene > Vertex Tools > Subpanel",
	"description": "Sets a series of object position keyframes based on the vertices of a target mesh",
	"warning": "inexperienced developer, use at your own risk",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Render"}

# Features:
	# Select source object mesh (active object?)
	# Select target objects (full selection minus active, or name pattern?)
	# Randomise order (randomises the)
	# Button: set positions
	# Button: set keyframes
	# Button: set offset keyframes
	# Number: offset value

# Based on the following resources:
# https://blender.stackexchange.com/questions/1311/how-can-i-get-vertex-positions-from-a-mesh
# 
# 
# 
# 
# 

import bpy
from bpy.app.handlers import persistent

###########################################################################
# Main function

@persistent
def mesh_positions(scene):
	if not bpy.context.view_layer.objects.active.data.vertices:
		return

	print ("successfully clicked a button")
	# ...

###########################################################################
# Project settings and UI rendering classes

class MeshPositionsSettings(bpy.types.PropertyGroup):
	position_type: bpy.props.EnumProperty(
		name='Position Type',
		description='Sets how the mesh vertices affect the list of objects',
		items=[
			('POSITION', 'Position', 'Sets the position of the selected objects, but does not set a keyframe'),
			('KEYFRAME', 'Keyframe', 'Sets the position of the selected objects and creates keyframes at the current time'),
			('OFFSET', 'Offset Keyframes', 'Sets the position of the selected objects and creates offset keyframes starting at the current time'),
			],
		default='OFFSET')
	keyframe_offset: bpy.props.IntProperty(
		name="Offset",
		description="Number of frames each keyframe will be offset by")

def VFTOOLS_append_panel(self,context):
	try:
		layout = self.layout
	except Exception as exc:
		print(str(exc) + " | Error in View3D Ht Tool Header when adding to panel")

class VFTOOLS_mesh_positions(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = 'VFtools'
	bl_order = 0
	bl_label = "Mesh Positions"
	bl_idname = "VFTOOLS_mesh_positions"

	@classmethod
	def poll(cls, context):
		return True

	def draw_header(self, context):
		try:
			layout = self.layout
		except Exception as exc:
			print(str(exc) + " | Error in VF Mesh Positions panel header")

	def draw(self, context):
		try:
			layout = self.layout
			layout.use_property_decorate = False  # No animation
			layout.prop(context.scene.mesh_positions_settings, 'position_type')
			if bpy.context.scene.mesh_positions_settings.position_type == 'OFFSET':
				layout.prop(context.scene.mesh_positions_settings, 'keyframe_offset')
			op = layout.operator("export_applink.pilgway_3d_coat",text=r"Test Button",emboss=True,depress=False,icon_value=0)
		except Exception as exc:
			print(str(exc) + " | Error in VF Mesh Positions panel")

classes = (MeshPositionsSettings, VFTOOLS_mesh_positions)

###########################################################################
# Addon registration functions

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.mesh_positions_settings = bpy.props.PointerProperty(type=MeshPositionsSettings)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.mesh_positions_settings

if __name__ == "__main__":
	register()

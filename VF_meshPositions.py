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

# Usage:
	# Select target items
	# Select source object mesh (active object)
	# Randomise order (randomises the order the objects are processed in)
	# Frame offset (sequences the keyframes by a set amount)
	# Create keyframes!

# Known issues:
	# If the source object sorts anywhere but the end of the selected objects list, we're in trouble

# Based on the following resources:
# https://blender.stackexchange.com/questions/1311/how-can-i-get-vertex-positions-from-a-mesh
# https://blender.stackexchange.com/questions/155363/add-on-dev-button-that-simply-calls-a-function
# https://blender.stackexchange.com/questions/133962/how-to-use-keyframes-and-the-python-api-programmatically
# https://www.geeksforgeeks.org/range-to-a-list-in-python/
# 

# And ended up not using these:
# https://blenderartists.org/t/loop-over-collections-in-the-outliner/1172818/2
# https://b3d.interplanety.org/en/calling-functions-by-pressing-buttons-in-blender-custom-ui/
# 
# 
# 

import bpy
from bpy.app.handlers import persistent
import random

###########################################################################
# Main function

class VF_Mesh_Position_Offset(bpy.types.Operator):
	bl_idname = "vfmeshposition.offset"
	bl_label = "Create Offset Keyframes"

	def execute(self, context):
		# self.report({'INFO'}, f"This is {self.bl_idname}")
		if not bpy.context.view_layer.objects.active.data.vertices:
			return {'CANCELLED'}

		startFrame = bpy.context.scene.frame_current

		source = bpy.context.view_layer.objects.active.data.vertices
		objWorld = bpy.context.view_layer.objects.active.matrix_world
		# targets = bpy.context.view_layer.objects.selected
		targets = []
		for i in range(len(bpy.context.view_layer.objects.selected)):
			if targets[i].name != bpy.context.view_layer.objects.active.name:
				targets.append(targets[i])


		print ("    Raw List:")
		for i in range(len(targets)):
			print (targets[i].name)

		# Remove the active item from the selected items, if it exists in the list
		removeIndex = -1
		for i in range(len(targets)):
			if targets[i].name == bpy.context.view_layer.objects.active.name:
				removeIndex = i
		if removeIndex >= 0:
			del targets[removeIndex]

		print ("    Edited List:")
		for i in range(len(targets)):
			print (targets[i].name)



		length = min(len(source), len(targets) - 1)

		# Randomise the order of the objects if enabled
		order = [*range(length)]
		if bpy.context.scene.vf_mesh_positions_settings.enable_shuffle:
			random.shuffle(order)

		# # Loop through all of the vertices or objects (whichever is shorter)
		# for i in range(length):
		# 	# Only apply positional changes to the non-active objects
		# 	if bpy.context.view_layer.objects.active.name != targets[i].name:
		# 		newFrame = startFrame + (i * bpy.context.scene.vf_mesh_positions_settings.keyframe_offset)
		# 		co_transformed = objWorld @ source[i].co
		# 		targets[order[i]].location = co_transformed
		# 		targets[order[i]].keyframe_insert(data_path="location", frame=newFrame)

				# print ("loop: " + str(i))
				# print ("newFrame: " + str(newFrame))
				# print ("vert: " + str(source[i].co))
				# print ("vert: " + str(co_transformed))
				# print ("item: " + targets[order[i]].name)
				# print ("position: " + str(targets[order[i]].location))

		return {'FINISHED'}

###########################################################################
# Project settings and UI rendering classes

class MeshPositionsSettings(bpy.types.PropertyGroup):
	enable_shuffle: bpy.props.BoolProperty(
		name="Shuffle",
		description="Enable/disable randomisation of the order vertex positions are applied to the target objects (if disabled, Blender's default alpha-numeric sorting is used)",
		default=False)
	keyframe_offset: bpy.props.IntProperty(
		name="Offset",
		description="Number of frames each keyframe will be offset by",
		default=0)

def VFTOOLS_append_panel(self,context):
	try:
		layout = self.layout
	except Exception as exc:
		print(str(exc) + " | Error in View3D Ht Tool Header when adding to panel")

class VFTOOLS_PT_mesh_positions(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = 'VFtools'
	bl_order = 0
	bl_label = "Mesh Positions"
	bl_idname = "VFTOOLS_PT_mesh_positions"

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
			box = layout.box()
			if bpy.context.view_layer.objects.active.type == "MESH":
				box.label(text="Source: " + bpy.context.view_layer.objects.active.name + ", " + str(len(bpy.context.view_layer.objects.active.data.vertices)) + " points")
				box.label(text="Selected: " + str(len(bpy.context.view_layer.objects.selected) - 1) + " items")
			else:
				box.label(text="Error: active object must be a mesh")
			layout.use_property_decorate = False  # No animation
			row = layout.row()
			row.prop(context.scene.vf_mesh_positions_settings, 'enable_shuffle')
			row.prop(context.scene.vf_mesh_positions_settings, 'keyframe_offset')
			layout.operator(VF_Mesh_Position_Offset.bl_idname)
		except Exception as exc:
			print(str(exc) + " | Error in VF Mesh Positions panel")

classes = (VF_Mesh_Position_Offset, MeshPositionsSettings, VFTOOLS_PT_mesh_positions)

###########################################################################
# Addon registration functions

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.vf_mesh_positions_settings = bpy.props.PointerProperty(type=MeshPositionsSettings)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.vf_mesh_positions_settings

if __name__ == "__main__":
	register()

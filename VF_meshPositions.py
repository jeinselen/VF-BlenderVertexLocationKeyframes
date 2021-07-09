bl_info = {
	"name": "VF Mesh Positions",
	"author": "John Einselen - Vectorform LLC",
	"version": (0, 5),
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

# Add random offset ordering, as opposed to just random assignment

# Based on the following resources:
# https://blender.stackexchange.com/questions/1311/how-can-i-get-vertex-positions-from-a-mesh
# https://blender.stackexchange.com/questions/155363/add-on-dev-button-that-simply-calls-a-function
# https://blender.stackexchange.com/questions/133962/how-to-use-keyframes-and-the-python-api-programmatically
# https://www.geeksforgeeks.org/range-to-a-list-in-python/

import bpy
from bpy.app.handlers import persistent
import random

###########################################################################
# Main class

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
		# The active item may or may not be in the selected items group, so we have to make sure we don't include it in our targets
		targets = []
		for i in range(len(bpy.context.view_layer.objects.selected)):
			if bpy.context.view_layer.objects.selected[i].name != bpy.context.view_layer.objects.active.name:
				targets.append(bpy.context.view_layer.objects.selected[i])
		length = min(len(source), len(targets))

		# Randomise the order of the object associations
		assoc = [*range(length)]
		if bpy.context.scene.vf_mesh_positions_settings.shuffle_association:
			random.shuffle(assoc)

		# Randomise the order of the object timing offsets
		timing = [*range(length)]
		if bpy.context.scene.vf_mesh_positions_settings.shuffle_timing:
			random.shuffle(timing)

		# Loop through all of the vertices or objects (whichever is shorter)
		for i in range(length):
			offsetFrame = startFrame + (timing[i] * bpy.context.scene.vf_mesh_positions_settings.keyframe_offset)
			co_transformed = objWorld @ source[i].co
			# targets[assoc[i]].location = co_transformed
			# targets[assoc[i]].keyframe_insert(data_path="location", frame=offsetFrame)
			if bpy.context.scene.vf_mesh_positions_settings.location_x:
				targets[assoc[i]].location[0] = co_transformed[0]
				targets[assoc[i]].keyframe_insert(data_path="location", index = 0, frame=offsetFrame)
			if bpy.context.scene.vf_mesh_positions_settings.location_y:
				targets[assoc[i]].location[1] = co_transformed[1]
				targets[assoc[i]].keyframe_insert(data_path="location", index = 1, frame=offsetFrame)
			if bpy.context.scene.vf_mesh_positions_settings.location_z:
				targets[assoc[i]].location[2] = co_transformed[2]
				targets[assoc[i]].keyframe_insert(data_path="location", index = 2, frame=offsetFrame)

		return {'FINISHED'}

###########################################################################
# Project settings and UI rendering classes

class VFMeshPositionsSettings(bpy.types.PropertyGroup):
	location_x: bpy.props.BoolProperty(
		name="Location X",
		description="Enable/disable keyframing for the X location channel",
		default=True)
	location_y: bpy.props.BoolProperty(
		name="Location Y",
		description="Enable/disable keyframing for the Y location channel",
		default=True)
	location_z: bpy.props.BoolProperty(
		name="Location Z",
		description="Enable/disable keyframing for the Z location channel",
		default=True)
	shuffle_association: bpy.props.BoolProperty(
		name="Shuffle association",
		description="Enable/disable randomisation of the order vertex positions are applied to the target objects (if disabled, items and vertices are sorted by creation order)",
		default=False)
	shuffle_timing: bpy.props.BoolProperty(
		name="Shuffle Timing",
		description="Enable/disable randomisation of which items move first (this maintains the association order of vertices and objects, but randomises the order of the time offsets)",
		default=False)
	keyframe_offset: bpy.props.IntProperty(
		name="Frame Offset",
		description="Number of frames each sequential keyframe will be offset by",
		default=1)

class VFTOOLS_PT_mesh_positions(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = 'VF Tools'
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
			layout.use_property_decorate = False  # No animation
			# row = layout.row()
			# row.prop(context.scene.vf_mesh_positions_settings, 'enable_shuffle')
			# row.prop(context.scene.vf_mesh_positions_settings, 'keyframe_offset')
			row1 = layout.row()
			row1.prop(context.scene.vf_mesh_positions_settings, 'location_x')
			row1.prop(context.scene.vf_mesh_positions_settings, 'location_y')
			row1.prop(context.scene.vf_mesh_positions_settings, 'location_z')
			row2 = layout.row()
			row2.prop(context.scene.vf_mesh_positions_settings, 'shuffle_association')
			row2.prop(context.scene.vf_mesh_positions_settings, 'shuffle_timing')
			layout.prop(context.scene.vf_mesh_positions_settings, 'keyframe_offset')
			box = layout.box()
			if bpy.context.view_layer.objects.active and bpy.context.view_layer.objects.active.type == "MESH":
				if len(bpy.context.view_layer.objects.selected) > 1:
					layout.operator(VF_Mesh_Position_Offset.bl_idname)
					box.label(text=str(len(bpy.context.view_layer.objects.active.data.vertices)) + " vertices in source \"" + bpy.context.view_layer.objects.active.name + "\"")
					if bpy.context.view_layer.objects.active.select_get():
						box.label(text=str(len(bpy.context.view_layer.objects.selected) - 1) + " selected target items")
					else:
						box.label(text=str(len(bpy.context.view_layer.objects.selected)) + " selected target items")
				else:
					box.label(text="Select both source and target objects")
			else:
				box.label(text="Active object must be a mesh")
		except Exception as exc:
			print(str(exc) + " | Error in VF Mesh Positions panel")

classes = (VF_Mesh_Position_Offset, VFMeshPositionsSettings, VFTOOLS_PT_mesh_positions)

###########################################################################
# Addon registration functions

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.vf_mesh_positions_settings = bpy.props.PointerProperty(type=VFMeshPositionsSettings)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.vf_mesh_positions_settings

if __name__ == "__main__":
	register()

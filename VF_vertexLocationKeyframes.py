bl_info = {
	"name": "VF Vertex Location Keyframes",
	"author": "John Einselen - Vectorform LLC",
	"version": (0, 6, 2),
	"blender": (2, 80, 0),
	"location": "Scene > VF Tools > Vertex Location Keyframes",
	"description": "Create location keyframes for selected items based on vertices from a source mesh",
	"warning": "inexperienced developer, use at your own risk",
	"wiki_url": "",
	"tracker_url": "",
	"category": "3D View"}

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

class VF_Vertex_Location_Keyframes(bpy.types.Operator):
	bl_idname = "vfvertexlocationkeyframes.offset"
	bl_label = "Create Keyframes"
	bl_description = "Create location keyframes for each target item"

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

		# Randomise the order of the object orders
		order = [*range(length)]
		if bpy.context.scene.vf_vertex_location_keyframes_settings.shuffle_order:
			random.shuffle(order)

		# Randomise the order of the object timing offsets
		timing = [*range(length)]
		if bpy.context.scene.vf_vertex_location_keyframes_settings.shuffle_timing:
			random.shuffle(timing)

		# Loop through all of the vertices or objects (whichever is shorter)
		for i in range(length):
			offsetFrame = startFrame + (timing[i] * bpy.context.scene.vf_vertex_location_keyframes_settings.keyframe_offset)
			# Transform vertex locations to world space
			if bpy.context.scene.vf_vertex_location_keyframes_settings.world_space:
				co_transformed = objWorld @ source[i].co
			else:
				co_transformed = source[i].co
			# Set locations and keyframes on a per-channel basis to allow for selective location changes
			if bpy.context.scene.vf_vertex_location_keyframes_settings.location_x:
				targets[order[i]].location[0] = co_transformed[0]
				targets[order[i]].keyframe_insert(data_path="location", index = 0, frame=offsetFrame)
			if bpy.context.scene.vf_vertex_location_keyframes_settings.location_y:
				targets[order[i]].location[1] = co_transformed[1]
				targets[order[i]].keyframe_insert(data_path="location", index = 1, frame=offsetFrame)
			if bpy.context.scene.vf_vertex_location_keyframes_settings.location_z:
				targets[order[i]].location[2] = co_transformed[2]
				targets[order[i]].keyframe_insert(data_path="location", index = 2, frame=offsetFrame)

		return {'FINISHED'}

###########################################################################
# Project settings and UI rendering classes

class VFVertexLocationKeyframesSettings(bpy.types.PropertyGroup):
	location_x: bpy.props.BoolProperty(
		name="Location X",
		description="Enable/disable keyframing of the X location channel",
		default=True)
	location_y: bpy.props.BoolProperty(
		name="Location Y",
		description="Enable/disable keyframing of the Y location channel",
		default=True)
	location_z: bpy.props.BoolProperty(
		name="Location Z",
		description="Enable/disable keyframing of the Z location channel",
		default=True)
	world_space: bpy.props.BoolProperty(
		name="World Space",
		description="Enable/disable world space vertex locations (when disabled the vertex locations will be relative to the mesh object)",
		default=True)
	shuffle_order: bpy.props.BoolProperty(
		name="Shuffle Order",
		description="Enable/disable randomisation of the order that items are associated with vertices (when disabled the item and vertex groups are sorted by internal ID, typically order of creation)",
		default=False)
	shuffle_timing: bpy.props.BoolProperty(
		name="Shuffle Timing",
		description="Enable/disable randomisation of the sequence order (this maintains the item and vertex order, but randomises the application of time offsets)",
		default=False)
	keyframe_offset: bpy.props.IntProperty(
		name="Frame Offset",
		description="Number of frames each sequential keyframe will be offset by",
		default=1)

class VFTOOLS_PT_vertex_location_keyframes(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = 'VF Tools'
	bl_order = 2
	bl_options = {'DEFAULT_CLOSED'}
	bl_label = "Vertex Location Keyframes"
	bl_idname = "VFTOOLS_PT_vertex_location_keyframes"

	@classmethod
	def poll(cls, context):
		return True

	def draw_header(self, context):
		try:
			layout = self.layout
		except Exception as exc:
			print(str(exc) + " | Error in VF Vertex Location Keyframes panel header")

	def draw(self, context):
		try:
			layout = self.layout
			layout.use_property_decorate = False # No animation

			row1 = layout.row()
			row1.prop(context.scene.vf_vertex_location_keyframes_settings, 'location_x')
			row1.prop(context.scene.vf_vertex_location_keyframes_settings, 'location_y')
			row1.prop(context.scene.vf_vertex_location_keyframes_settings, 'location_z')

			row2 = layout.row()
			row2.prop(context.scene.vf_vertex_location_keyframes_settings, 'world_space')
			row2.prop(context.scene.vf_vertex_location_keyframes_settings, 'shuffle_order')
			row2.prop(context.scene.vf_vertex_location_keyframes_settings, 'shuffle_timing')
			layout.prop(context.scene.vf_vertex_location_keyframes_settings, 'keyframe_offset')

			box = layout.box()
			if bpy.context.view_layer.objects.active and bpy.context.view_layer.objects.active.type == "MESH":
				if len(bpy.context.view_layer.objects.selected) > 1:
					layout.operator(VF_Vertex_Location_Keyframes.bl_idname)
					box.label(text=str(len(bpy.context.view_layer.objects.active.data.vertices)) + " vertices in source \"" + bpy.context.view_layer.objects.active.name + "\"")
					if bpy.context.view_layer.objects.active.select_get():
						box.label(text=str(len(bpy.context.view_layer.objects.selected) - 1) + " selected target items")
					else:
						box.label(text=str(len(bpy.context.view_layer.objects.selected)) + " selected target items")
				else:
					box.label(text="Select both source mesh and target objects")
			else:
				box.label(text="Active object must be a mesh")
		except Exception as exc:
			print(str(exc) + " | Error in VF Vertex Location Keyframes panel")

classes = (VF_Vertex_Location_Keyframes, VFVertexLocationKeyframesSettings, VFTOOLS_PT_vertex_location_keyframes)

###########################################################################
# Addon registration functions

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.vf_vertex_location_keyframes_settings = bpy.props.PointerProperty(type=VFVertexLocationKeyframesSettings)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.vf_vertex_location_keyframes_settings

if __name__ == "__main__":
	register()

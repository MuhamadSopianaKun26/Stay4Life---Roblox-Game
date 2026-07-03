import bpy
import bmesh
import math

def create_material(name, color, roughness=0.5):
    """Membuat material PBR sederhana."""
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        # Kompatibel dengan Blender 3.x dan 4.x
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
    return mat

def clear_scene():
    """Membersihkan mesh lama dengan nama serupa agar script bisa dijalankan berulang kali."""
    for obj in list(bpy.data.objects):
        if "Medkit" in obj.name or "Cross" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)

def create_medkit():
    clear_scene()

    # 1. Buat Material
    mat_white = create_material("Medkit_White", (0.9, 0.9, 0.93, 1.0), roughness=0.4)
    mat_red = create_material("Medkit_Red", (0.8, 0.05, 0.05, 1.0), roughness=0.3)
    mat_dark = create_material("Medkit_Dark", (0.15, 0.15, 0.17, 1.0), roughness=0.6)

    # 2. Buat Kotak Utama Medkit
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
    box = bpy.context.active_object
    box.name = "Medkit_Box"
    box.scale = (0.9, 0.4, 0.7) 
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Bevel agar low-poly manis
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bevel(offset=0.05, segments=1)
    bpy.ops.object.mode_set(mode='OBJECT')
    box.data.materials.append(mat_white)

    # 3. Buat Logo "+" (Cross) - DIPERBAIKI agar tidak crash
    def add_cross(location, rotation_z, name_suffix):
        # Buat Bar Vertikal
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
        vert_bar = bpy.context.active_object
        vert_bar.scale = (0.18, 0.05, 0.55)
        vert_bar.name = f"Cross_V_{name_suffix}"
        
        # Buat Bar Horizontal
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
        horiz_bar = bpy.context.active_object
        horiz_bar.scale = (0.55, 0.05, 0.18)
        horiz_bar.name = f"Cross_H_{name_suffix}"
        
        # Gabungkan (Join) kedua bar
        bpy.ops.object.select_all(action='DESELECT')
        vert_bar.select_set(True)
        horiz_bar.select_set(True)
        bpy.context.view_layer.objects.active = vert_bar
        bpy.ops.object.join()
        
        cross = bpy.context.active_object
        cross.name = f"Medkit_Cross_{name_suffix}"
        cross.location = location
        cross.rotation_euler[2] = rotation_z
        
        # Apply scale agar tidak distorsi saat di-bevel/edit
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        cross.data.materials.append(mat_red)
        cross.parent = box
        return cross

    # Logo depan (+Y) dan belakang (-Y)
    add_cross((0, -0.41, 0), 0, "Front")
    add_cross((0, 0.41, 0), math.radians(180), "Back")

    # 4. Buat Handle / Pegangan di atas kotak
    def create_handle_part(name, location, scale):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
        part = bpy.context.active_object
        part.name = name
        part.scale = scale
        part.data.materials.append(mat_dark)
        part.parent = box
        # Apply scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        return part

    create_handle_part("Medkit_HandleTop", (0, 0, 0.78), (0.45, 0.12, 0.08))
    create_handle_part("Medkit_HandleL", (-0.18, 0, 0.73), (0.08, 0.12, 0.12))
    create_handle_part("Medkit_HandleR", (0.18, 0, 0.73), (0.08, 0.12, 0.12))

    # 5. Klip pengunci di sisi depan
    for x_pos in [-0.4, 0.4]:
        create_handle_part(f"Medkit_Latch_{x_pos}", (x_pos, -0.405, 0.35), (0.12, 0.04, 0.15))

    # Pilih box sebagai aktif dan rapikan hierarchy
    bpy.ops.object.select_all(action='DESELECT')
    box.select_set(True)
    bpy.context.view_layer.objects.active = box
    
    print("✅ Medkit Low Poly berhasil dibuat!")

if __name__ == "__main__":
    create_medkit()
import bpy
import bmesh
import math
import random

def create_material(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

def clear_scene():
    for obj in bpy.data.objects:
        if "Barricade" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)

def create_wooden_barricade():
    clear_scene()
    random.seed(101)

    # 1. Material Kayu & Paku
    mat_wood1 = create_material("Barricade_WoodLight", (0.45, 0.28, 0.15, 1.0), roughness=0.75)
    mat_wood2 = create_material("Barricade_WoodMed", (0.34, 0.20, 0.10, 1.0), roughness=0.8)
    mat_wood3 = create_material("Barricade_WoodDark", (0.22, 0.13, 0.06, 1.0), roughness=0.85)
    wood_mats = [mat_wood1, mat_wood2, mat_wood3]

    mat_frame = create_material("Barricade_FrameWood", (0.16, 0.10, 0.05, 1.0), roughness=0.9)
    mat_nail = create_material("Barricade_NailMetal", (0.40, 0.42, 0.45, 1.0), roughness=0.3, metallic=0.85)

    # 2. Buat Kusen Jendela (Window Frame)
    frame_objs = []
    configs = [
        ("Frame_L", (-0.95, 0, 0), (0.15, 0.15, 1.3)),
        ("Frame_R", (0.95, 0, 0),  (0.15, 0.15, 1.3)),
        ("Frame_T", (0, 0, 1.15),  (1.1, 0.15, 0.15)),
        ("Frame_B", (0, 0, -1.15), (1.1, 0.15, 0.15)),
    ]
    
    # Objek induk utama
    parent_empty = bpy.data.objects.new("Barricade_Root", None)
    bpy.context.collection.objects.link(parent_empty)

    for name, loc, sc in configs:
        bpy.ops.mesh.primitive_cube_add(size=2.0, location=loc)
        obj = bpy.context.active_object
        obj.name = f"Barricade_{name}"
        obj.scale = sc
        obj.data.materials.append(mat_frame)
        obj.parent = parent_empty

    # 3. Buat Papan & Serpihan Kayu yang Dipaku (Wood Planks & Splinters)
    def add_plank(name, loc, rot_z, length, width=0.18, thickness=0.04, mat=None):
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=2.0)
        
        # Atur skala & sedikit distorsi sudut agar terlihat seperti serpihan kasar
        for v in bm.verts:
            v.co.x *= (length / 2.0) * random.uniform(0.92, 1.08)
            v.co.y *= thickness / 2.0
            v.co.z *= (width / 2.0) * random.uniform(0.88, 1.12)
            
        bm.to_mesh(mesh)
        bm.free()
        
        obj.location = loc
        obj.rotation_euler = (random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), rot_z)
        obj.data.materials.append(mat if mat else random.choice(wood_mats))
        obj.parent = parent_empty
        return obj

    # Daftar papan utama yang menutupi jendela
    plank_defs = [
        # (Z_pos, rot_z, length)
        (0.8,  math.radians(0),   2.1),
        (0.4,  math.radians(0),  1.9),
        (0.0,  math.radians(0),   2.2),
        (-0.35, math.radians(0), 1.8),
        (-0.75, math.radians(0), 2.0),
        # Papan diagonal silang
        (0.1,  math.radians(0),  2.5),
        (-0.1, math.radians(0), 2.4),
    ]

    created_planks = []
    for i, (z, rot, length) in enumerate(plank_defs):
        # Y ditaruh sedikit di depan kusen (-0.12 sampai -0.22) agar menumpuk berlapis
        y_off = -0.15 - (i * 0.018)
        plank = add_plank(f"Barricade_Plank_{i+1}", (random.uniform(-0.08, 0.08), y_off, z), rot, length)
        created_planks.append((plank, length, y_off))

    # 4. Tambahkan Serpihan Kayu Tambahan (Splinter Pieces yang ditambal-sulam)
    for i in range(10):
        z_pos = random.uniform(-0.9, 0.9)
        x_pos = random.uniform(-0.7, 0.7)
        y_pos = -0.26 - (i * 0.01)
        rot = random.uniform(-0.5, 0.5)
        add_plank(f"Barricade_Splinter_{i+1}", (x_pos, y_pos, z_pos), rot, length=random.uniform(0.4, 0.8), width=random.uniform(0.08, 0.14), thickness=0.035)

    # 5. Tambahkan Paku Besi (Nails) pada setiap papan dan serpihan
    def add_nail(loc):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=0.04, location=loc)
        nail = bpy.context.active_object
        nail.name = "Barricade_Nail"
        nail.rotation_euler[0] = math.radians(90)  # Menghadap ke depan (-Y)
        nail.data.materials.append(mat_nail)
        nail.parent = parent_empty

    # Pasang 2 paku di ujung kiri dan kanan setiap papan utama
    for plank, length, y_off in created_planks:
        for side in [-1, 1]:
            nail_x = side * (length * 0.42)
            nail_z = plank.location.z + random.uniform(-0.03, 0.03)
            add_nail((nail_x, y_off - 0.03, nail_z))

    bpy.ops.object.select_all(action='DESELECT')
    parent_empty.select_set(True)
    bpy.context.view_layer.objects.active = parent_empty
    print("Barricade Kayu jendela dari serpihan kayu dan paku berhasil dibuat!")

if __name__ == "__main__":
    create_wooden_barricade()

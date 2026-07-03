import bpy
import bmesh
import math

def create_material(name, color, roughness=0.5, metallic=0.0):
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
        if "Grenade" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)

def create_grenade():
    clear_scene()

    # 1. Buat Material
    # Warna Hijau Tua untuk body granat
    mat_green = create_material("Grenade_GreenDark", (0.07, 0.14, 0.06, 1.0), roughness=0.5, metallic=0.2)
    # Warna Abu-abu metalik untuk handle tuas, pin, dan cincin
    mat_metal = create_material("Grenade_GreyMetal", (0.55, 0.58, 0.60, 1.0), roughness=0.3, metallic=0.85)

    # 2. Buat Body Granat Kotak-Kotak (Pineapple Frag Grenade)
    mesh_body = bpy.data.meshes.new("GrenadeBodyMesh")
    obj_body = bpy.data.objects.new("Grenade_Body", mesh_body)
    bpy.context.collection.objects.link(obj_body)

    bm = bmesh.new()
    # Buat UV Sphere sebagai dasar oval nanas
    bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=0.55)

    # Regangkan vertikal (sumbu Z) agar berbentuk oval
    for v in bm.verts:
        v.co.z *= 1.28

    # Ambil face bagian tengah (hindari kutub paling atas & bawah agar rapi)
    faces_to_extrude = [f for f in bm.faces if abs(f.calc_center_median().z) < 0.55 and len(f.verts) == 4]

    # Inset individual dengan depth positif untuk menghasilkan tekstur timbul "kotak-kotak"
    bmesh.ops.inset_individual(bm, faces=faces_to_extrude, thickness=0.04, depth=0.05)

    bm.to_mesh(mesh_body)
    bm.free()
    obj_body.data.materials.append(mat_green)

    # 3. Leher / Fuse Kepala Granat
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.18, depth=0.35, location=(0, 0, 0.75))
    fuse = bpy.context.active_object
    fuse.name = "Grenade_Fuse"
    fuse.data.materials.append(mat_metal)
    fuse.parent = obj_body

    # 4. Handle Pin / Tuas Safety Lever
    # Kita buat kubus yang diposisikan memanjang ke bawah di samping body
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.22, 0, 0.5))
    lever = bpy.context.active_object
    lever.name = "Grenade_Lever"
    lever.scale = (0.06, 0.16, 0.45)
    lever.rotation_euler[1] = math.radians(12)  # Miring mengikuti lengkungan body granat
    lever.data.materials.append(mat_metal)
    lever.parent = obj_body

    # Bagian atas tuas yang melengkung ke leher fuse
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.1, 0, 0.85))
    lever_top = bpy.context.active_object
    lever_top.name = "Grenade_LeverTop"
    lever_top.scale = (0.16, 0.16, 0.05)
    lever_top.data.materials.append(mat_metal)
    lever_top.parent = obj_body

    # 5. Cincin Pengaman (Safety Pin Ring)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.12, 
        minor_radius=0.02, 
        major_segments=16, 
        minor_segments=8, 
        location=(-0.25, 0, 0.75)
    )
    ring = bpy.context.active_object
    ring.name = "Grenade_SafetyRing"
    ring.rotation_euler = (0, math.radians(90), 0)
    ring.data.materials.append(mat_metal)
    ring.parent = obj_body

    # Batang pin penahan (melintang dari cincin ke fuse)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.018, depth=0.3, location=(-0.08, 0, 0.75))
    pin_bar = bpy.context.active_object
    pin_bar.name = "Grenade_PinBar"
    pin_bar.rotation_euler = (0, math.radians(90), 0)
    pin_bar.data.materials.append(mat_metal)
    pin_bar.parent = obj_body

    # Pilih body granat sebagai objek aktif
    bpy.ops.object.select_all(action='DESELECT')
    obj_body.select_set(True)
    bpy.context.view_layer.objects.active = obj_body
    print("Granat Hijau Tua dengan tekstur kotak-kotak berhasil dibuat!")

if __name__ == "__main__":
    create_grenade()

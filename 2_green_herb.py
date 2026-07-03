import bpy
import bmesh
import math

def create_material(name, color, roughness=0.6):
    """Membuat material PBR sederhana."""
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
    return mat

def clear_scene():
    """Membersihkan objek lama dengan nama serupa."""
    for obj in bpy.data.objects:
        if "Herb" in obj.name or "Pot" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)

def create_green_herb():
    clear_scene()

    # 1. Buat Material
    mat_pot = create_material("Herb_PotBrown", (0.45, 0.22, 0.12, 1.0), roughness=0.7)
    mat_soil = create_material("Herb_SoilDark", (0.08, 0.05, 0.03, 1.0), roughness=0.9)
    mat_stem = create_material("Herb_StemGreen", (0.12, 0.35, 0.10, 1.0), roughness=0.5)
    mat_leaf = create_material("Herb_LeafGreen", (0.15, 0.55, 0.12, 1.0), roughness=0.4)

    # 2. Buat Pot Coklat Low Poly
    mesh_pot = bpy.data.meshes.new("HerbPotMesh")
    obj_pot = bpy.data.objects.new("Herb_Pot", mesh_pot)
    bpy.context.collection.objects.link(obj_pot)

    bm = bmesh.new()
    # Kerucut terpotong (segmen dikurangi jadi 10 agar low poly estetik)
    bmesh.ops.create_cone(bm, segments=10, radius1=0.45, radius2=0.32, depth=0.7)
    # Geser sedikit agar dasar pot pas di Z=0
    for v in bm.verts:
        v.co.z += 0.35
    
    # Ekstrude bibir pot
    top_faces = [f for f in bm.faces if f.calc_center_median().z > 0.69]
    res_inset = bmesh.ops.inset_individual(bm, faces=top_faces, thickness=0.06, depth=0.0)
    
    # Ekstrude ke dalam pot (ongga untuk tanah)
    bmesh.ops.extrude_discrete_faces(bm, faces=res_inset["faces"])
    for f in res_inset["faces"]:
        for v in f.verts:
            v.co.z -= 0.15

    bm.to_mesh(mesh_pot)
    bm.free()
    obj_pot.data.materials.append(mat_pot)

    # 3. Buat Tanah (Soil)
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.38, depth=0.05, location=(0, 0, 0.55))
    soil = bpy.context.active_object
    soil.name = "Herb_Soil"
    soil.data.materials.append(mat_soil)
    soil.parent = obj_pot

    # 4. Buat Batang Utama (Stem)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=1.3, location=(0, 0, 0.8))
    stem = bpy.context.active_object
    stem.name = "Herb_Stem"
    stem.data.materials.append(mat_stem)
    stem.parent = obj_pot

    # 5. Buat Daun Low Poly Khas Resident Evil Green Herb
    def create_single_leaf(name, length=0.6, width=0.25):
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        
        # Koordinat custom daun berlian dengan lipatan tengah
        verts = [
            (0.0, 0.0, 0.0),           # 0: pangkal daun (di batang)
            (-width/2, length*0.4, 0.05), # 1: kiri
            (width/2, length*0.4, 0.05),  # 2: kanan
            (0.0, length*0.45, -0.05), # 3: lipatan tengah bawah
            (0.0, length, -0.1)        # 4: ujung daun runcing
        ]
        faces = [
            (0, 1, 3),
            (0, 3, 2),
            (3, 1, 4),
            (3, 4, 2)
        ]
        
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj.data.materials.append(mat_leaf)
        obj.parent = stem
        return obj

    # Atur posisi 7 daun menyebar berlapis di sekitar batang
    leaf_configs = [
        # (angle_deg, z_offset, tilt_deg, scale)
        (0,   0.5, 45, 1.1),
        (72,  0.8, 42, 1.0),
        (144, 0.6, 48, 1.05),
        (216, 0.9, 40, 0.95),
        (288, 0.4, 46, 1.1),
        # Lapisan atas lebih mendongak dan sedikit lebih kecil
        (36,  0.22, 30, 0.85),
        (180, 0.25, 28, 0.8)
    ]

    for i, (angle, z_off, tilt, sc) in enumerate(leaf_configs):
        leaf = create_single_leaf(f"Herb_Leaf_{i+1}")
        leaf.location = (0, 0, (z_off - 0.3)) # Relatif thd pusat batang
        leaf.rotation_euler = (math.radians(tilt), 0, math.radians(angle))
        leaf.scale = (sc, sc, sc)

    bpy.ops.object.select_all(action='DESELECT')
    obj_pot.select_set(True)
    bpy.context.view_layer.objects.active = obj_pot
    print("Green Herb Low Poly Resident Evil berhasil dibuat!")

if __name__ == "__main__":
    create_green_herb()

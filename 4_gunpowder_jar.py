import bpy
import bmesh
import math
import random

def create_material(name, color, roughness=0.5, alpha=1.0, transmission=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    if alpha < 1.0 or transmission > 0.0:
        if bpy.app.version < (4, 0, 0):
            mat.blend_method = 'BLEND'
            mat.shadow_method = 'HASHED'
        else:

            if hasattr(mat, 'surface_render_method'):
                mat.surface_render_method = 'DITHERED' 
        
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in bsdf.inputs:
            bsdf.inputs["Transmission"].default_value = transmission
    return mat

def clear_scene():
    for obj in list(bpy.data.objects):
        if "Gunpowder" in obj.name or "PowderJar" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)
            
    col = bpy.data.collections.get("Gunpowder_Grains")
    if col:
        bpy.data.collections.remove(col)

def create_gunpowder_jar():
    clear_scene()
    random.seed(42)  # Seed agar posisi serbuk konsisten & rapi

    # 1. Material
    mat_glass = create_material("Gunpowder_GlassJar", (0.85, 0.9, 0.92, 0.35), roughness=0.15, alpha=0.35, transmission=0.85)
    mat_lid = create_material("Gunpowder_LidBrown", (0.38, 0.22, 0.12, 1.0), roughness=0.8)
    mat_powder = create_material("Gunpowder_Black", (0.05, 0.05, 0.06, 1.0), roughness=0.95)

    # 2. Wadah Kaca (Jar Body) - Low Poly Octagonal
    mesh_jar = bpy.data.meshes.new("JarMesh")
    obj_jar = bpy.data.objects.new("Gunpowder_JarBody", mesh_jar)
    bpy.context.collection.objects.link(obj_jar)

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, segments=8, radius1=0.45, radius2=0.45, depth=0.8)
    for v in bm.verts:
        v.co.z += 0.4  

    # PERBAIKAN: Cari top face berdasarkan Normal (lebih aman daripada Z coordinate)
    top_faces = [f for f in bm.faces if f.normal.z > 0.9]
    
    if top_faces:
        res_inset = bmesh.ops.inset_individual(bm, faces=top_faces, thickness=0.1, depth=0.0)
        res_ext = bmesh.ops.extrude_discrete_faces(bm, faces=res_inset["faces"])
        for f in res_ext["faces"]:
            for v in f.verts:
                v.co.z += 0.15

    bm.to_mesh(mesh_jar)
    bm.free()
    obj_jar.data.materials.append(mat_glass)

    # 3. Isi Gun Powder di dalam Botol
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.38, depth=0.55, location=(0, 0, 0.32))
    inner_powder = bpy.context.active_object
    inner_powder.name = "Gunpowder_InnerContent"
    inner_powder.data.materials.append(mat_powder)
    inner_powder.parent = obj_jar

    # Buat permukaan atas isi tidak rata
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=1)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    for v in inner_powder.data.vertices:
        if v.co.z > 0.2:
            v.co.z += random.uniform(-0.05, 0.06)
            
    # PERBAIKAN: Update mesh agar perubahan vertex langsung terlihat
    inner_powder.data.update()

    # 4. Penutup Botol (Cork/Lid)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.38, depth=0.18, location=(0, 0, 0.98))
    lid = bpy.context.active_object
    lid.name = "Gunpowder_Lid"
    lid.data.materials.append(mat_lid)
    lid.parent = obj_jar

    # 5. Serbuk-serbuk Hitam (Grains)
    grains_col = bpy.data.collections.new("Gunpowder_Grains")
    bpy.context.scene.collection.children.link(grains_col)

    def add_grain(loc, scale_fac, name):
        mesh_g = bpy.data.meshes.new(name)
        obj_g = bpy.data.objects.new(name, mesh_g)
        grains_col.objects.link(obj_g)
        
        bm_g = bmesh.new()
        bmesh.ops.create_icosphere(bm_g, subdivisions=1, radius=0.03 * scale_fac)
        for v in bm_g.verts:
            v.co.x *= random.uniform(0.6, 1.4)
            v.co.y *= random.uniform(0.6, 1.4)
            v.co.z *= random.uniform(0.4, 1.2)
        bm_g.to_mesh(mesh_g)
        bm_g.free()
        
        obj_g.location = loc
        obj_g.rotation_euler = (random.uniform(0, 3.14), random.uniform(0, 3.14), random.uniform(0, 3.14))
        obj_g.data.materials.append(mat_powder)
        obj_g.parent = obj_jar
        return obj_g

    # Taburan serbuk di dasar botol
    for i in range(40):
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(0.35, 0.75)
        x = math.cos(angle) * dist
        y = math.sin(angle) * dist
        z = random.uniform(0.005, 0.04)
        add_grain((x, y, z), random.uniform(0.7, 1.8), f"Gunpowder_GrainBottom_{i}")

    # Taburan serbuk di bagian atas
    for i in range(20):
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(0.25, 0.48)
        x = math.cos(angle) * dist
        y = math.sin(angle) * dist
        z = random.uniform(0.85, 0.98)
        add_grain((x, y, z), random.uniform(0.5, 1.3), f"Gunpowder_GrainTop_{i}")

    # Pilih jar sebagai aktif
    bpy.ops.object.select_all(action='DESELECT')
    obj_jar.select_set(True)
    bpy.context.view_layer.objects.active = obj_jar
    
    print("Wadah Gun Powder dengan serbuk hitam berhasil dibuat!")

if __name__ == "__main__":
    create_gunpowder_jar()
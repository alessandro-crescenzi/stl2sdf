import os  # to walk through directories, to rename files
import argparse
# Libraries
import trimesh  # for converting voxel grids to meshes (to import objects into simulators)

# Modules
import tools_sdf_generator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script converts an STL file into a model that can be spawned in"
                                                 "Gazebo simulator for ROS Noetic")

    # Mandatory argument
    parser.add_argument("file", type=str, help="The path to the stl file")

    # Optional arguments
    parser.add_argument("--scaling_factor", type=int, default=1.0, help="Scaling factor for the conversion"
                                                                        " from STL to SDF")
    parser.add_argument("--object_is_static", action="store_true", default=True)
    parser.add_argument("--max_contacts", type=int, default=20)
    parser.add_argument("--author_name", type=str, default="")
    parser.add_argument("--author_email", type=str, default="")
    parser.add_argument("--element_description", type=str, default="")

    args = parser.parse_args()

    filename = args.file
    scaling_factor = args.scaling_factor
    object_is_static = args.object_is_static
    max_contacts = args.max_contacts
    author_name = args.author_name
    author_email = args.author_email
    element_description = args.element_description

    # Generate a folder to store the images
    print("Generating a folder to save the mesh")
    # Generate a folder with the same name as the input file, without its ".binvox" extension
    name, _ = os.path.splitext(filename)
    directory = name
    os.makedirs(os.path.join(directory, "meshes"), exist_ok=True)

    mesh = trimesh.load(filename)
    # scaling_factor = 100
    mesh.apply_scale(scaling=scaling_factor)

    mass = mesh.volume  # WATER density
    print("\n\nMesh volume: {} (used as mass)".format(mesh.volume))
    print("Mass (equal to volume): {0}".format(mass))
    print("Mesh convex hull volume: {}\n\n".format(mesh.convex_hull.volume))
    print("Mesh bounding box volume: {}".format(mesh.bounding_box.volume))

    print("Merging vertices closer than a pre-set constant...")
    mesh.merge_vertices()
    print("Removing duplicate faces...")
    mesh.update_faces(mesh.unique_faces())
    print("Making the mesh watertight...")
    trimesh.repair.fill_holes(mesh)
    # print("Fixing inversion and winding...")
    # trimesh.repair.fix_winding(mesh)
    # trimesh.repair.fix_inversion(mesh)
    trimesh.repair.fix_normals(mesh)

    print("\n\nMesh volume: {}".format(mesh.volume))
    print("Mesh convex hull volume: {}".format(mesh.convex_hull.volume))
    print("Mesh bounding box volume: {}".format(mesh.bounding_box.volume))

    print("Computing the center of mass: ")
    center_of_mass = mesh.center_mass
    print(center_of_mass)

    print("Computing moments of inertia: ")
    moments_of_inertia = mesh.moment_inertia
    print(moments_of_inertia)  # inertia tensor in meshlab

    print("Generating the STL mesh file")
    trimesh.exchange.export.export_mesh(
        mesh=mesh,
        file_obj=os.path.join(directory, "meshes", filename),
        file_type="stl"
    )

    print("Generating the SDF files...")

    tools_sdf_generator.generate_model_sdf(
        directory=directory,
        object_name=name,
        center_of_mass=center_of_mass,
        inertia_tensor=moments_of_inertia,
        mass=mass,
        model_stl_path=os.path.join(directory, "meshes", filename),
        object_is_static=object_is_static,
        max_contacts=max_contacts)

    tools_sdf_generator.generate_sdf_config(
        directory=directory,
        object_name=name,
        author_name=author_name,
        author_email=author_email,
        element_description=element_description
    )

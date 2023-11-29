import os
import xml.etree.ElementTree as ET
import xml.dom.minidom


def generate_model_sdf(directory,
                       object_name,
                       center_of_mass,
                       inertia_tensor,
                       mass,
                       model_stl_path,
                       object_is_static,
                       max_contacts):
    # http://sdformat.org/spec?ver=1.6&elem=visual

    # Object mass format: scalar
    # Center of Mass format: [x,y,z]
    # Inertia tensor format:
    # | ixx ixy ixz |
    # | ixy iyy iyz |
    # | ixz iyz izz |
    ixx = round(inertia_tensor[0][0], 20)
    ixy = round(inertia_tensor[0][1], 20)
    ixz = round(inertia_tensor[0][2], 20)
    iyy = round(inertia_tensor[1][1], 20)
    iyz = round(inertia_tensor[1][2], 20)
    izz = round(inertia_tensor[2][2], 20)

    sdf_model = ET.Element("sdf", version="1.4")
    model = ET.SubElement(sdf_model, "model", name=object_name)
    static = ET.SubElement(model, "static")
    static.text = str(object_is_static)

    link = ET.SubElement(model, "link", name="link")

    pose = ET.SubElement(link, "pose")
    pose.text = "0 0 0 0 0 0"

    inertial = ET.SubElement(link, "inertial")
    inertial_pose = ET.SubElement(inertial, "pose")
    inertial_pose.text = f"{round(center_of_mass[0], 10)} {round(center_of_mass[1], 10)} {round(center_of_mass[2], 10)} 0 0 0"
    mass_elem = ET.SubElement(inertial, "mass")
    mass_elem.text = str(round(mass, 6))

    inertia = ET.SubElement(inertial, "inertia")
    ixx_elem = ET.SubElement(inertia, "ixx")
    ixx_elem.text = str(ixx)
    ixy_elem = ET.SubElement(inertia, "ixy")
    ixy_elem.text = str(ixy)
    ixz_elem = ET.SubElement(inertia, "ixz")
    ixz_elem.text = str(ixz)
    iyy_elem = ET.SubElement(inertia, "iyy")
    iyy_elem.text = str(iyy)
    iyz_elem = ET.SubElement(inertia, "iyz")
    iyz_elem.text = str(iyz)
    izz_elem = ET.SubElement(inertia, "izz")
    izz_elem.text = str(izz)

    visual = ET.SubElement(link, "visual", name="visual")
    geometry = ET.SubElement(visual, "geometry")
    mesh = ET.SubElement(geometry, "mesh")
    uri = ET.SubElement(mesh, "uri")
    uri.text = "model://" + model_stl_path

    material = ET.SubElement(visual, "material")
    script = ET.SubElement(material, "script")
    uri_material = ET.SubElement(script, "uri")
    uri_material.text = "file://media/materials/scripts/gazebo.material"
    name = ET.SubElement(script, "name")
    name.text = "Gazebo/Green"

    collision = ET.SubElement(link, "collision", name="collision")
    max_contacts_element = ET.SubElement(collision, "max_contacts")
    max_contacts_element.text = str(max_contacts)
    geometry_collision = ET.SubElement(collision, "geometry")
    mesh_collision = ET.SubElement(geometry_collision, "mesh")
    uri_collision = ET.SubElement(mesh_collision, "uri")
    uri_collision.text = "model://" + model_stl_path

    # Convert XML structure to string with indentation
    xml_string = xml.dom.minidom.parseString(ET.tostring(sdf_model)).toprettyxml()

    with open(os.path.join(directory, "model.sdf"), "w") as xml_file:
        xml_file.write('<?xml version="1.0"?>\n' + xml_string)


def generate_sdf_config(directory,
                        object_name,
                        author_name,
                        author_email,
                        element_description):
    # config file creation
    model_config = ET.Element("model")
    name_elem = ET.SubElement(model_config, "name")
    name_elem.text = object_name

    version_elem = ET.SubElement(model_config, "version")
    version_elem.text = "1.0"

    sdf_elem = ET.SubElement(model_config, "sdf", version="1.6")
    sdf_elem.text = "model.sdf"

    author_elem = ET.SubElement(model_config, "author")
    author_name_elem = ET.SubElement(author_elem, "name")
    author_name_elem.text = author_name
    author_email_elem = ET.SubElement(author_elem, "email")
    author_email_elem.text = author_email

    description_elem = ET.SubElement(model_config, "description")
    description_elem.text = element_description

    # Convert XML structure to string with indentation
    xml_string = xml.dom.minidom.parseString(ET.tostring(model_config)).toprettyxml()

    with open(os.path.join(directory, "model.config"), "w") as xml_file:
        xml_file.write('<?xml version="1.0"?>\n' + xml_string)


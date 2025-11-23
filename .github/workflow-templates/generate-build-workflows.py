#!/usr/bin/env python3
import json
import os

# Paths
TEMPLATES_DIR = os.path.dirname(__file__)
DISTROS_FILE = os.path.join(TEMPLATES_DIR, "distros.json")
OUTPUT_DIR = os.path.join(TEMPLATES_DIR, "../workflows")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Map template filename → tag prefix pattern
TEMPLATE_TAG_PREFIX = {
    "builds.yml": "builds-{{NAME_SHORT}}",
    "builds-with-pimbra.yml": "builds-with-pimbra-{{NAME_SHORT}}",
    "docker-builds.yml": "docker-builds-{{NAME_SHORT}}"
}

def generate_workflow(template_content: str, distro: dict, output_dir: str, tag_prefix_template: str) -> str:
    """
    Generate a per-distro workflow YAML for a given distro using the template.
    Replaces {{MATRIX_SECTION}} with empty string for single-distro workflows.
    """
    name_short = distro["name"].lower().replace(" ", "-")
    workflow_content = template_content

    # Replace placeholders
    workflow_content = workflow_content.replace("{{NAME}}", distro["name"])
    workflow_content = workflow_content.replace("{{NAME_SHORT}}", name_short)
    workflow_content = workflow_content.replace("{{DOCKER_TAG}}", distro.get("docker_tag", ""))
    workflow_content = workflow_content.replace("{{BUILD_DIR_PREFIX}}", distro.get("build_dir_prefix", ""))
    workflow_content = workflow_content.replace("{{TAG_PREFIX}}", tag_prefix_template.replace("{{NAME_SHORT}}", name_short))
    workflow_content = workflow_content.replace("{{FULLNAME}}", distro["fullname"])
    workflow_content = workflow_content.replace("{{MATRIX_SECTION}}", "")  # single-distro
    workflow_content = workflow_content.replace("{{VERSION}}", distro.get("version", ""))
    workflow_content = workflow_content.replace("{{DISTRO_FAMILY}}", distro.get("distro_family", ""))
    workflow_content = workflow_content.replace("{{DOCKERFILE}}", distro.get("dockerfile", ""))

    # Output filename matches tag prefix
    output_file = os.path.join(output_dir, f"{tag_prefix_template.replace('{{NAME_SHORT}}', name_short)}.yml")
    with open(output_file, "w") as f:
        f.write(workflow_content)

    return output_file

def generate_matrix_workflow(template_content: str, output_file: str, distros: list, tag_prefix: str) -> str:
    """
    Generate a matrix workflow YAML that includes all distros in one workflow.
    """
    workflow_content = template_content

    # Build YAML matrix block manually
    matrix_lines = ["    strategy:", "      matrix:", "        distro:"]
    for d in distros:
        matrix_lines.append(f"          - name: {d['name'].lower().replace(' ', '-')}")
        matrix_lines.append(f"            docker_tag: {d.get('docker_tag', '')}")
        matrix_lines.append(f"            build_dir_prefix: {d.get('build_dir_prefix', '')}")
        matrix_lines.append(f"            fullname: {d['fullname']}")

    matrix_yaml = "\n".join(matrix_lines)

    # Replace placeholders
    workflow_content = workflow_content.replace("{{MATRIX_SECTION}}", matrix_yaml)
    workflow_content = workflow_content.replace("{{TAG_PREFIX}}", tag_prefix)
    workflow_content = workflow_content.replace("{{NAME_SHORT}}", "all")
    workflow_content = workflow_content.replace("{{DOCKER_TAG}}", "")  # Docker tag per matrix entry
    workflow_content = workflow_content.replace("{{BUILD_DIR_PREFIX}}", "")  # per matrix entry
    workflow_content = workflow_content.replace("{{FULLNAME}}", "all")

    output_path = os.path.join(OUTPUT_DIR, output_file)
    with open(output_path, "w") as f:
        f.write(workflow_content)

    return output_path

def main():
    # Load distros
    with open(DISTROS_FILE, "r") as f:
        distros = json.load(f)

    # Generate per-distro workflows
    for template_file, tag_prefix_template in TEMPLATE_TAG_PREFIX.items():
        template_path = os.path.join(TEMPLATES_DIR, template_file)
        with open(template_path, "r") as f:
            template_content = f.read()

        for distro in distros:
            # For docker-builds, only generate per-distro; no matrix
            output_file = generate_workflow(template_content, distro, OUTPUT_DIR, tag_prefix_template)
            print(f"Generated workflow: {output_file}")

        # Generate matrix workflow only for builds.yml and builds-with-pimbra.yml
        if template_file in ["builds.yml", "builds-with-pimbra.yml"]:
            matrix_tag_prefix = "builds" if template_file == "builds.yml" else "builds-with-pimbra"
            output_file = template_file  # matrix workflow overwrites template filename
            output_file_path = generate_matrix_workflow(template_content, output_file, distros, matrix_tag_prefix)
            print(f"Generated matrix workflow: {output_file_path}")

if __name__ == "__main__":
    main()

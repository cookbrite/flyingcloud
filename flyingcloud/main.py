#!/usr/bin/env python

from __future__ import unicode_literals, absolute_import, print_function

import os
import platform

import sh
import sys

import yaml

from .base import DockerBuildLayer


def get_layer(layer_base_class, layer_name, layer_info):
    # TODO: make these use defaults so they can be optional
    layer = layer_base_class(layer_base_class.AppName, command_name=layer_name)
    layer.__doc__ = "Parsed from {}".format(layer_name)
    layer.Description = layer_info['description']
    layer.ExposedPorts = layer_info['exposed_ports']
    layer.SourceImageBaseName = '{}_{}'.format(
        layer_base_class.AppName, layer_info["parent"])
    layer.set_layer_defaults()

    return layer

def configure_layers(project_root):
    project_name, project_info, layers_info = get_project_info(project_root)
    return parse_project_yaml(project_name=project_name,
                                project_info=project_info,
                                layers_info=layers_info)


def parse_project_yaml(project_name=None, project_info=None, layers_info=None):
    class NewLayer(DockerBuildLayer):
        pass

    # shared settings
    # TODO: make these use defaults so they can be optional
    NewLayer.project_filename = project_name
    NewLayer.USERNAME_VAR = project_info['username_varname']
    NewLayer.PASSWORD_VAR = project_info['password_varname']
    NewLayer.Registry = project_info['registry']
    NewLayer.RegistryDockerVersion = project_info['registry_docker_version']
    NewLayer.Organization = project_info['organization']
    NewLayer.AppName = project_info['app_name']
    NewLayer.LoginRequired = project_info['login_required']
    NewLayer.SquashLayer = project_info['squash_layer']
    NewLayer.PushLayer = project_info['push_layer']
    NewLayer.PullLayer = project_info['pull_layer']

    layers = []
    for layer_name in project_info["layers"]:
        layers.append(get_layer(NewLayer, layer_name, layers_info[layer_name]))

    return layers


def get_project_info(project_root):
    project_filename = os.path.join(project_root, "flyingcloud.yaml")
    project_name = os.path.basename(project_root)
    with open(project_filename) as fp:
        project_info = yaml.load(fp)

    layers_info = {}
    for layer_name in project_info['layers']:
        layer_filename = os.path.join(project_root, "salt", layer_name, "layer.yaml")
        with open(layer_filename) as fp:
            info = yaml.load(fp)
            layers_info[layer_name] = info

    return project_name, project_info, layers_info


def main():
    if os.geteuid() != 0 and platform.system() == "Linux":
        sudo_command = sh.Command('sudo')
        sudo_command([sys.executable] + sys.argv)
        return

    project_root = os.getcwd()
    base_dir = os.path.abspath(project_root)
    defaults = dict(
        base_dir=base_dir,
    )

    try:
        layers = configure_layers(project_root)
        if not layers:
            raise ValueError("Uh!")
    except:
        # TODO: argparse help
        raise

    layers[0].main(
        defaults,
        *layers,
        description="Build Docker images using SaltStack")

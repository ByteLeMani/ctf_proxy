import os
import importlib
import sys
import shutil


def generate_module_files(service_names, base_directory):
    template_path = os.path.join(base_directory, "template.py")
    for service_name in service_names:
        service_path = os.path.join(base_directory, service_name)
        try:
            os.mkdir(service_path)
        except FileExistsError:
            pass
        sys.path.append(service_path)
        in_module_path = os.path.join(service_path, service_name + "_in.py")
        out_module_path = os.path.join(service_path, service_name + "_out.py")
        if not os.path.isfile(in_module_path):
            shutil.copy(template_path, in_module_path)
            os.chmod(in_module_path, 0o777)
        if not os.path.isfile(out_module_path):
            shutil.copy(template_path, out_module_path)
            os.chmod(out_module_path, 0o777)


def import_modules(service_name, reload=True):
    in_module_name = service_name + "_in"
    out_module_name = service_name + "_out"
    try:
        if reload:
            importlib.reload(importlib.import_module((in_module_name)))
            importlib.reload(importlib.import_module((out_module_name)))
        else:
            __import__(in_module_name)
            __import__(out_module_name)
        in_module = sys.modules[in_module_name].Module()
        out_module = sys.modules[out_module_name].Module()
    except ImportError as e:
        print('Module %s not found' % service_name)
        print(e.msg)
        sys.exit(3)
    return in_module, out_module

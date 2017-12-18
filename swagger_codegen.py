import subprocess
import os
import shutil

"""
This file is used to update and install the Python Client of the swagger api.
First it runs the Swagger Codegen tool to connect to the server and retrieve the swagger OpenAPI specification.
Then it generates the Python Client using the code templates file.
Finally, it will pip install the Python Client package into the Python environment.
"""


def locate_swagger_codegen_file(directory_to_search):
    for f in os.listdir(directory_to_search):
        if '.jar' in f:
            return os.path.join(directory_to_search, f)

    raise Exception("Could not locate swagger codegen .jar file in: " + directory_to_search)


def generate_swagger_api_code(url, language='python', package_name='swagger_api_client'):
    working_dir = os.getcwd()
    here = os.path.abspath(os.path.dirname(__file__))
    swagger_codegen_jar_file = locate_swagger_codegen_file(here)
    output_dir = os.path.join(here, 'swagger_source')

    # Remove previous install if it exists
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)

    print "Building Python Client"
    subprocess.check_output(['java', '-jar', swagger_codegen_jar_file, 'generate', '-i', url, '-l', language, '-o', output_dir, '-DmodelTests=false,apiTests=false,packageName=' + package_name])
    print "Installing Python Client: %s" % package_name
    os.chdir(output_dir)  # switch to package directory
    subprocess.check_output(['pip', 'install', '.', '-U'])
    os.chdir(working_dir)  # switch back to previous working directory

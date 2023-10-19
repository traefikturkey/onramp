import os
import subprocess
import sys
from shutil import copyfile

def read_variables(filename, prefix):
    variables = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith(prefix):
                variable = line[:line.index('=')].strip()
                variables.append(variable)
    return variables

def prompt_user_for_values(variables):
    values = {}
    for var in variables:
        value = input(f"Enter a value for {var}: ")
        values[var] = value
    return values

def load_values_into_environment(values):
    for var, value in values.items():
        os.environ[var] = value

def call_envsubst(input_file, output_file):
    try:
        with open(input_file, 'r') as f_in:
            with open(output_file, 'w') as f_out:
                subprocess.run(['envsubst'], stdin=f_in, stdout=f_out, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Environment substitution failed with error code {e.returncode}.")
        print(e.output)

def main(file_path, prefix):
    # Create the output file path by replacing the extension of the input file with '.env'
    env_filepath="environments-enabled/"
    output_file_path = os.path.join(env_filepath, os.path.splitext(os.path.split(file_path)[1])[0] + '.env')

    # Read variable names from file
    variables = read_variables(file_path, prefix)    
    

    # Check to see if any variables need to be gathered
    #
    # Fix: Commented variables are having empty values assigned during subst.
    #      This is not a major issue, more of something doesn't work quite as 
    #      intended and will bug the crap out of me.
    #
    if (len(variables) > 0):
        # Prompt the user for values for each variable
        values = prompt_user_for_values(variables)
        # Load the values into the environment
        load_values_into_environment(values)
        call_envsubst(file_path, output_file_path)
    else:
        copyfile(file_path, output_file_path)        


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python script.py <file_path> <prefix>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    prefix = sys.argv[2] + "_"
    main(file_path, prefix)
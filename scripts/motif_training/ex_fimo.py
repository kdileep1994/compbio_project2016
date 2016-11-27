"""Script to run fimo on the entire genome/sequences"""

from subprocess import call
from itertools import chain

def run_fimo(meme_path, motif_file, sequence_file, op_folder, options):
    """Run fimo with the given options"""
    command = [meme_path + './fimo']
    others = list(chain(*zip(options.keys(), options.values())))
    command += others
    files = ['--oc', op_folder]
    command += files
    inputs = [motif_file, sequence_file]
    command += inputs
    shell_command = ' '.join(command)
    print(shell_command)
    call(shell_command, shell=True)
    return None

def ex_fimo(meme_path, motif_file, sequence_file, op_folder, thresh=0.0001):
    options = {"--thresh": str(thresh), "--verbosity": str(1)}
    fimo_dir = '/'.join(op_folder.split('/')[:-1])
    call('mkdir '+fimo_dir, shell=True)
    run_fimo(meme_path, motif_file, sequence_file, op_folder, options)

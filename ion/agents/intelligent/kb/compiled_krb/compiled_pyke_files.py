# compiled_pyke_files.py

from pyke import target_pkg

pyke_version = '1.1.1'
compiler_version = 1
target_pkg_version = 1

try:
    loader = __loader__
except NameError:
    loader = None

def get_target_pkg():
    return target_pkg.target_pkg(__name__, __file__, pyke_version, loader, {
         ('ion.agents.intelligent.kb', '', 'useragent.krb'):
           [1318734033.253675, 'useragent_bc.py'],
         ('ion.agents.intelligent.kb', '', 'resourceagent.krb'):
           [1318734033.2626281, 'resourceagent_bc.py'],
         ('ion.agents.intelligent.kb', '', 'useragent_facts.kfb'):
           [1318734033.2649851, 'useragent_facts.fbc'],
         ('ion.agents.intelligent.kb', '', 'resourceagent_facts.kfb'):
           [1318734033.265934, 'resourceagent_facts.fbc'],
        },
        compiler_version)


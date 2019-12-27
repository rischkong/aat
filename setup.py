# # # # GENERATED FILE -- DO NOT MODIFY # # # #
from setuptools import setup, find_packages, Extension
from distutils.version import LooseVersion
from codecs import open
from setuptools.command.build_ext import build_ext
import os
import os.path
import os
import re
import sys
import sysconfig
import platform
import subprocess
try:
    from shutil import which
    CPU_COUNT = os.cpu_count()
except ImportError:
    # Python2
    try:
        from backports.shutil_which import which
    except ImportError:
        which = lambda x: x  # just rely on path
    import multiprocessing
    CPU_COUNT = multiprocessing.cpu_count()

here = os.path.abspath(os.path.dirname(__file__))
PREFIX = sysconfig.get_config_vars()['prefix']

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requires = f.read().split()

if sys.version_info.major < 3 or sys.version_info.minor < 7:
    raise Exception('Must be python3.7 or above')


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        self.cmake_cmd = which('cmake')
        try:
            out = subprocess.check_output([self.cmake_cmd, '--version'])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: " +
                ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)',
                                                   out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension_cmake(ext)

    def build_extension_cmake(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cfg = 'Debug' if self.debug else 'Release'

        cmake_args = [
            '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + os.path.abspath(os.path.join('perspective', 'table')),
            '-DCMAKE_BUILD_TYPE=' + cfg,
            '-DCPP_BUILD_TESTS=0',
            '-DAAT_PYTHON_VERSION={}'.format(platform.python_version()),
            '-DPYTHON_EXECUTABLE={}'.format(sys.executable),
            '-DPython_ROOT_DIR={}'.format(PREFIX),
            '-DPython_ROOT={}'.format(PREFIX),
            '-DPSP_CMAKE_MODULE_PATH={folder}'.format(folder=os.path.join(ext.sourcedir, 'cmake')),
            '-DPSP_CPP_SRC={folder}'.format(folder=ext.sourcedir),
            '-DPSP_PYTHON_SRC={folder}'.format(folder=os.path.join(ext.sourcedir, "..", 'perspective'))
        ]

        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(
                cfg.upper(),
                extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2' if os.environ.get('DOCKER', '') else '-j{}'.format(CPU_COUNT)]

        env = os.environ.copy()
        env['PSP_ENABLE_PYTHON'] = '1'
        env["PYTHONPATH"] = os.path.pathsep.join((os.path.join(os.path.dirname(os.__file__), 'site-packages'), os.path.dirname(os.__file__)))

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call([self.cmake_cmd, os.path.abspath(ext.sourcedir)] + cmake_args, cwd=self.build_temp, env=env, stderr=subprocess.STDOUT)
        subprocess.check_call([self.cmake_cmd, '--build', '.'] + build_args, cwd=self.build_temp, env=env, stderr=subprocess.STDOUT)
        print()  # Add an empty line for cleaner output

setup(
    name='aat',
    version='0.0.2',
    description='Algorithmic trading library',
    long_description=long_description,
    url='https://github.com/timkpaine/aat',
    download_url='https://github.com/timkpaine/aat/archive/v0.0.2.tar.gz',
    author='Tim Paine',
    author_email='timothy.k.paine@gmail.com',
    license='Apache 2.0',
    install_requires=requires,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='algorithmic trading cryptocurrencies',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={'dev': requires + ['pytest', 'pytest-cov', 'pylint', 'flake8', 'mock']},
    entry_points={
        'console_scripts': [
            'aat=aat:main',
        ],
    },
    ext_modules=[CMakeExtension('aat')],
    cmdclass=dict(build_ext=CMakeBuild),
)

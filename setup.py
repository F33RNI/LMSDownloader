"""
 Copyright (C) 2023 Fern Lane, LMSDownloader

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 See the License for the specific language governing permissions and
 limitations under the License.

 IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR
 OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 OTHER DEALINGS IN THE SOFTWARE.
"""
from pathlib import Path

from setuptools import find_packages, setup

setup(
    name="LMSDownloader",
    version="1.1.0",
    license="Apache License 2.0",
    author="Fern Lane (aka F3RNI)",
    author_email="xxoinvizionxx@gmail.com",
    description="Download presentations and lectures from LMS",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/F33RNI/LMSDownloader",
    project_urls={"Bug Report": "https://github.com/F33RNI/LMSDownloader/issues/new"},
    entry_points={
        "console_scripts": [
            "lmsdownloader = LMSDownloader.main:main"
        ],
    },
    install_requires=[
        "Pillow~=10.1.0",
        "pypdf2~=3.0.1",
        "beautifulsoup4~=4.12.2",
        "selenium~=4.14.0",
    ],
    long_description=Path.open(Path("README.md"), encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    py_modules=["LMSDownloader"],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
        "Topic :: Utilities"
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ],
)

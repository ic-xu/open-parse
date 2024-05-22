#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import base64
import json
import os
import re
from io import BytesIO

import fitz
from cachetools import LRUCache, cached
from PIL import Image

PROJECT_BASE = os.getenv("RAG_PROJECT_BASE") or os.getenv("RAG_DEPLOY_BASE")
RAG_BASE = os.getenv("RAG_BASE")


def get_project_base_directory(*args):
    global PROJECT_BASE
    if PROJECT_BASE is None:
        PROJECT_BASE = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                os.pardir,
                os.pardir,
            )
        )

    if args:
        return os.path.join(PROJECT_BASE, *args)
    return PROJECT_BASE


def get_rag_directory(*args):
    global RAG_BASE
    if RAG_BASE is None:
        RAG_BASE = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                os.pardir,
                os.pardir,
                os.pardir,
            )
        )
    if args:
        return os.path.join(RAG_BASE, *args)
    return RAG_BASE


def get_rag_python_directory(*args):
    return get_rag_directory("python", *args)


@cached(cache=LRUCache(maxsize=10))
def load_json_conf(conf_path):
    if os.path.isabs(conf_path):
        json_conf_path = conf_path
    else:
        json_conf_path = os.path.join(get_project_base_directory(), conf_path)
    try:
        with open(json_conf_path) as f:
            return json.load(f)
    except BaseException:
        raise OSError(
            f"loading json file config from '{json_conf_path}' failed!"
        )


def dump_json_conf(config_data, conf_path):
    if os.path.isabs(conf_path):
        json_conf_path = conf_path
    else:
        json_conf_path = os.path.join(get_project_base_directory(), conf_path)
    try:
        with open(json_conf_path, "w") as f:
            json.dump(config_data, f, indent=4)
    except BaseException:
        raise OSError(
            f"loading json file config from '{json_conf_path}' failed!"
        )


def load_json_conf_real_time(conf_path):
    if os.path.isabs(conf_path):
        json_conf_path = conf_path
    else:
        json_conf_path = os.path.join(get_project_base_directory(), conf_path)
    try:
        with open(json_conf_path) as f:
            return json.load(f)
    except BaseException:
        raise OSError(
            f"loading json file config from '{json_conf_path}' failed!"
        )


def rewrite_json_file(filepath, json_data):
    with open(filepath, "w") as f:
        json.dump(json_data, f, indent=4, separators=(",", ": "))
    f.close()


def thumbnail(filename, blob):
    filename = filename.lower()
    if re.match(r".*\.pdf$", filename):
        pdf = fitz.open(stream=blob, filetype="pdf")
        pix = pdf[0].get_pixmap(matrix=fitz.Matrix(0.03, 0.03))
        buffered = BytesIO()
        Image.frombytes("RGB", [pix.width, pix.height],
                        pix.samples).save(buffered, format="png")
        return "data:image/png;base64," + \
            base64.b64encode(buffered.getvalue()).decode("utf-8")

    if re.match(r".*\.(jpg|jpeg|png|tif|gif|icon|ico|webp)$", filename):
        image = Image.open(BytesIO(blob))
        image.thumbnail((30, 30))
        buffered = BytesIO()
        image.save(buffered, format="png")
        return "data:image/png;base64," + \
            base64.b64encode(buffered.getvalue()).decode("utf-8")

    if re.match(r".*\.(ppt|pptx)$", filename):
        import aspose.pydrawing as drawing
        import aspose.slides as slides
        try:
            with slides.Presentation(BytesIO(blob)) as presentation:
                buffered = BytesIO()
                presentation.slides[0].get_thumbnail(0.03, 0.03).save(
                    buffered, drawing.imaging.ImageFormat.png)
                return "data:image/png;base64," + \
                    base64.b64encode(buffered.getvalue()).decode("utf-8")
        except Exception:
            pass


def traversal_files(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname

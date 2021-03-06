#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START vision_document_text_tutorial]
# [START vision_document_text_tutorial_imports]
import argparse
from enum import Enum
import io
import json
import os 
from PIL import Image
from PIL import ImageOps
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw, ImageFont 
from braille import extract, translated
# [END vision_document_text_tutorial_imports]


class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5


def draw_boxes(image, bounds, color):
    """Draw a border around the image using the hints in the vector list."""
    draw = ImageDraw.Draw(image)

    for bound in bounds:
        draw.polygon([
            bound.vertices[0].x, bound.vertices[0].y,
            bound.vertices[1].x, bound.vertices[1].y,
            bound.vertices[2].x, bound.vertices[2].y,
            bound.vertices[3].x, bound.vertices[3].y], color, None) 
    return image


def get_document_bounds(image_file, feature):
    # [START vision_document_text_tutorial_detect_bounds]
    """Returns document bounds given an image."""
    client = vision.ImageAnnotatorClient()

    bounds = []

    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    # Collect specified feature bounds by enumerating all document features
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if (feature == FeatureType.SYMBOL):
                            bounds.append(symbol.bounding_box)

                    if (feature == FeatureType.WORD):
                        bounds.append(word.bounding_box)

                if (feature == FeatureType.PARA):
                    bounds.append(paragraph.bounding_box)

            if (feature == FeatureType.BLOCK):
                bounds.append(block.bounding_box)

        if (feature == FeatureType.PAGE):
            bounds.append(block.bounding_box)

    # The list `bounds` contains the coordinates of the bounding boxes.
    # [END vision_document_text_tutorial_detect_bounds]
    return bounds


def render_doc_text(filein, fileout):
    image = Image.open(filein)
    bounds = get_document_bounds(filein, FeatureType.PAGE)
    draw_boxes(image, bounds, 'white')
    bounds = get_document_bounds(filein, FeatureType.PARA)
    draw_boxes(image, bounds, None)
    bounds = get_document_bounds(filein, FeatureType.WORD)
    draw_boxes(image, bounds, 'white') 
    draw = ImageDraw.Draw(image) 
    
    file1 = open('json.txt', 'r') # Reads in x and y coordinates for placing text
    jname = file1.read()
    
    x_coor = []
    y_coor = []

    with open(jname) as json_file:
        data = json.load(json_file)
        for p in data['textAnnotations']:
            x_coor.append(p['boundingPoly']['vertices'][0]['x'])
            y_coor.append(p['boundingPoly']['vertices'][0]['y'])

    # Font size for braille and translated text from map
    fsize = 18
    for i in range(1, len(translated)):
        draw.text((x_coor[i], y_coor[i]), translated[i],(0,0,0),font=ImageFont.truetype("Swell-Braille.ttf", fsize))
    
    
    #reverses and converts from bmp to svg 
    #im = ImageOps.mirror(image)
    if "jpg" in jname:
        image.save("image.jpg")
    elif "png" in jname:
        image.save("image.png")
    image.show()
    
    """
    ary = np.array(im)
    
    #split 3 channels rgb
    r,g,b = np.splot(ary,3,axis=2)
    r=r.reshape(-1)
    g=r.reshape(-1)
    b=r.reshape(-1)

    #Standard RGB to grayscale
    bitmap = list(map(lambda x: 0.299*x[0]+0.587*x[1]+0.114*x[2], zip(r,g,b)))
    bitmap = np.array(bitmap).reshape([ary.shape[0], ary.shape[1]])
    bitmap = np.dot((bitmap > 128).astype(float),255)
    im = Image.fromarray(bitmap.astype(np.uint8))
    """
    

    if fileout is not 0:
        image.save(fileout) 
    else:
        image.show()
    #os.remove(jname)
if __name__ == '__main__':
    # [START vision_document_text_tutorial_run_application]
    parser = argparse.ArgumentParser()
    parser.add_argument('detect_file', help='The image for text detection.')
    parser.add_argument('-out_file', help='Optional output file', default=0)
    args = parser.parse_args()

    render_doc_text(args.detect_file, args.out_file)
    # [END vision_document_text_tutorial_run_application]
# [END vision_document_text_tutorial]

#!/usr/bin/env python3.7
#
# Description:
#   
#   The utilities here are for convenient creation, updating, and 
#       assignment of material shaders.  These ease the use of materials
#       in scripts, while still handling the idiosyncrasies of materials.
#
#  Typical use: 
#   Creates Maya standard materials for specified objects.   
#   There are handlers to ease scripting of materials tasks like 
#       assigning using random ranges of parameters.
#   There is a utility to script texture testing -- adding textures 
#       to materials and/or creating poly planes of the right ratio to easily
#       view materials in-scene.
#   
# Author:
#   Tony Kaap
#

from __future__ import absolute_import
from __future__ import print_function
import logging
from random import uniform
from math import fmod, sqrt
logger = logging.getLogger(__name__) # name of this script or module
logger.setLevel(logging.WARNING)

import maya.cmds as mc
import maya.mel as mm

def createShader(shaderName="standardSurface1", shaderAttrValues={}, shaderType="standardSurface"):
    """
    Creates a new shader
    
    Params:
        name:   The desired name of the new shader node.  If this name already exists, the standard Maya name conflict rules will be applied
        
        shaderAttrValues: a dict of values to be set into the attrs on the shading node.  These should be in key:value pairs of <attr name>:<attr value>, so that they can be set to any shader type
    
            If any parameter should be a random value, pass in a tuple of (lowValue, highValue).
    
        shaderType: pass in a shader type to override and choose a different shader node
            default: standardSurface
    
    Return:
        A tuple of the shader node and the shadingGroup for this shader.
        shaderNode
        shadingGroupNode
        
    """
    logger_name = "{:s}.{:s}".format(__name__,createShader.__name__)
    logger = logging.getLogger(logger_name) # set the name of the logger to the current function name
    logger.setLevel(logging.WARNING)

    logger.debug("Inside createShader")
    
    shaderNode = mc.shadingNode(shaderType, asShader=1, name=shaderName)
    shadingGroupNode = mc.sets(renderable=1, noSurfaceShader=1, empty=1, name=shaderNode+"SG")
    mc.connectAttr(shaderNode+".outColor", shadingGroupNode+".surfaceShader",f=1)
    
    logger.debug("Done creating material, calling updateShader")
    updateShader(shaderNode,shaderAttrValues)
            
    return (shaderNode, shadingGroupNode)

def updateShader(shaderNode, shaderAttrValues):
    """
    params:
        walk through the shaderAttrValues dict keys and set the values onto the corresponding attrs on the shaderNode
    return:
        nothing
    """
    logger_name = "{:s}.{:s}".format(__name__,updateShader.__name__)
    logger = logging.getLogger(logger_name) # set the name of the logger to the current function name
    logger.setLevel(logging.WARNING)

    logger.debug("Inside updateShader: updating material %s"%shaderNode)
    
    inAttrs = shaderAttrValues.keys()
    for inAttr in inAttrs:
        attrType = mc.getAttr("%s.%s"%(shaderNode,inAttr),type=1)
        logger.debug("attr %s is of type \"float\", value %s, setting"%(inAttr, attrType))
        # set vector values
        if attrType == u"float3":
            values = shaderAttrValues.get(inAttr,(0,0,0))
            mc.setAttr("{:s}.{:s}".format(shaderNode,inAttr), handleValue(values[0]), handleValue(values[1]), handleValue(values[2]) )
            pass
        # set scalar values
        elif attrType == u"float":
            value = handleValue(shaderAttrValues.get(inAttr,0.0))
            mc.setAttr("{:s}.{:s}".format(shaderNode,inAttr), value )
            pass
        else:
            logging.warning("attr %s is of unimplemented type %s, skipping"%(inAttr,attrType))
    

def handleValue(inValue):
    """
    check if in the inValue is a request to replace it with a random value between a lowvalue and high value.  If so, do so.  If inValue is a tuple instead of a scalar, return a uniform random between the 0th and 1st element
    
    return either the inValue or the result of the uniform random.
    
    Possibly extend this to handle other random or range functions
    """
    logger_name = "{:s}.{:s}".format(__name__,handleValue.__name__)
    logger = logging.getLogger(logger_name) # set the name of the logger to the current function name
    logger.setLevel(logging.WARNING)

    if type(inValue) in [tuple,list]:
        logger.debug("random range")
        return uniform(inValue[0],inValue[1])
    else:
        return inValue

def deleteUnusedNodes():
    """Runs the Maya command to Delete Unused Nodes
    This will delete all shading nodes, textures, etc that are not part of a currently-assigned
    shading network.
    """
    mm.eval("hyperShadePanelMenuCommand(\"hyperShadePanel1\", \"deleteUnusedNodes\")")
    
def addToOrCreateShader(shaderName, nodes, shaderAttrValues={}):
    """
    Adds nodes to existing shader.  If a shader by that name does not yet exist, create one using the passed-in shaderAttrValues dict

    If new attribute values are passed in, the shader's values will also be updated.
    """
    logger_name = "{:s}.{:s}".format(__name__,addToOrCreateShader.__name__)
    logger = logging.getLogger(logger_name) # set the name of the logger to the current function name
    logger.setLevel(logging.WARNING)

    logger.debug("Inside addToOrCreateShader")
    
    if not addToShader(shaderName,nodes):
        (shaderName,shadingGroup) = createShader(shaderName=shaderName, shaderAttrValues=shaderAttrValues)
        addToShader(shaderName,nodes)

    updateShader(shaderName,shaderAttrValues)
    return shaderName
    
def createOrUpdateShader(shaderName, shaderAttrValues={}, shaderType="standardSurface"):
    """
    params:
        shaderNode - name of the shader to create or update
        shaderAttrValues - dict of attr values to set into the attrs of the shader node
        shaderType - the desired shader type to create, if needed
    return:
        If a new shader was created, both the shader and the shadingGroup are returned
        If the shader was only updated, only the shader node name is returned
    """
    logger_name = "{:s}.{:s}".format(__name__,createOrUpdateShader.__name__)
    logger = logging.getLogger(logger_name) # set the name of the logger to the current function name
    logger.setLevel(logging.WARNING)

    logger.debug("Inside createOrUpdateShader")
    
    if not mc.objExists(shaderName):
        (shaderNode, shadingGroupNode) = createShader(shaderName=shaderName, shaderAttrValues=shaderAttrValues, shaderType=shaderType)
    else:
        updateShader(shaderName=shaderName, shaderAttrValues=shaderAttrValues)
        shadingGroupNode = None
    return (shaderNode, shadingGroupNode) 
    
    
    
def addToShader(shaderName, nodes=[]):
    """
    Add a node or list of nodes to an existing shader.  Pass the desired shader's name as shaderName
        
    Params:
        shaderName - the string name of the shader that the nodes should be added to
            If shaderName is actually a shadingGroup, this will also succeed
        nodes - the name of a node or a list of names of nodes that should be assigned to this shader
        
    Return:
        True if successful
        False if shader or shadingGroup does not exist 
    """
    logger_name = "{:s}.{:s}".format(__name__,addToShader.__name__)
    logger = logging.getLogger(logger_name) # set the name of the logger to the current function name
    logger.setLevel(logging.WARNING)

    logger.debug("Inside addToShader")
    
    if not mc.objExists(shaderName):
        logger.info("%s does not exist."%shaderName)
        return False

    if not (mc.nodeType(shaderName) == "shadingEngine"):
        shadingGroup = getShadingGroup(shaderName)
    else:
        shadingGroup = shaderName

    if shadingGroup is None:
        logger.warning("Cannot find a shadingGroup for shader %s"%shaderName)
        return False

    if mc.objExists(shadingGroup):
        logger.debug("Adding %s to SG: %s"%(nodes, shadingGroup))
        mc.sets(nodes,e=1,fe=shadingGroup)
    
    return True
    
def getShadingGroup(shader):
    """
    Finding the shadingGroup of a shader is not intuitive.  This utility handles the
    process.
    
    Parmas:
        The sting name of the shader node
        
    Return:
        The string name of the shadingGroup, if one exists.  Otherwise, return Nones
    """
    logger_name = "{:s}.{:s}".format(__name__,getShadingGroup.__name__)
    logger = logging.getLogger(logger_name) # set the name of the logger to the current function name
    logger.setLevel(logging.WARNING)

    if mc.objExists(shader+".outColor"):
        c = mc.listConnections(shader+".outColor")
    elif mc.objExists(shader+".outValue"):
        c = mc.listConnections(shader+".outValue")
    elif mc.objExists(shader+".message"):
        c = mc.listConnections(shader+".message")
    for sg in c:
        if sg[-2:] != "SE":
            break
    return sg

def getShaderForObj(obj):
    """
        returns the string name of the surface shader for the shading group that this object is assigned to.
    """
    logger_name = "{:s}.{:s}".format(__name__,getShaderForObj.__name__)
    logger = logging.getLogger(logger_name) # set the name of the logger to the current function name
    logger.setLevel(logging.WARNING)
    
    shape = mc.listRelatives(obj,s=1)[0]
    SGs = mc.listConnections(shape, type='shadingEngine')
    if SGs == None:
        return None
    shadingGroup = SGs[0]
    materials =  mc.listConnections(shadingGroup+'.surfaceShader', source=1)     
    if materials == None:
        return None
    return materials[0]        


def generateColor(index, modulateV=False, S=0.5, V=1.0):
    """ If not also modulating V, use the V argument   
    http://gamedev.stackexchange.com/questions/46463/is-there-an-optimum-set-of-colors-for-10-players/46587
    """
    logger_name = "{:s}.{:s}".format(__name__,generateColor.__name__)
    logger = logging.getLogger(logger_name) # set the name of the logger to the current function name
    logger.setLevel(logging.WARNING)
    
    if modulateV:
        return (fmod(index * 0.618033988749895, 1.0),
            S,
            sqrt(1.0 - fmod(index * 0.618033988749895, 0.5)));
    else:
        return (fmod(index * 0.618033988749895, 1.0),
            S,
            V)

def createPlaneForTexturePath(path, name=None):
    """
    Given a file path to an image file, creates a polyPlane geometry with the right aspect ratio to 
    fit the file texture, create a material, and a file node, and connect the file texture to the shader
    
    This is a good way to exercise createPlaneForFileNode and createFileTextureNodeForShader
    """
    logger_name = "{:s}.{:s}".format(__name__,createPlaneForTexturePath.__name__)
    logger = logging.getLogger(logger_name) # set the name of the logger to the current function name
    logger.setLevel(logging.INFO)
    
    if not (os.path.exists(path)):
        path = path.replace('\\','/') # try swapping the path delimiters
        if not (os.path.exists(path)):
            logger.error("Error: file not found: %s, exiting",path)
            raise IOError
            return
    shader_type = 'arnold'
    (shader,sg) = createMaterial(path.split(os.sep)[-1]+"_mat",type=shader_type)
    (fileNode, placementNode) = createFileTextureNodeForShader(shader=shader, fullFilePath=path, type=shader_type, name=shader+"_file_tex")
    createPlaneForFileNode(fileNode, sg, name=name)

def createPlaneForFileNode(fileNode,shading_group,name=None, scalingFactor=10.0):
    """
    Given a File node, creates a polyPlane geometry with the right aspect ratio to 
    fit the file texture, and assigns that geometry to the shading group
    """
    
    logger_name = "{:s}.{:s}".format(__name__,createPlaneForFileNode.__name__)
    logger = logging.getLogger(logger_name) # set the name of the logger to the current function name
    logger.setLevel(logging.INFO)
    
    wPixels = mc.getAttr(fileNode+".osx") / scalingFactor
    hPixels = mc.getAttr(fileNode+".osy") / scalingFactor
    if name:
        polyNode = mc.polyPlane(w=wPixels, h=hPixels, sx=1, sy=1,name=name)[0]
    else:
        polyNode = mc.polyPlane(w=wPixels, h=hPixels, sx=1, sy=1)[0]
  
    # lambertNode = mc.shadingNode("lambert", asShader=1)
    # mc.connectAttr(fileNode+".outColor", lambertNode+".color")
    # sgNode = mc.sets(renderable=1, noSurfaceShader=1, empty=1, name=lambertNode+"SG")
    # mc.connectAttr(lambertNode+".color", sgNode+".surfaceShader",f=1)
    mc.sets(polyNode, e=1, fe=shading_group)


def createFileTextureNodeForShader(shader, fullFilePath='', type=None, name=None):
    """
    Utility to create a fileTexture node, and use it to drive the shader
    returns name of (fileNode, place2dTexture)
    """
    
    logger_name = "{:s}.{:s}".format(__name__,createFileTextureNodeForShader.__name__)
    logger = logging.getLogger(logger_name) # set the name of the logger to the current function name
    logger.setLevel(logging.WARNING)
    
    # create file texture
    if not name == None:
        fileNode = mc.shadingNode('file', asTexture=1, name=name)
    else:
        fileNode = mc.shadingNode('file', asTexture=1)

    # create 2D placement
    placementNode = mc.shadingNode('place2dTexture', asUtility=1)

    # connect up the placement to the file texture node
    mc.connectAttr(placementNode+'.coverage', fileNode+'.coverage', f=1)
    mc.connectAttr(placementNode+'.translateFrame', fileNode+'.translateFrame', f=1)
    mc.connectAttr(placementNode+'.rotateFrame', fileNode+'.rotateFrame', f=1)
    mc.connectAttr(placementNode+'.mirrorU', fileNode+'.mirrorU', f=1)
    mc.connectAttr(placementNode+'.mirrorV', fileNode+'.mirrorV', f=1)
    mc.connectAttr(placementNode+'.stagger', fileNode+'.stagger', f=1)
    mc.connectAttr(placementNode+'.wrapU', fileNode+'.wrapU', f=1)
    mc.connectAttr(placementNode+'.wrapV', fileNode+'.wrapV', f=1)
    mc.connectAttr(placementNode+'.repeatUV', fileNode+'.repeatUV', f=1)
    mc.connectAttr(placementNode+'.offset', fileNode+'.offset', f=1)
    mc.connectAttr(placementNode+'.rotateUV', fileNode+'.rotateUV', f=1)
    mc.connectAttr(placementNode+'.noiseUV', fileNode+'.noiseUV', f=1)
    mc.connectAttr(placementNode+'.vertexUvOne', fileNode+'.vertexUvOne', f=1)
    mc.connectAttr(placementNode+'.vertexUvTwo', fileNode+'.vertexUvTwo', f=1)
    mc.connectAttr(placementNode+'.vertexUvThree', fileNode+'.vertexUvThree', f=1)
    mc.connectAttr(placementNode+'.vertexCameraOne', fileNode+'.vertexCameraOne', f=1)
    mc.connectAttr(placementNode+'.outUV', fileNode+'.uv', f=1)
    mc.connectAttr(placementNode+'.outUvFilterSize', fileNode+'.uvFilterSize', f=1)
    
    if type is None:
        type = mc.nodeType(shader)
        logger.debug("setting type to %s" % type)
    if type in ('standardSurface'):
        logger.debug("processing standardSurface")
        mc.connectAttr(fileNode+'.outColor', shader+'.baseColor', force=1)
        mc.connectAttr(fileNode+'.outAlpha', shader+'.transmission', force=1)
    elif type in ('mia', 'mia_material'):
        mc.connectAttr(fileNode+'.outColor', shader+'.diffuse', force=1)
        mc.connectAttr(fileNode+'.outAlpha', shader+'.diffuseA', force=1)
    elif type in ('arnold', 'arnoldStd'):
        mc.connectAttr(fileNode+'.outColor', shader+'.baseColor', force=1)
    else: # blinn, vraymtl
        mc.connectAttr(fileNode+'.outColor', shader+'.color', force=1)
    
    # set the file texture name to the file node.
    mc.setAttr(fileNode+'.fileTextureName', fullFilePath, type="string")
    
    return (fileNode, placementNode)





























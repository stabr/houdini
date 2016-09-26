import hou, os

outpath = ''

def getObjByType(h_type):
    return [g for g in fbx.allSubChildren() if g.type().name() == h_type]

obj = hou.node('/obj')
#get fbx node
fbx = [f for f in obj.children() if 'fbx' in f.name().lower()]
if len(fbx)>0:
    fbx = fbx[-1]

# get fbx content
fbx_geo = getObjByType('geo')
fbx_cam = getObjByType('cam')
fbx_mat = getObjByType('shopnet')

# create combine node win fbx content
cmb = obj.createNode('geo',
                    node_name = 'combine',
                    run_init_scripts = False)
# crete merge node
mrg = cmb.createNode('merge')
for g in fbx_geo:
    #print 'create.. %s' % g.name()
    fl = [f for f in g.children() if f.type().name() == 'file'][0]
    
    om = cmb.createNode('object_merge',
                        node_name = g.name())
    om.parm('objpath1').set('/obj/%s/%s/%s' % (fbx.name(), g.name(), fl.name()))
    om.parm('xformtype').set(1)
    om.moveToGoodPosition()
    gr = om.createOutputNode('group',
                        node_name = om.name()+'_gr')
    gr.parm('crname').set(om.name())
    gr.moveToGoodPosition()
    
    chl = [f for f in g.children() if f.type().name() in ['group','material']]
    if len(chl)>0:
        copi = hou.copyNodesTo(chl, cmb)
        for c in copi:
            c.moveToGoodPosition()
        copi[0].setFirstInput(gr)
        mrg.setNextInput(copi[-1])
        mat = [o for o in copi if o.type().name() == 'material']
        if len(mat)>0:
            #print mat.relativePathTo()
            for m in range(mat[0].evalParm('num_materials')):
                pth = mat[0].evalParm('shop_materialpath%d'%(m+1))[3:]
                mat[0].parm('shop_materialpath%d'%(m+1)).set(pth)
    else:
        mrg.setNextInput(gr)
    outpath = os.path.dirname(fl.evalParm('file'))
mrg.moveToGoodPosition()
# copy camera
hou.copyNodesTo(fbx_cam, obj)
# copy materials
cmb_mat = cmb.createNode('shopnet', node_name = 'materials')
cmb_mat.moveToGoodPosition()
mts = fbx_mat[0].children()
hou.copyNodesTo(fbx_mat[0].children(), cmb_mat)
#create output
outpath += '/fbx_geo.bgeo'
rop = mrg.createOutputNode('rop_geometry')
rop.moveToGoodPosition()
rop.parm('sopoutput').set(outpath)
rop.render()

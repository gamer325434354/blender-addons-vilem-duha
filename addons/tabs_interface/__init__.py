
bl_info = {
    "name": "Tabs interface",
    "author": "Vilem Duha",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "Everywhere(almost)",
    "description": "Blender tabbed.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "All"}

import bpy,os, math, string, random, time

import bpy, bpy_types
from bpy.app.handlers import persistent
from tabs_interface.panel_order import spaces
from tabs_interface import panel_order , fixes

_hidden_panels = {}
_panels = {}
_context_items = []
_bl_panel_types = []

_tab_panels = {}
_update_tabs = []
_update_categories = []

@classmethod
def noPoll(cls, context):
    return False
@classmethod
def yesPoll(cls, context):
    return True

@classmethod
def smartPoll(cls, context):
    prefs = bpy.context.user_preferences.addons["tabs_interface"].preferences
    polled = cls.opoll(context)
    item = bpy.context.scene.panelData.get(cls.realID)
    
    return (item.activated or item.pin) and polled and item.show and prefs.original_panels
    
def drawHeaderPin(cls, context):
    layout = cls.layout
    #r = layout.row()
    pd = bpy.context.scene.panelData[cls.realID]
    if pd.pin: icon = 'PINNED'
    else: icon = 'UNPINNED'
    layout.prop(bpy.context.scene.panelData[cls.realID],'pin' , icon_only = True, icon=icon, emboss = False)
    if hasattr(cls, 'orig_draw_header'):
        cls.orig_draw_header(context)
    #else:
    #    layout.label(cls.bl_label)
    

def hide_panel(tp_name):
    
    if tp_name in _hidden_panels:
        pass

    elif hasattr(bpy.types, tp_name):
        tp = getattr(bpy.types, tp_name)
        
       
        if not hasattr(tp,'opoll'):
            if not hasattr(tp,'poll'):
                tp.poll = yesPoll
            tp.opoll = tp.poll 
            tp.poll = smartPoll
        if hasattr(tp, 'draw_header'):
            tp.orig_draw_header = tp.draw_header
        tp.draw_header = drawHeaderPin
        
        if hasattr(tp,'bl_options'):
            if 'DEFAULT_CLOSED' in tp.bl_options:
                tp.bl_options.remove('DEFAULT_CLOSED')
        bpy.utils.unregister_class(tp)
        _hidden_panels[tp_name] = tp
        bpy.utils.register_class(tp)
        
            
def unhide_panel(tp_name):
    if tp_name in _hidden_panels:
        tp = getattr(bpy.types, tp_name)
        bpy.utils.unregister_class(tp)
        if hasattr(tp,'opoll'):
            tp.poll = tp.opoll
            del tp.opoll
        
        bpy.utils.register_class(tp)
        del _hidden_panels[tp_name]

    else:
        pass

DEFAULT_PANEL_PROPS = ['__class__', '__contains__', '__delattr__', '__delitem__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '__weakref__', '_dyn_ui_initialize', 'append', 'as_pointer', 'bl_category', 'bl_context', 'bl_description', 'bl_idname', 'bl_label', 'bl_options', 'bl_region_type', 'bl_rna', 'bl_space_type', 'COMPAT_ENGINES', 'draw','draw_header', 'driver_add', 'driver_remove', 'get', 'id_data', 'is_property_hidden', 'is_property_readonly', 'is_property_set', 'items', 'keyframe_delete', 'keyframe_insert', 'keys', 'orig_category', 'path_from_id', 'path_resolve', 'poll', 'opoll', 'prepend', 'property_unset', 'remove', 'type_recast', 'values']

NOCOPY_PANEL_PROPS = ['__class__', '__contains__', '__delattr__', '__delitem__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '__weakref__', '_dyn_ui_initialize', 'append', 'as_pointer', 'bl_category', 'bl_context', 'bl_description', 'bl_idname', 'bl_label', 'bl_options', 'bl_region_type', 'bl_rna', 'bl_space_type', 'COMPAT_ENGINES',  'driver_add', 'driver_remove', 'get', 'id_data', 'is_property_hidden', 'is_property_readonly', 'is_property_set', 'items', 'keyframe_delete', 'keyframe_insert', 'keys',  'orig_category', 'path_from_id', 'path_resolve', 'poll', 'prepend', 'property_unset', 'remove', 'type_recast', 'values']

   
def updatePin(self, context) :
    pname = self.name
    s = bpy.context.scene
    if self.pin:
        if pname not in s.pinned_panels:
            litem = s.pinned_panels.add()
            litem.name = s.panelData[pname].name
            litem.space = s.panelData[pname].space
    elif pname in s.pinned_panels:
        s.pinned_panels.remove(s.pinned_panels.find(pname))
       


class tabSetups(bpy.types.PropertyGroup):
    '''stores data for tabs'''
    tabsenum = bpy.props.EnumProperty(name='Post processor',
        items=[('tabID', 'tabb', 'tabbiiiieeee')])
    active_tab = bpy.props.StringProperty(name="Active tab", default="Machine")
    active_category = bpy.props.StringProperty(name="Active category", default="Machine")
           
class tabCategoryData(bpy.types.PropertyGroup):
    #''stores data for categories''
    
    #id = bpy.props.StringProperty(name="panel id", default="")
    #pin = bpy.props.BoolProperty(name="pin", default=False, update = updatePin)
    show = bpy.props.BoolProperty(name="show", default=True)#, update = updatePin)
    #space = bpy.props.StringProperty(name="space", default="Machine")

            
            
class panelData(bpy.types.PropertyGroup):
    '''stores data for panels'''
    
    #id = bpy.props.StringProperty(name="panel id", default="")
    pin = bpy.props.BoolProperty(name="pin", default=False, update = updatePin)
    show = bpy.props.BoolProperty(name="show", default=True)#, update = updatePin)
    activated = bpy.props.BoolProperty(name="activated", default=False)#, update = updatePin)
    space = bpy.props.StringProperty(name="space", default="Machine")
    region = bpy.props.StringProperty(name="region", default="Machine")
 

    
def getlabel(panel):
    return panel.bl_label

DONT_USE = [ 'DATA_PT_modifiers', 'OBJECT_PT_constraints', 'BONE_PT_constraints']   
def getPanelIDs():
    s = bpy.types.Scene
    if not hasattr(s, 'panelIDs'):
        s.panelIDs = {}
   
    newIDs = []
    panel_tp = bpy.types.Panel
    typedir = dir(bpy.types)
    btypeslen = len(typedir)
    
    for tp_name in typedir:
        if tp_name.find('_tabs')==-1  or tp_name not in DONT_USE: #and tp_name.find('NODE_PT_category_')==-1
            tp = getattr(bpy.types, tp_name)
            #print(tp)
            if tp == panel_tp or not issubclass(tp, panel_tp):
                continue
                
            #if (hasattr(tp, 'bl_options') and 'HIDE_HEADER' in tp.bl_options):
                #print(tp.bl_rna.identifier)
            if not (hasattr(tp, 'bl_options') and 'HIDE_HEADER' in tp.bl_options):
                if s.panelIDs.get(tp.bl_rna.identifier) == None:
                        newIDs.append(tp)
                s.panelIDs[tp.bl_rna.identifier] = tp
                if tp.is_registered!=True:
                    print('not registered', tp.bl_label)
                
                            
    #print(tp)  
    
    return newIDs
   
class myPanel:
    pass
    
'''
DATA_PT_modifiers.draw = modifiersDraw
    bpy.types.OBJECT_PT_constraints.draw = constraintsDraw
    bpy.types.BONE_PT_constraints.draw = 
'''

def processPanelForTabs(panel):
    if not hasattr(panel, 'realID' ):
        panel.realID = panel.bl_rna.identifier
        if hasattr(panel, 'bl_category'):
            #if panel.bl_category == 'Archimesh':
                #print ('ARCHISHIT')
            if not hasattr(panel, 'orig_category'):
                panel.orig_category = panel.bl_category
            panel.bl_category = 'Tools'
        hide_panel(panel.realID)
        
def buildTabDir(panels):
    print('rebuild tabs ', len(panels))
   
    if hasattr(bpy.types.Scene, 'panelSpaces'):
        spaces =  bpy.types.Scene.panelSpaces
    else:
        spaces = panel_order.spaces
        for sname in spaces:
            space = spaces[sname]
            
            for rname in space:
                nregion = []
                region = space[rname]
                
                for p in region:
                    try:
                        panel = eval( 'bpy_types.bpy_types.'+p)
                        #print(panel)
                        #print(panel)
                        
                        processPanelForTabs(panel)
                        
                        nregion.append(panel)
                        
                    except:
                        print('non existing panel ' + p)
                #if rname =='UI' and sname == 'VIEW_3D':
                    #print(region)   
                space[rname] = nregion
                #print(space[rname])
        
        
    
    #print('called buildtabdir')
    for panel in panels:
        if hasattr(panel, 'bl_space_type'):
            st = panel.bl_space_type
            if st!= 'USER_PREFERENCES':
                #print((st))
                #toz a je to vyreseny - ten panel se asi
                if panel.bl_label == 'Collision':
                    print('collision in tabdir')
                if spaces.get(st) == None:
                    spaces[st] = {}#[panel]
                
                if hasattr(panel, 'bl_region_type'):
                    rt = panel.bl_region_type
                    #print(rt)
                    if spaces[st].get(rt)==None:
                        spaces[st][rt] = []
                
               
                    
                    if panel not in spaces[st][rt]:
                        spaces[st][rt].append(panel)
                        #print(panel)
                        processPanelForTabs(panel)
                        if panel.bl_label == 'Collision':
                            print('collision assign in tabdir')
    return spaces 

def updatePanels():    
        newIDs = getPanelIDs() #bpy.types.Scene.panels = 
        bpy.types.Scene.panelSpaces = buildTabDir(newIDs)
        createSceneTabData()
        #print(getPanels)
        #print(newIDs)
def getPanels(getspace, getregion):
    if not hasattr(bpy.types.Scene, 'panelIDs'):
        updatePanels()
    panels = bpy.types.Scene.panelSpaces[getspace][getregion]
    #print(getspace,getregion,len(panels))
    return panels
        
def drawEnable(self,context):
    layout = self.layout
    row = layout.row()
    row.label('Enable:')
    
def layoutActive(self,context):
    layout = self.layout
    layout.active = True
    layout.enabled = True
    #layout.label('\n\n\n\n\n\n\n\n\n')
    #for a in range(0,90):
    #    r = layout.separator()
        
def layoutSeparator(self,context):
    layout = self.layout
    layout.separator()
    
class CarryLayout:
    def __init__(self, layout):
        self.layout = layout

def drawNone(self,context):
    pass;

def tabRow(layout):
    prefs = bpy.context.user_preferences.addons["tabs_interface"].preferences
    row = layout.row(align = prefs.fixed_width)# not prefs.fixed_width)
    if not prefs.fixed_width:
        row.scale_y=prefs.scale_y
    if not prefs.fixed_width:
        row.alignment = 'LEFT'
    return row
    
def drawTabsLayout(layout, context, operator_name = 'wm.activate_panel', texts = [], ids = [], tdata = [],  active = '', enable_hiding = False): #tdata=[],
    '''Creates and draws actual layout of tabs'''
    prefs = bpy.context.user_preferences.addons["tabs_interface"].preferences
    w = context.region.width
    margin = 20 
    if prefs.box:
        margin +=5
    iconwidth = 25
    oplist = []
    if prefs.box:
        layout = layout.box()
    layout = layout.column(align = True)
    #layout.prop(prefs,'hiding' , icon_only = True, icon='RESTRICT_VIEW_OFF') 
    '''
    if icons == []:
        for t in texts:
            icons.append('NONE')
    '''
    if not prefs.fixed_width:# variable width layout <3
        baserest = w - margin
        restspace = baserest
        
        tw = 0
        splitalign = True
        row = tabRow(layout)
        split=row
        rows = 0
        i=0
        for t,id in zip(texts,ids):
            last_tw = tw
            if prefs.emboss and restspace != baserest: 
                drawtext = '| ' +t
            else:
                drawtext = t
            tw = getApproximateFontStringWidth(drawtext)
            if enable_hiding and prefs.hiding: tw += iconwidth
            #print(context.space_data.type)
            #print(context.region.type)
            #print(dir(context))
            if context.space_data.type == 'VIEW_3D' and context.region.type == 'TOOLS':#TOOLBAR draws differnt buttons...
                tw += 10
            
            oldrestspace = restspace
            restspace = restspace - tw
            if restspace>0:
                
                split = split.split(tw/oldrestspace, align = splitalign)
                
            else:
                drawtext = t
                tw = getApproximateFontStringWidth(drawtext) 
                if rows ==0 and enable_hiding: #draw hiding mode icon here
                    if oldrestspace>iconwidth:
                        split = split.split((oldrestspace - iconwidth)/oldrestspace, align = False)
                        #split = split.split()
                    if prefs.hiding:
                        icon = 'RESTRICT_VIEW_ON'
                    else:
                        icon = 'RESTRICT_VIEW_OFF'
                    row.prop(prefs,'hiding' , icon_only = True, icon=icon, emboss = not prefs.emboss)
                    if prefs.hiding:
                        tw += iconwidth
                if context.space_data.type == 'VIEW_3D' and context.region.type == 'TOOLS':#TOOLBAR draws differnt buttons...
                    tw += 10 #  tw +=15
                rows+=1
                oldrestspace = baserest
                restspace = baserest- tw
                row = tabRow(layout)
                split = row.split(tw/oldrestspace, align = splitalign)
            
            if enable_hiding and prefs.hiding:
                split.prop(tdata[i], 'show', text = drawtext)
                oplist.append(None)
            else:
            
                if active[i]:
                    op = split.operator(operator_name, text=drawtext , emboss = prefs.emboss)
                else:
                    op = split.operator(operator_name, text=drawtext , emboss = not prefs.emboss)
                oplist.append(op)
            i+=1    
            #
    else:# GRID  layout
        wtabcount = math.floor(w/80)
        if wtabcount == 0:
            wtabcount = 1
        if prefs.fixed_columns:
            
            space = context.area.type
            
            if space == 'PROPERTIES':
                wtabcount = prefs.columns_properties
            else:
                wtabcount = prefs.columns_rest
        ti = 0
        rows = 0
        row=tabRow(layout)
        #split = row.split(0.9, align=True)
        
        #row = split
        #hiding
        
        
        i=0
        for t,id in zip(texts,ids):
            if (enable_hiding and prefs.hiding) or (not enable_hiding or tdata[i].show):
                splitratio = 1/(wtabcount-ti)
                if splitratio == 1 and rows == 0:
                    splitratio =  (1-(wtabcount * (iconwidth/((w-margin)))))
                if splitratio ==1:
                    split = row
                else:
                    split = row.split(splitratio, align = True)
                drawn = False
                if enable_hiding and prefs.hiding:
                    split.prop(tdata[i], 'show', text = t)
                    drawn = True
                else:
                    if not enable_hiding or tdata[i].show:
                    
                        if active[i]:
                            op = split.operator(operator_name, text=t , icon = 'NONE', emboss = prefs.emboss)
                        else:
                            op = split.operator(operator_name, text=t , icon = 'NONE', emboss = not prefs.emboss)
                        oplist.append(op)
                        drawn = True
                if splitratio != 1:
                    row = split.split(align = True)
                ti+=1
            else:
                oplist.append(None)
            i+=1
            if ti == wtabcount:
                ti = 0
                if enable_hiding and rows == 0:
                        #print('hide;')
                        #split = split.split(splitratio, align = True)
                        #split = split.split(align = True)
                        if prefs.hiding:
                            icon = 'RESTRICT_VIEW_ON'
                        else:
                            icon = 'RESTRICT_VIEW_OFF'
                        row.prop(prefs,'hiding' , icon_only = True, icon=icon , emboss = not prefs.emboss)
                rows+=1
                row=tabRow(layout)
            
        if ti!=0:
            while ti<wtabcount:
                row.label('')
                ti+=1
    return oplist
       
       
def drawUpDown(self, context, tabID):
    layout = self.layout
    s = bpy.context.scene
    #r = bpy.context.region
    tabpanel_data = s.panelTabData.get(tabID)
    active_tab = tabpanel_data.active_tab
    op = layout.operator("wm.panel_up", text = 'up' , emboss = True )
    op.panel_id=active_tab
    op.tabpanel_id=tabID
    op = layout.operator("wm.panel_down", text = 'down' , emboss = True )
    op.panel_id=active_tab
    op.tabpanel_id=tabID
 
def getApproximateFontStringWidth(st):
    size = 10
    for s in st:
        if s in 'i|': size+=2
        elif s in ' ': size+=4
        elif s in 'sfrt': size+=5
        elif s in 'ceghkou': size+=6
        elif s in 'PadnBCST3E': size+=7
        elif s in 'GMODVXYZ': size+=8
        elif s in 'w': size+=9
        elif s in 'm': size+=10
        else: size += 7
    #print(size)
    return size# Convert to picas 
 
def mySeparator(layout):
    prefs = bpy.context.user_preferences.addons["tabs_interface"].preferences
    
    if not prefs.box:
        layout.separator()
    if prefs.emboss and not prefs.box:
        b=layout.box()
        b.scale_y=0
 
def drawTabs(self,context,plist, tabID):
    space = context.space_data.type
    prefs = bpy.context.user_preferences.addons["tabs_interface"].preferences
    s = bpy.context.scene
    #r = bpy.context.region
    tabpanel_data = s.panelTabData.get(tabID)
    panel_data = s.panelData
    if tabpanel_data == None:
        _update_tabs.append(self)
        return []
        
    if prefs.reorder_panels:
        drawUpDown(self, context, tabID)
    emboss = prefs.emboss
    
    #print('au')
    draw_panels = []    
    categories={}
    categories_list = []#this because it can be sorted, not like dict.
   
    active_tab = tabpanel_data.active_tab
    active_category = tabpanel_data.active_category
    hasactivetab = False
    hasactivecategory = False
    
   # print('wau')
    for pdata in s.pinned_panels:
        #attempt to pin panel in property window, doesn't work :( due to context issues, e.g. transform locks panel was screwed.
        #if pdata.space == getspace == 'PROPERTIES':
        #   draw_panels.append(eval('bpy.types.' + pdata.name))
        #else:
        #pinning
        for p in plist:#this could be smartsr, avoid for loop?
            if p.realID == pdata.name:
                draw_panels.append(p)
                
    for pdata in s.activated_panels:
        for p in plist:#this could be smartsr, avoid for loop?
            if p.realID == pdata.name and p not in draw_panels:
                draw_panels.append(p)
                
    for p in plist:
        if hasattr(p,'bl_category'):
            if categories.get(p.orig_category) == None:
                categories[p.orig_category] = [p]
                categories_list.append(p.orig_category)
            else:
                categories[p.orig_category].append(p)
        if  tabpanel_data.active_tab == p.realID:
            hasactivetab = True
            
   
        
    if len(categories)>0:
        #print('hascategories')
        catorder = panel_order.categories
        
        sorted_categories=[]
        cdata = []
        for c1 in catorder:
            for c in categories:
                if c==c1:
                    sorted_categories.append(c)
                    cdata.append(s.categories[c])
        for c in categories:
            if c not in sorted_categories:
                sorted_categories.append(c)
                cdata.append(s.categories[c])
        for c in categories:
            if c == active_category:
                hasactivecategory = True
            
        if not hasactivecategory:
            
            active_category = sorted_categories[0]
        active = []
        for cname in sorted_categories:
            if cname == active_category:
                active.append(True)
            else:
                active.append(False)
    
    
    
    preview= None
    layout = self.layout
    maincol = layout.column(align = True)
    
    
    if len(categories)>0: #EVIL TOOL PANELS!       
        #row=tabRow(maincol)
        
        catops = drawTabsLayout(maincol, context, operator_name = 'wm.activate_category', texts = sorted_categories, ids = sorted_categories, tdata = cdata,  active = active, enable_hiding = True)
        for cat, cname  in zip(catops, sorted_categories):
            if cat!=None:
                cplist = categories[cname]
                cat.category=cname
                cat.tabpanel_id=tabID
                #print('catlen ',cname , len(cplist), cplist)
                if len(cplist) == 1:
                    cat.single_panel = cplist[0].realID
           
        plist = categories[active_category]
        if len(plist)>1:
            mySeparator(maincol)
        
        
        category_active_tab = tabpanel_data.get('active_tab_'+active_category)
        if category_active_tab != None:
            active_tab = category_active_tab
            hasactivetab = True
    
    if not hasactivetab and len(plist)>0:
        activetab = plist[0].realID
    #print('categories' , categories)  
   
    if len(plist)>1:#property windows
        texts = []
        ids=[]
        tdata = []
        tabpanels = []
        
        #row=tabRow(maincol)
        active = []
        for p in plist:
            if p.bl_label == 'Preview':
                preview = p
            else:
                #if p.realID == active_tab and p.realID not in s.pinned_panels:
                 #   draw_panels.append(p)
                texts.append(p.bl_label)
                ids.append(p.realID)
                tabpanels.append(p)
                tdata.append(panel_data[p.realID])
                active.append(panel_data[p.realID].activated)
        #print(texts)       
        tabops = drawTabsLayout(maincol, context, operator_name ='wm.activate_panel', texts = texts, ids = ids, tdata = tdata, active = active, enable_hiding = True)   
        for op,p in zip(tabops, tabpanels):
            if op!=None:
                op.panel_id=p.realID
                op.tabpanel_id=tabID
                op.category=active_category
    elif len(plist)==1:
        p = plist[0]
        #print(p.bl_label)
        #if hasattr(p,'category'):# Node editor
        #    self.category = p.category
        if p not in draw_panels:
            draw_panels.append(p)
    #print(plist)
    layout.active = True
    if preview != None:
        preview.draw(self, context)
    return draw_panels


def modifiersDraw(self, context):
    ob = context.object
    layout = self.layout
    layout.operator_menu_enum("object.modifier_add", "type")
    if len(ob.modifiers)>0:
        maincol = layout.column(align = True)
        
        active_modifier = ob.active_modifier
        if not ob.active_modifier in ob.modifiers:
            active_modifier = ob.modifiers[0].name
        if len(ob.modifiers)>1:
            names = ob.modifiers.keys()
            active = []
            for m in ob.modifiers:
                if m.name == active_modifier:
                    active.append(True)
                else:
                    active.append(False)
            tabops= drawTabsLayout(maincol, context,  operator_name = 'object.activate_modifier', texts = names, ids = names, active = active)   
            for op, mname in zip(tabops,names):
                op.modifier_name = mname
                
            mySeparator(maincol)
        md = ob.modifiers[active_modifier]
        box = layout.template_modifier(md)
        if box:
            # match enum type to our functions, avoids a lookup table.
            getattr(self, md.type)(box, ob, md)

            
def constraintsDraw(self, context):

    ob = context.object

    layout = self.layout
    if ob.type == 'ARMATURE' and ob.mode == 'POSE':
        box = layout.box()
        box.alert = True  # XXX: this should apply to the box background
        box.label(icon='INFO', text="Constraints for active bone do not live here")
        box.operator("wm.properties_context_change", icon='CONSTRAINT_BONE',
                     text="Go to Bone Constraints tab...").context = 'BONE_CONSTRAINT'
    else:
        layout.operator_menu_enum("object.constraint_add", "type", text="Add Object Constraint")
    if len(ob.constraints)>0:
        maincol = layout.column(align = True)
        
        active_constraint = ob.active_constraint
        if not ob.active_constraint in ob.constraints:
            active_constraint = ob.constraints[0].name
            
        active = []
        for c in ob.constraints:
            if c.name == active_constraint:
                active.append(True)
            else:
                active.append(False)
                
        if len(ob.constraints)>1:
            names = ob.constraints.keys()  
            tabops= drawTabsLayout(maincol, context,  operator_name = 'object.activate_constraint', texts = names, ids = names, active = active)  
            for op, cname in zip(tabops, names):   
                op.constraint_name = cname
        con = ob.constraints[active_constraint]
        self.draw_constraint(context, con)    
       
      
def boneConstraintsDraw(self, context):
    pb = context.pose_bone
    layout = self.layout
    layout.operator_menu_enum("pose.constraint_add", "type", text="Add Bone Constraint")
    

    if len(pb.constraints)>0:
        maincol = layout.column(align = True)
        active_constraint = pb.active_constraint
        if not pb.active_constraint in pb.constraints:
            active_constraint = pb.constraints[0].name
        if len(pb.constraints)>1:
            maincol = layout.column(align = True)
        
            active_constraint = pb.active_constraint
            if not pb.active_constraint in pb.constraints:
                active_constraint = pb.constraints[0].name
                
            active = []
            for c in pb.constraints:
                if c.name == active_constraint:
                    active.append(True)
                else:
                    active.append(False)
                    
            if len(pb.constraints)>1:
                names = pb.constraints.keys()
                #tabops= drawTabsLayout(maincol, context,  operator_name = 'object.activate_constraint', texts = names, ids = names, active = active_constraint)  
                tabops= drawTabsLayout(maincol, context,  operator_name = 'object.activate_posebone_constraint',texts =  names,ids =  names,active =  active)  
                for op, cname in zip(tabops, names):   
                    op.constraint_name = cname
        con = pb.constraints[active_constraint]
        self.draw_constraint(context, con)    
            
    
def drawPanels(self, context, draw_panels):
    layout = self.layout
    #print(draw_panels)
    for drawPanel in draw_panels:
        for var in dir(drawPanel):
            if var not in DEFAULT_PANEL_PROPS:
                exec('self.'+var +' = drawPanel.' + var)
                
        box = layout.box()
        box.scale_y =1
        
        row = box.row()
        row.scale_y=.6
        if hasattr(drawPanel, "draw_header"):
            fakeself = CarryLayout(row)
            if hasattr(drawPanel, 'orig_draw_header'):
                drawPanel.orig_draw_header(fakeself,context)
            #else:   
            #    drawPanel.draw_header(fakeself,context)
            
        row.label(drawPanel.bl_label)
        pd = bpy.context.scene.panelData[drawPanel.realID]
        if pd.pin: icon = 'PINNED'
        else: icon = 'UNPINNED'
        row.prop(bpy.context.scene.panelData[drawPanel.realID],'pin' , icon_only = True, icon=icon, emboss = False)
        # these are various functions defined all around blender for panels. We need them to draw the panel inside the tab panel
        
        if hasattr(drawPanel, "draw"):
            #layoutActive(self,context)
            drawPanel.draw(self,context)
        layoutActive(self,context)
        
        layout.separator()
        b=layout.box()
        b.scale_y=0
 
def pollTabs(panels, context):
    draw_plist = []
    for p in panels:
        #p = panelIDs[pname]
        #p = eval('bpy.types.'+panelID)
        polled = True
        
        
        
        if hasattr(p, "poll"):
            polled = p.opoll(context)
            '''
            try:
                
                if hasattr(p,'opoll'):
                    polled = p.opoll(context)
                    #print('opoll',p.bl_label, p.opoll(context))
                else:
                    #print('poll')
                    polled = p.poll(context)
            except:
                #print ("Unexpected error:", sys.exc_info()[0])
                pass;
                print('badly implemented poll', p.bl_label)
            '''
        if polled:
            draw_plist.append(p)     
    #print('polled', len(panels), len(draw_plist))
    return draw_plist
           
        
def getFilteredTabs(self,context):        
     
    
    #getspace = self.bl_space_type 
    getspace = context.area.type
    #getregion = self.bl_region_type 
    getregion = context.region.type
    tab_panel_category = ''
    if hasattr(self, 'bl_category'):
        tab_panel_category = self.bl_category
    panellist = getPanels(getspace, getregion )
    #print (panellist)
    tabpanel = self#eval('bpy.types.' + tabID)
    #print (bpy.types.PHYSICS_PT_collision in panellist)
    
    possible_tabs = []
    possible_tabs_wider = []
    categories = []
    #print(panellist)
    for panel in panellist:
        #if panel.bl_label == 'Collision':
            #print('collision in filterfunc')
        #print(getspace, getregion, panellist)
        if not hasattr(panel, 'bl_label'):
            print ('not a panel' ,panel)
        
        elif panel.bl_label!= '':# and panel.bl_label!= 'Influence' and panel.bl_label!= 'Mapping': #these were crashing. not anymore.
            polled = True
            
            #first  filter context and category before doing eval and getting actual panel object. still using  fo data.
            if hasattr(panel, 'bl_context'): 
                pctx = panel.bl_context.upper()
                if panel.bl_context == 'particle':
                    pctx = 'PARTICLES'
                
                if hasattr(context.space_data, 'context'):
                    if not pctx == context.space_data.context:
                        polled =False
                        
                elif hasattr(context, 'mode'):
                    #TOOLS NEED DIFFERENT APPROACH!!! THS IS JUST AN UGLY UGLY HACK....
                    if panel.bl_context == 'mesh_edit':
                        pctx = 'EDIT_MESH'
                    elif panel.bl_context == 'curve_edit':
                        pctx = 'EDIT_CURVE'
                    elif panel.bl_context == 'surface_edit':
                        pctx = 'EDIT_SURFACE'
                    elif panel.bl_context == 'text_edit':
                        pctx = 'EDIT_TEXT'
                    elif panel.bl_context == 'armature_edit':
                        pctx = 'EDIT_ARMATURE'
                    elif panel.bl_context == 'mball_edit':
                        pctx = 'EDIT_METABALL'
                    elif panel.bl_context == 'lattice_edit':
                        pctx = 'EDIT_LATTICE'
                    elif panel.bl_context == 'posemode':
                        pctx = 'POSE'
                    elif panel.bl_context == 'mesh_edit':
                        pctx = 'SCULPT'
                    elif panel.bl_context == 'weightpaint':
                        pctx = 'PAINT_WEIGHT'    
                    elif panel.bl_context == 'vertexpaint':
                        pctx = 'PAINT_VERTEX'
                    elif panel.bl_context == 'vertexpaint':
                        pctx = 'PAINT_TEXTURE'
                    elif panel.bl_context == 'objectmode':
                        pctx = 'OBJECT'
                    
                    if not pctx == context.mode:
                        polled =False
                        pass
                   #print((context.space_data.context))
            if polled:
                possible_tabs_wider.append(panel)
            if hasattr(panel, 'bl_category'): 
                if panel.bl_category != tab_panel_category:
                    polled = False
                
            if polled:
                possible_tabs.append(panel)
    #print('possible', len(possible_tabs))   
    draw_tabs_list = pollTabs(possible_tabs, context)
    self.tabcount = len(draw_tabs_list)
    #print(self.tabcount)
    bpy.types.Scene.panelTabInfo[self.bl_idname] = [self.tabcount, possible_tabs_wider]
    
    #print(draw_tabs_list)
    return draw_tabs_list
        
                            
def drawRegionUI(self,context):#, getspace, getregion, tabID):
    prefs = bpy.context.user_preferences.addons["tabs_interface"].preferences
    #print(dir(self))
   
    tabID = self.bl_idname
    
    draw_tabs_list = getFilteredTabs(self,context)
    #print('pre',self.tabcount)
    #print('filtered',len(draw_tabs_list))   
    draw_panels = drawTabs(self, context, draw_tabs_list, tabID)       
    if not prefs.original_panels:
        drawPanels(self, context, draw_panels)
    

    
class PanelUp(bpy.types.Operator):
    """ panel order utility"""
    bl_idname = 'wm.panel_up'
    bl_label = 'panel up'
    bl_options = {'REGISTER'}
    
    tabpanel_id = bpy.props.StringProperty(name="tab panel name",
                default = 'you didnt assign panel to the operator in ui def')
    panel_id = bpy.props.StringProperty(name="panel name",
                default='')
    
    
    def execute(self, context):
        #unhide_panel(self.tabpanel_id)
        tabpanel = eval('bpy.types.' + self.tabpanel_id )
        panel_id = self.panel_id
   
        ps = bpy.types.Scene.panelSpaces
       
        #print('up1')
        for s in ps:
            space = ps[s]
            
            for r in space:
               
                #print('up2')
                region = space[r]
                swapped =False
                for i,p in enumerate(region):
                    if p.realID == panel_id and i>0:
                        for i1 in range(i-1,0,-1):
                            p1 = region[i1]
                            family = False
                            if hasattr(p, 'bl_context') and hasattr(p1, 'bl_context') and p.bl_context == p1.bl_context:
                                family = True
                            if hasattr(p, 'orig_category') and hasattr(p1, 'orig_category') and p.orig_category == p1.orig_category:
                                family = True
                            #print(family, p.bl_context)
                            if family:
                                swapped = True
                                region[i]=p1
                                region[i1] = p
                                
                                break;
                        if not swapped:
                            region[i] = region[i-1]
                            region[i-1] = p
       
        return {'FINISHED'} 
 
class PanelDown(bpy.types.Operator):
    """ panel order utility"""
    bl_idname = 'wm.panel_down'
    bl_label = 'panel down'
    bl_options = {'REGISTER'}
    
    tabpanel_id = bpy.props.StringProperty(name="tab panel name",
                default=' you didnt assign panel to the operator in ui def')
    panel_id = bpy.props.StringProperty(name="panel name",
                default='')
    
    
    def execute(self, context):
        #unhide_panel(self.tabpanel_id)
        tabpanel = eval('bpy.types.' + self.tabpanel_id )
        panel_id = self.panel_id
   
        ps = bpy.types.Scene.panelSpaces
       
        #print('up1')
        for s in ps:
            space = ps[s]
            
            for r in space:
               
                #print('up2')
                region = space[r]
                swapped =False
                for i,p in enumerate(region):
                    if p.realID == panel_id and i < len(region)-1:
                        for i1 in range(i+1,len(region)):
                            p1 = region[i1]
                            family = False
                            if hasattr(p, 'bl_context') and hasattr(p1, 'bl_context') and p.bl_context == p1.bl_context:
                                family = True
                            if hasattr(p, 'orig_category') and hasattr(p1, 'orig_category') and p.orig_category == p1.orig_category:
                                family = True
                            #print(family, p.bl_context)
                            if family:
                                swapped = True
                                region[i]=p1
                                region[i1] = p
                                
                                break;
                    
                        if not swapped:
                            region[i] = region[i+1]
                            region[i+1] = p
                            break;
                    
        return {'FINISHED'} 
 
class WritePanelOrder(bpy.types.Operator):
    """write panel order utility"""
    bl_idname = 'wm.write_panel_order'
    bl_label = 'write panel order'
    bl_options = {'REGISTER'}
    
    
    
    def execute(self, context):
        ps = bpy.types.Scene.panelSpaces
        f = open('panelSpaces.py','w')
        nps={}
        for s in ps:
            space = ps[s]
            nps[s]={}
            for r in space:
                nps[s][r]=[]
                nregion = nps[s][r]
                region = space[r]
                
                for p in region:
                    #nregion.append('bpy.types.'+p.realID)
                    nregion.append(p.realID)
                #nregion.sort()
                #space[r] = nregion
                
        ddef = str(nps) 
        ddef = ddef.replace('},','},\n    ')
        ddef = ddef.replace("],",'],\n    ' )
        ddef = ddef.replace("[","[\n    " )
        ddef = ddef.replace(", ",",\n    " )
        ddef = ddef.replace("]},","]},\n    " )
        ddef = ddef.replace("]}}","]}}" )
        '''
        ddef = ddef.replace('},','},\n    ')
        ddef = ddef.replace("'],",'],\n    ' )
        ddef = ddef.replace("['","[\n    " )
        ddef = ddef.replace("', '",",\n    " )
        ddef = ddef.replace("']},","]},\n    " )
        ddef = ddef.replace("']}}","]}}" )
        '''
        #ddef.replace(',',']ahoj' )
        f.write(ddef)
        f.close()
        return {'FINISHED'}
        
def deActivatePanel(panel_name):
    s = bpy.context.scene
    item = bpy.context.scene.panelData.get(panel_name)
    item.activated = False     
    s.activated_panels.remove(s.activated_panels.find(panel_name))
    


    
class ActivatePanel(bpy.types.Operator):
    """activate panel"""
    bl_idname = 'wm.activate_panel'
    bl_label = 'activate panel'
    bl_options = {'REGISTER'}
    
    tabpanel_id = bpy.props.StringProperty(name="tab panel name",
                default='PROPERTIES_PT_tabs')
    panel_id = bpy.props.StringProperty(name="panel name",
                default='')
    category = bpy.props.StringProperty(name="panel name",
                default='')
    shift = bpy.props.BoolProperty(name="shift",
                default=False)
    def execute(self, context):
        prefs = bpy.context.user_preferences.addons["tabs_interface"].preferences
        tabpanel = eval('bpy.types.' + self.tabpanel_id )
        s =bpy.context.scene
        #print(_activated_panels)
        s.panelTabData[self.tabpanel_id].active_tab = self.panel_id
        
        panel = tabpanel
        item = bpy.context.scene.panelData.get(self.panel_id)
        
        if not self.shift:
            for i in range(len(s.activated_panels)-1,-1,-1):
                p = s.activated_panels[i]
                if p.region == panel.bl_region_type and p.space == panel.bl_space_type:
                    deActivatePanel(p.name)
                    print(p.name)
       
        
        item.space = tabpanel.bl_space_type
        
        #if prefs.original_panels:
        if self.shift and item.activated:
            deActivatePanel(self.panel_id)
        else:
            item.activated = True
            if self.category!= '':
                s.panelTabData[self.tabpanel_id]['active_tab_'+self.category] = self.panel_id
            
            if self.panel_id not in s.activated_panels:
                
                item = s.activated_panels.add()
                item.space = panel.bl_space_type
                item.region = panel.bl_region_type
                item.name = self.panel_id
                
        return {'FINISHED'}
    def invoke(self, context, event):
        if event.shift: # for Multi-selection self.obj = context.selected_objects
            self.shift = True
            #print('shift')
        else: 
            self.shift = False
        return self.execute(context)
        
class ActivateCategory(bpy.types.Operator):
    """activate category"""
    bl_idname = 'wm.activate_category'
    bl_label = 'activate panel category'
    bl_options = {'REGISTER'}
    
    tabpanel_id = bpy.props.StringProperty(name="tab panel name",
                default='PROPERTIES_PT_tabs')
    category = bpy.props.StringProperty(name="category",
                default='ahoj')
    single_panel =  bpy.props.StringProperty(name="category",
                default='')
    shift = bpy.props.BoolProperty(name="shift",
                default=False)
                
    def execute(self, context):
        prefs = bpy.context.user_preferences.addons["tabs_interface"].preferences
        #unhide_panel(self.tabpanel_id)
        tabpanel = eval('bpy.types.' + self.tabpanel_id )
        s =bpy.context.scene
        s.panelTabData[self.tabpanel_id].active_category = self.category
       
        return {'FINISHED'}    
        
    def invoke(self, context, event):
        prefs = bpy.context.user_preferences.addons["tabs_interface"].preferences
        if event.shift: # for Multi-selection self.obj = context.selected_objects
            self.shift = True
            #print('shift')
        else: 
            self.shift = False
        if self.single_panel != '':
            bpy.ops.wm.activate_panel( tabpanel_id = self.tabpanel_id, panel_id = self.single_panel, category = self.category, shift=self.shift)
        return self.execute(context)
        
class PopupPanel(bpy.types.Operator):
    """activate panel"""
    bl_idname = 'wm.popup_panel'
    bl_label = 'popup_panel'
    bl_options = {'REGISTER'}
    
    
    tabpanel_id = bpy.props.StringProperty(name="tab panel name",
                default='PROPERTIES_PT_tabs')
    panel_id = bpy.props.StringProperty(name="panel name",
                default='')
    
     
    def draw_panel(self, layout, pt):
        try:
            if hasattr(pt, "poll") and not pt.poll(bpy.context):
                print("POLL")
                return
        except:
            print("POLL")
            return
        
        p = pt(bpy.context.window_manager)
        p.layout = layout.box()
        p.draw(bpy.context)
        '''
        try:
            if hasattr(p, "draw"):
                if isinstance(p.draw, types.MethodType):
                     p.draw(bpy.context)
                else:
                    p.draw(p, bpy.context)
        except:
            pass
        '''
 
    def draw(self, context):
        layout = self.layout
        tp = _hidden_panels[self.panel_id]
       # tp = eval('bpy.types.' + self.panel_id )
        self.draw_panel(layout, tp)
 
    def execute(self, context):
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)
        
class ActivateModifier(bpy.types.Operator):
    """activate modifier"""
    bl_idname = 'object.activate_modifier'
    bl_label = 'activate modifier'
    bl_options = {'REGISTER'}
    
    modifier_name = bpy.props.StringProperty(name="Modifier name",
                default='')
    
    
    def execute(self, context):
        ob = bpy.context.active_object
        ob.active_modifier = self.modifier_name
        return {'FINISHED'}
    
class ActivateConstraint(bpy.types.Operator):
    """activate constraint"""
    bl_idname = 'object.activate_constraint'
    bl_label = 'activate constraint'
    bl_options = {'REGISTER'}
    
    constraint_name = bpy.props.StringProperty(name="Constraint name", default='')
    
    
    def execute(self, context):
        ob = bpy.context.active_object
        ob.active_constraint = self.constraint_name
        return {'FINISHED'}  
        
class ActivatePoseBoneConstraint(bpy.types.Operator):
    """activate constraint"""
    bl_idname = 'object.activate_posebone_constraint'
    bl_label = 'activate constraint'
    bl_options = {'REGISTER'}
    
    constraint_name = bpy.props.StringProperty(name="Constraint name",
                default='')
    
    
    def execute(self, context):
        pb = bpy.context.pose_bone
        pb.active_constraint = self.constraint_name
        return {'FINISHED'}  
        
class TabsPanel:
    @classmethod
    def poll(cls, context):
        
        tabspanel_info = bpy.types.Scene.panelTabInfo.get(cls.bl_idname)
        if tabspanel_info == None:
            return True
        possible_tabs = tabspanel_info[1]
        draw_tabs_list = pollTabs(possible_tabs, context)
        #print(cls.bl_region_type,cls.bl_space_type,len(draw_tabs_list),len(tabspanel_info[1]))
        #if tabspanel_info!= None:
           # c = len(pollTabs(tabspanel_info[1], context))
            #print('poll',cls.bl_idname, c, len(tabspanel_info[1]))
        return tabspanel_info==None or len(draw_tabs_list) >1
 
 
   
#THIS FUNCTION DEFINES ALL THE TABS PANELS.!!! 
def createPanels():
    spaces = bpy.types.Scene.panelSpaces
    s = bpy.types.Scene
    definitions=[]
    panelIDs = []
    pdef = "class %s(TabsPanel,bpy.types.Panel):\n    bl_space_type = '%s'\n    bl_region_type = '%s'\n    %s\n    COMPAT_ENGINES = {'BLENDER_RENDER', }\n    bl_label = ''\n    bl_options = {'HIDE_HEADER'}\n    bl_idname = '%s'\n    draw = drawRegionUI\n"
    for sname in spaces:
        space = spaces[sname]
        for rname in space:
            region = space[rname]
            
            
            categories={}
            contexts={}
            for panel in region:
                if hasattr(panel, 'bl_context'):
                    contexts[panel.bl_context] = 1
                if hasattr(panel, 'bl_category'):
                    categories[panel.bl_category] = True
                
            
            
            if len(categories)>0:
                #for cname in categories:
                cname = 'Tools'
                cnamefixed = cname.upper();
                cnamefixed = cnamefixed.replace(' ','_')
                cnamefixed = cnamefixed.replace('/','_')
                pname = '%s_PT_%s_%s_tabs' %(sname.upper(), rname.upper(), cnamefixed.upper())
                
                cstring = pdef % (pname, sname.upper() ,rname.upper(), "bl_category = '%s'" % cname ,pname)
                
                definitions.append(cstring)
                panelIDs.append(pname)
            elif len(contexts)>0:
                for cname in contexts:
                    cnamefixed = cname.upper();
                    cnamefixed = cnamefixed.replace(' ','_')
                    cnamefixed = cnamefixed.replace('/','_')
                    pname = '%s_PT_%s_%s_tabs' %(sname.upper(), rname.upper(), cnamefixed.upper())
                    
                    cstring = pdef % (pname, sname.upper() ,rname.upper(), "bl_context = '%s'" % cname ,pname)
                    
                    definitions.append(cstring)
                    panelIDs.append(pname)
            else:     
                pname = '%s_PT_%s_tabs' %(sname.upper(), rname.upper())
                cstring = pdef % (pname, sname.upper() ,rname.upper(), "",pname)
                definitions.append(cstring)
                panelIDs.append(pname)
                
    return definitions,panelIDs
class VIEW3D_PT_transform(bpy.types.Panel):
    bl_label = "Transform"
    bl_idname = "VIEW3D_PT_transform"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    @classmethod
    def poll(cls, context):
        return False
    def draw(self, context):
        pass;
        
class VIEW3D_PT_Transform(bpy.types.Panel):
    bl_label = "Transform"
    bl_idname = "VIEW3D_PT_Transform"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    @classmethod
    def poll(cls, context):
        return bpy.context.active_object != None
        
    def draw(self, context):
        layout = self.layout

        ob = context.object
        layout.alignment = 'RIGHT'
        row = layout.row()

        row.column(align = True).prop(ob, "location")
        #align=False);
        row.column(align = True).prop(ob, "lock_location")
        row = layout.row()
        if ob.rotation_mode == 'QUATERNION':
            row.column().prop(ob, "rotation_quaternion", text="Rotation")
            
        elif ob.rotation_mode == 'AXIS_ANGLE':
            #row.column().label(text="Rotation")
            #row.column().prop(pchan, "rotation_angle", text="Angle")
            #row.column().prop(pchan, "rotation_axis", text="Axis")
            row.column().prop(ob, "rotation_axis_angle", text="Rotation")
            
        else:
            row.column().prop(ob, "rotation_euler", text="Rotation")
        row.column(align = True).prop(ob, "lock_rotation")
        layout.prop(ob, "rotation_mode", text='')
        row = layout.row()
        row.column().prop(ob, "scale")
        row.column(align = True).prop(ob, "lock_scale")
        row = layout.row()
        row.column(align = True).prop(ob, "dimensions")

    
class TabInterfacePreferences(bpy.types.AddonPreferences):
    bl_idname = "tabs_interface"
    # here you define the addons customizable props
    original_panels = bpy.props.BoolProperty(name = 'Default blender panels', description = '', default=True)
    fixed_width = bpy.props.BoolProperty(name = 'Grid layout', default=True)
    fixed_columns = bpy.props.BoolProperty(name = 'Fixed number of colums', default=True)
    columns_properties = bpy.props.IntProperty(name = 'Columns in property window', default=3)
    columns_rest = bpy.props.IntProperty(name = 'Columns in side panels', default=2)
    emboss = bpy.props.BoolProperty(name = 'Invert tabs drawing', default=True)
    #align_rows = bpy.props.BoolProperty(name = 'Align tabs in rows', default=True)
    box = bpy.props.BoolProperty(name = 'Draw box around tabs', default=True)
    scale_y = bpy.props.FloatProperty(name = 'vertical scale of tabs', default=1)
    reorder_panels = bpy.props.BoolProperty(name = 'allow reordering panels (developer tool only)', default=False)
    hiding = bpy.props.BoolProperty(name = 'Enable panel hiding', description = 'switch to/from hiding mode', default=False)
    #hidden_panels = bpy.props.CollectionProperty(type = bpy.props.StringProperty)
    
    # here you specify how they are drawn
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "emboss")
        layout.prop(self, "box")
        
        layout.prop(self, "fixed_width")
        if self.fixed_width:
            layout.prop(self, "fixed_columns")
            if self.fixed_columns:
                layout.prop(self, "columns_properties")
                layout.prop(self, "columns_rest")
        #layout.prop(self, "align_rows")
        if not self.fixed_width:
            layout.prop(self, "scale_y")
        layout.prop(self, "original_panels")
        layout.prop(self, "reorder_panels")
    
    
 

def createSceneTabData():
    print('create tab panel data')
    s = bpy.context.scene
    #print('handler')
    for pname in bpy.types.Scene.panelIDs:
        p = bpy.types.Scene.panelIDs[pname]
        #print('space update in creatabpaneldata', pname)
        if not hasattr(p, 'realID') or s.panelData.get(p.realID) == None:
            buildTabDir([p])
        if not p.realID in bpy.context.scene.panelData:
            item = bpy.context.scene.panelData.add()
            item.name = p.realID
            item.space = p.bl_space_type
            item.region = p.bl_region_type
        if hasattr(p, 'bl_category'):
            c = s.categories.get(p.orig_category)
            if c == None:
                c = s.categories.add();
                c.name = p.orig_category
        #cs =s.categories.keys()
        #cs.sort()
        #print(cs)
            
    #print(_tab_panels)
  
    while len( _update_tabs)>0:
        pt= _update_tabs.pop()
        print(pt)
        #print( r.panelTabData)
        #print( s.panelTabData.get(pt.bl_rna.identifier))
        pname = pt.bl_rna.identifier
        
        if s.panelTabData.get(pname) == None:
            item = s.panelTabData.add()
            item.name = pname
    
@persistent
def scene_load_handler(scene):
    s = bpy.context.scene
   
    btypeslen = len(dir(bpy.types))
    if btypeslen!= s.get('bpy_types_len'):
        updatePanels()
    s['bpy_types_len'] = btypeslen
    print(btypeslen)
    #if len(_update_tabs)>0:
    createSceneTabData()
    
            
@persistent
def scene_update_handler(scene):
    s = bpy.context.scene
    sc = s.get('tabs_update_counter')
    first = False
    if sc == None:
        first = True
        sc = s['tabs_update_counter'] = 0
        
    s['tabs_update_counter']+=1
    if sc>200 or first:# this should be replaced by better detecting if registrations might have changed.
        s['tabs_update_counter'] = 0
        t = time.time()
        s = bpy.context.scene
       
        btypeslen = len(dir(bpy.types))
        if btypeslen!= s.get('bpy_types_len') or first:
            updatePanels()
        s['bpy_types_len'] = btypeslen
        #print('updating', btypeslen)
        if len(_update_tabs)>0:
            createSceneTabData()
        
        allt = s.get('updatetime')
        tadd = time.time()-t
        if allt== None:
            s['updatetime']=tadd
        else:
            s['updatetime']+=tadd
@persistent
def object_select_handler(scene):
    s = bpy.context.scene
    #print('handler')
    if bpy.context.active_object:
        if not hasattr(s,'active_previous'):
            #print('firsttime')
            s.active_previous = bpy.context.active_object.name
        if bpy.context.active_object.name != s.active_previous:
            #print("Selected object", bpy.context.active_object.name)
            s.active_previous = bpy.context.active_object.name
        

        
def register():
    
    bpy.utils.register_class(VIEW3D_PT_Transform)#we need this panel :()
    bpy.utils.register_class(VIEW3D_PT_transform)#we need this panel :()

    
    bpy.utils.register_class(PanelUp)
    bpy.utils.register_class(PanelDown)
    bpy.utils.register_class(WritePanelOrder)
    bpy.utils.register_class(ActivatePanel)
    bpy.utils.register_class(ActivateCategory)
    bpy.utils.register_class(PopupPanel)
    bpy.utils.register_class(ActivateModifier)
    bpy.utils.register_class(ActivateConstraint)
    bpy.utils.register_class(ActivatePoseBoneConstraint)
    bpy.utils.register_class(tabSetups)
    bpy.utils.register_class(panelData)
    bpy.utils.register_class(tabCategoryData)
    bpy.utils.register_class(TabInterfacePreferences)
    
    bpy.types.DATA_PT_modifiers.draw = modifiersDraw
    bpy.types.OBJECT_PT_constraints.draw = constraintsDraw
    bpy.types.BONE_PT_constraints.draw = boneConstraintsDraw
    
    bpy.types.Scene.active_previous = bpy.props.StringProperty(name = 'active object previous', default = '')
    bpy.types.Object.active_modifier = bpy.props.StringProperty(name = 'active modifier', default = '')
    bpy.types.Object.active_constraint = bpy.props.StringProperty(name = 'active constraint', default = '')
    bpy.types.PoseBone.active_constraint = bpy.props.StringProperty(name = 'active constraint', default = '')
    bpy.types.Scene.panelData = bpy.props.CollectionProperty(type=panelData)
    
    bpy.types.Scene.panelTabData = bpy.props.CollectionProperty(type=tabSetups)
    bpy.types.Scene.categories = bpy.props.CollectionProperty(type=tabCategoryData)
    
    bpy.types.Scene.pinned_panels = bpy.props.CollectionProperty(type=panelData) #only pinned pann
    bpy.types.Scene.activated_panels = bpy.props.CollectionProperty(type=panelData) #only pinned pann
    #bpy.types.Scene.hidden_tabs = bpy.props.CollectionProperty(type=panelData)
    bpy.app.handlers.load_post.append(scene_load_handler)
    bpy.app.handlers.scene_update_pre.append(scene_update_handler)
    
    allpanels = getPanelIDs()
    bpy.types.Scene.panelSpaces = buildTabDir(allpanels)
    bpy.types.Scene.panelTabInfo = {}
    
    #build the classess here!!
    definitions, panelIDs = createPanels()
    for d in definitions:
        #print(d)
        exec(d)
    for pname in panelIDs:
        #print('register ', pname)
        p = eval(pname)
        bpy.utils.register_class(eval(pname))
        pt = eval('bpy.types.'+pname)
        _tab_panels[pname] = pt    
        #print(pname)
    
     
    
def unregister():
    #first, fix the panels:
    for panel in bpy.types.Scene.panelIDs:
        
        if hasattr(panel, 'bl_category'):
            if hasattr(panel, 'orig_category'):
                panel.bl_category = panel.orig_category
            
        unhide_panel(panel.realID)
        
    bpy.utils.unregister_class(VIEW3D_PT_Transform)
    bpy.utils.unregister_class(VIEW3D_PT_transform)
    
    
    
    definitions, panelIDs = createPanels()
    for d in definitions:
        #print(d)
        exec(d)
    for pname in panelIDs:
        #print('unregister ', pname)
        if hasattr(bpy.types, pname):
            bpy.utils.unregister_class(eval('bpy.types.'+pname))
    
    bpy.utils.unregister_class(PanelUp)
    bpy.utils.unregister_class(PanelDown)
    bpy.utils.unregister_class(WritePanelOrder)
    bpy.utils.unregister_class(ActivatePanel)
    bpy.utils.unregister_class(ActivateCategory)
    bpy.utils.unregister_class(PopupPanel)
    bpy.utils.unregister_class(ActivateModifier)
    bpy.utils.unregister_class(ActivateConstraint)
    bpy.utils.unregister_class(ActivatePoseBoneConstraint)
    bpy.utils.unregister_class(tabSetups)
    bpy.utils.unregister_class(panelData)
    bpy.utils.unregister_class(tabCategoryData)
    bpy.utils.unregister_class(TabInterfacePreferences)
    

if __name__ == "__main__":
    register()
    
    #https://github.com/meta-androcto/blenderpython/tree/master/scripts/addons_extern/AF_view3d_mod https://github.com/meta-androcto/blenderpython/tree/master/scripts/addons_extern/AF_view3d_toolbar_mod
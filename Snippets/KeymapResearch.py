#bl_info = {
#    "name": "KeymapResearch",
#    "author": "chichige-bobo",
#    "version": (1, 1),
#    "blender": (2, 69, 0),
#    "location": "TextEditor > ToolPanel ",
#    "description": "Research keymaps for better understanding",
#    "category": "Developer"}

import bpy
from bpy.props import *

class KeymapConflictCheckOperator(bpy.types.Operator):
    """Check whether key combination conflicts with existed"""
    bl_idname = "addongen.keymap_confilict_check_operator"
    bl_label = "Keymap Conflict Check Operator"
    bl_options = {'REGISTER'}
    
    type = bpy.props.StringProperty()
    
    def execute(self, context):
        pass

class KeymapResearchOperator(bpy.types.Operator):
    """Research keyconfigs.keymaps.keymap_items then write report to as text"""
    bl_idname = "addongen.keymap_research_operator"
    bl_label = "Keymap Research Operator"
    bl_options = {'REGISTER'}
    
    type = bpy.props.StringProperty()
    
    sep = "\n%s\n\n" % ('#' * 50)

    def execute(self, context):
        pps = context.scene.chichige_keymap_research_props        
        kcs = context.window_manager.keyconfigs
        kc = kcs[pps.keyconfig]
        km = kc.keymaps[pps.keymap]
        text = ""
        
        if self.type == "BASIC_STATS":
            text = self.getBasicStatistics(kcs)
        elif self.type == "KM_DETAIL":
            text += self.getKeymapDetail(kc)
        elif self.type == "FULL_KEYMAP_ITEMS":
            text += self.getFullKeymapItems(kc)
        elif self.type == "KM_ITEMS_DETAIL":
            text += self.getKeymapItems_detail(kc, km)
            
        elif self.type == "KM_UNORDINARY":
            text += self.getKeymaps_unordinary(kcs)
        elif self.type == "KM_KMI_UNORDINARY":
            text += self.getKeymaps_KeymapItems_unordinary(kcs)
            
        elif self.type == "ENUM_ITEMS":
            text += self.getEnumItems()
        elif self.type == "CUSTOM_FUNC":
            text += self.getCustomFiltering(kcs)
            
        textObjName = pps.text_name  # this prop is 'SKIP_SAVE'. but not worked as i expected
        if not textObjName or not textObjName in bpy.data.texts:
            textObj = bpy.data.texts.new('KeymapResearch_Report')
            pps.text_name = textObj.name
        else:
            textObj = bpy.data.texts[textObjName]
        
        textObj.from_string(text)
        
        #context.space_data.text = textObj ################# release comment to be active the report automatically 
        self.report({'INFO'}, "New report was written to %s" % textObj.name)
        print('If you are looking for the report, select "%s" in TextEditor' % textObj.name)
        return {'FINISHED'}
    
    #------------        
    def getBasicStatistics(self, kcs):
        text = """\
# Summary according to my observationas. (NOT OFFICIAL)
#
# keymap.space_type : almost 'EMPTY' but every other space_type exists.
# keymap-region_type is all 'WINDOW'. no exception found.
# keymap.is_modal : almost non modal. few are modal. e.g. GestureBorder, View3DFlyModal, KnifeToolModalMap
# keymap.is_user_modified : always False
# 
# keymap_item.propvalue        : always "NONE" except modal keymap
# When keymap is modal, keymap_item.name == "" and .idname == "" and .properties == "NONE".
# keymap_item.is_user_defined  : always False 
# keymap_item.is_user_modified : always False 
# keymap_item.key_modifier     : always "NONE" but GreasePencil has 'D'
# keymap_item.value            : 'ANY' when map_type is 'TIMER' or 'TEXTINPUT'
# when keymap is modal and keymap_item.map_type is 'TEXTINPUT'/'TIMER', .value is always 'NOTHING' and .any is always True
# 
# Hierarchy is keyconfigs.keyconfig.keymaps.keymap.keymap_items.keymap_item
#
###################################################
# Experiment:
# When run following lines, which keyconfig reacts? 
# km = wm.keyconfigs.XXXXX.keymaps.new(name='Grease Pencil', space_type='EMPTY')
# kmi = km.keymap_items.new("addongen.hello_world_operator", 'SPACE', 'PRESS', shift=True)
#
# Result:
# If added to Blender,         BlenderUser reflected it
# If added to BlenderAddon,    BlenderUser reflected it
# If added to BlenderUser,     no other reflected it
#
# When active is 3Dsmax,
# If added to BlenderAddon,    BlenderUser reflected it
# If added to active (3Dsmax), BlenderUser reflected it
#
# Conclusion:
# To search the conflict while keyconfigs.addon is used to register new key,
# the search should be done against keyconfigs.user 
# (If the Addon goes public, only Blender's and Addon's should be concerned.)
# (If someone using 3Dsmax preset, the user should change the key, not by the author.)
"""
        text += self.sep
        text += "keyconfigs\n"
        for kc in kcs:
            text += '    %s has %d keymaps\n' % (kc.name, len(kc.keymaps))
        
        text += self.sep
        text += "keyconfigs.active.name =  %s\n" % kcs.active.name 
        text += "keyconfigs.default.name = %s\n" % kcs.default.name 
        text += "keyconfigs.addon.name =   %s\n" % kcs.addon.name 
        text += "keyconfigs.user.name =    %s\n" % kcs.user.name 
        
        text += self.sep
        text += "#Sum of map_type of all keymap_items of all keymaps\n"
        for kc in kcs:
            dic = {'KEYBOARD' : 0, 'TWEAK' : 0, 'MOUSE' : 0, 'NDOF' : 0, 'TEXTINPUT': 0, 'TIMER' : 0}
            for km in kc.keymaps:
                for kmi in km.keymap_items:
                    dic[kmi.map_type] += 1
            text += '%s\n' % kc.name
            for k,v in dic.items():
                text += '    %s %s: %d\n' % (k, " " * (9 - len(k)), v)
                
        
        text += self.sep
        text += "# keyconfig\n"
        text += "#     keymap(len(keymap_items))\n\n"
        text += "#------------\n"
        for kc in kcs:
            text += '%s\n' % kc.name   
            for km in kc.keymaps:
                text += '    %s (%d)\n' % (km.name, len(km.keymap_items))        
        return text
    
    #-----------            
    def getKeymapDetail(self, kc):
        text = ""
                
        text += self.sep
        text += '%s\n' % kc.name   
        for km in kc.keymaps:
            text += '    %s (%d)\n' % (km.name, len(km.keymap_items))
            text += '        space_type =  %s\n' % km.space_type
            text += '        region_type = %s\n' % km.region_type
            text += '        show_expanded_items = %s\n' % km.show_expanded_items
            text += '        is_user_modified =    %s\n' % km.is_user_modified
            text += '        is_modal = %s\n' % km.is_modal
        return text

    #--------------
    def getFullKeymapItems(self, kc):
        text = "" 
        
        text += self.sep
        text += kc.name + "\n"
        for km in kc.keymaps:
            text += '    %s #(%s%s)\n' % (km.name, km.space_type, ", modal" if km.is_modal else "")
            for kmi in km.keymap_items:
                text += "            %s \n" % (kmi.name if kmi.name else "(.name is empty)")
                text += "                idname = %s \n" % kmi.idname
                text += "                map_type = %s \n" % kmi.map_type
                text += "                propvalue = %s \n" % kmi.propvalue
                text += "                type = %s \n" % kmi.type
                text += "                value = %s \n" % kmi.value
                keys = ['any', 'ctrl', 'shift', 'alt', 'oskey']
                keysTrue = []
                for k in keys:
                    if getattr(kmi, k):
                        keysTrue.append(k)              
                text += "                keys : %s\n" % keysTrue 
        return text    
        
    def getKeymapItems_detail(self, kc, km):
        text = "# This text is automatically override everytime run the command.\n\n" 
        text += self.sep
        text += kc.name + "\n"
        text += '    %s \n' % km.name 
        text += '        modal, usermod : %s, %s \n' % (km.is_modal, km.is_user_modified) 
        text += '        %s, %s \n' % (km.region_type, km.space_type)
        for kmi in km.keymap_items:
                text += "            %s \n" % (kmi.name if kmi.name else "(.name is empty)")
                text += "                    id = %s \n" % kmi.id
                text += "                    active = %s \n" % kmi.active
                text += "                    idname = %s \n" % kmi.idname
                text += "                    properties (class) = %s \n" % kmi.properties.__class__.__name__
                text += "                    propvalue = %s \n" % kmi.propvalue
                text += "                    is_user_defined = %s \n" % kmi.is_user_defined
                text += "                    is_user_modified = %s \n" % kmi.is_user_modified
                text += "                    key_modifier = %s \n" % kmi.key_modifier
                text += "                    map_type = %s \n" % kmi.map_type
                text += "                    type = %s \n" % kmi.type
                text += "                    value = %s \n" % kmi.value
                text += "                    any = %s \n" % kmi.any
                text += "                    shift = %s \n" % kmi.shift
                text += "                    alt = %s \n" % kmi.alt
                text += "                    ctrl = %s \n" % kmi.ctrl
                text += "                    oskey = %s \n" % kmi.oskey
        return text  
    
    
     #---------
    def getKeymaps_unordinary(self, kcs):
        text = ""
        
        text += self.sep
        text += "#Validate keymap.space_type is always 'EMPTY'\n\n"
        for kc in kcs:
            text += '%s\n' % kc.name
            subText = ""   
            for km in kc.keymaps:
                if km.space_type != 'EMPTY':
                    subText += '    %s\n' % km.name
                    subText += '        space_type = %s\n' % km.space_type
            text += "    (no exception found)\n" if not subText else subText
            text += "\n"
        
        text += self.sep
        text += "# Validate keymap.region_type is always 'WINDOW'\n\n"
        for kc in kcs:
            text += '%s\n' % kc.name   
            subText = ""   
            for km in kc.keymaps:
                if  km.region_type != 'WINDOW':
                    subText += '    %s\n' % km.name
                    subText += '        region_type = %s\n' % km.region_type
            text += "    (no exception found)\n" if not subText else subText
            text += "\n"
        
        text += self.sep
        text += "# Validate keymap.is_modal is always True\n\n"
        for kc in kcs:
            text += '%s\n' % kc.name   
            subText = ""   
            for km in kc.keymaps:
                if km.is_modal:
                    subText += '    %s\n' % km.name
            text += "    (no exception found)\n" if not subText else subText
            text += "\n"

        text += self.sep
        text += "# Validate keymap.show_expanded and .is_user_modified are always False\n\n"
        for kc in kcs:
            text += '%s\n' % kc.name   
            subText = ""   
            for km in kc.keymaps:
                if km.show_expanded_items or km.is_user_modified:
                    subText += '    %s\n' % km.name
                    subText += '        show_expanded_items = %s\n' % km.show_expanded_items
                    subText += '        is_user_modified = %s\n' % km.is_user_modified
            text += "    (no exception found)\n" if not subText else subText
            text += "\n"
        
        #------    
        text += self.sep
        text += "# Compare keyconfigs.default and keyconfigs.user \n\n"
        kc_def = kcs.default
        kc_user = kcs.user
        #if all kc_def.keymaps exists in kc_user 
        text += "# ------\n"
        text += '# Check if all %s.keymaps exists in %s.keymaps (listed below are those exist only in keyconfig "%s")\n' % (kc_def.name, kc_user.name, kc_def.name)
        text += "%s\n" % kc_def.name
        subText = ""
        for km_d in kc_def.keymaps:
            isKMExist = False
            for km_u in kc_user.keymaps:
                if km_d.name == km_u.name and km_d.is_modal == km_u.is_modal and km_d.is_user_modified == km_u.is_user_modified and \
                   km_d.space_type == km_u.space_type and km_d.region_type == km_u.region_type:
                    
                    isKMExist = True
                    subSubText = ""            
                    for kmi_d in km_d.keymap_items:
                        isKMIExist = False
                        for kmi_u in km_u.keymap_items:
                            if not km_d.is_modal and kmi_d.name == kmi_u.name and kmi_d.id == kmi_u.id:
                                isKMIExist = True
                                break
                            elif km_d.is_modal and kmi_d.propvalue == kmi_u.propvalue and kmi_d.id == kmi_u.id:
                                isKMIExist = True
                                break
                            
                        if not isKMIExist:
                            subSubText += '        %s\n' % (kmi_d.name if kmi_d.name else "(.name is empty)")
                            subSubText += '            id =  %s\n' % kmi_d.id
                            subSubText += "" if not km_d.is_modal else '            propvalue =  %s\n' % kmi_d.propvalue
                    
                    if subSubText:
                        subText += '    %s\n' % km_d.name
                        subText += subSubText
                        
            if not isKMExist:
                subText += '    %s (%d) # keymap was not matched.\n' % (km_d.name, len(km_d.keymap_items))
                subText += '        space_type =  %s\n' % km_d.space_type
                subText += '        region_type = %s\n' % km_d.region_type
                subText += '        is_user_modified =    %s\n' % km_d.is_user_modified
                subText += '        is_modal = %s\n' % km_d.is_modal
        text += ("    (all %s.keymaps found in %s)\n" % (kc_def.name, kc_user.name)) if not subText else subText
        text += "\n"
        
        #if all kc_user.keymaps exists in kc_def 
        text += '# Check if all %s.keymaps exists in %s.keymaps \n' % (kc_user.name, kc_def.name)
        text += "%s\n" % kc_user.name
        subText = ""
        for km_u in kc_user.keymaps:
            isKMExist = False
            for km_d in kc_def.keymaps:
                if km_u.name == km_d.name and km_u.is_modal == km_d.is_modal and km_u.is_user_modified == km_d.is_user_modified and \
                   km_u.space_type == km_d.space_type and km_u.region_type == km_d.region_type:
                    
                    isKMExist = True
                    subSubText = ""            
                    for kmi_u in km_u.keymap_items:
                        isKMIExist = False
                        for kmi_d in km_d.keymap_items:
                            if not km_u.is_modal and kmi_u.name == kmi_d.name and kmi_u.id == kmi_d.id:
                                isKMIExist = True
                                break
                            elif km_u.is_modal and kmi_u.propvalue == kmi_d.propvalue and kmi_u.id == kmi_d.id:
                                isKMIExist = True
                                break
                            
                        if not isKMIExist:
                            subSubText += '        %s\n' % (kmi_u.name if kmi_u.name else "(.name is empty)")
                            subSubText += '            id =  %s\n' % kmi_u.id
                            subSubText += "" if not km_u.is_modal else '            propvalue =  %s\n' % kmi_u.propvalue
                    
                    if subSubText:
                        subText += '    %s\n' % km_u.name
                        subText += subSubText
                            
            if not isKMExist:
                subText += '    %s (%d) # keymap was not matched.\n' % (km_u.name, len(km_u.keymap_items))
                subText += '        space_type =  %s\n' % km_u.space_type
                subText += '        region_type = %s\n' % km_u.region_type
                subText += '        is_user_modified =    %s\n' % km_u.is_user_modified
                subText += '        is_modal = %s\n' % km_u.is_modal
        text += ("    (all %s.keymaps found in %s)\n" % (kc_user.name, kc_def.name)) if not subText else subText
        text += "\n"
                
        return text

    #--------------
    def getKeymaps_KeymapItems_unordinary(self, kcs):
        text = """\
# name = Rotate View                               # has value when not modal / "" when modal
# idname = "operator's bl_idname"                  # has value when not modal / "" when modal
# properties (class) = Operator's generated class  # has value when not modal / "NONE" when modal
# propvalue = CONFIRM                              # "NONE" when Not modal / has value when modal
# is_user_defined = False                          # always False 
# is_user_modified = False                         # always False
# key_modifier = NONE                              # always "NONE" but GreasePencil
# map_type = MOUSE 
# type = MIDDLEMOUSE 
# value = RELEASE
# any = True                                       # if this is True, all other keys are also True 
# shift = True 
# alt = True 
# ctrl = True 
# oskey = True

"""
        text += self.sep
        text += '# Validate .name & .idname have value and propvalue is "NONE" when not modal. \n'
        text += '#          .name & .idname are  empty and propvalue has value when modal. \n\n'
        for kc in kcs:
            text += kc.name + "\n"
            kmText = ""
            for km in kc.keymaps:
                subText = ""
                for kmi in km.keymap_items:
                    if not km.is_modal:
                        if kmi.name != "" and kmi.idname != "" and kmi.propvalue == "NONE":
                            continue
                    else:    
                        if kmi.name == "" and kmi.idname == "" and kmi.propvalue != "NONE":
                            continue
                
                    subText += "            %s \n" % (kmi.name if kmi.name != "" else "(no .name found)")
                    subText += "                idname = %s \n" % (kmi.idname if kmi.idname != "" else '""')
                    subText += "                propvalue = %s \n" % kmi.propvalue
                    subText += "                properties (class) = %s \n" % kmi.properties.__class__.__name__
    
                if subText:
                    kmText += '    %s \n' % km.name 
                    kmText += '        modal, usermod : %s, %s \n' % (km.is_modal, km.is_user_modified) 
                    kmText += '        %s, %s \n' % (km.region_type, km.space_type)
                    kmText += subText
            text += "    (No exception found)\n" if not kmText else kmText
            text += "\n"
        
        text += self.sep
        text += '# Validate .is_user_defined and .is_user_modified are always False\n'
        text += '#      and .key_modifier always "NONE" \n\n'
        for kc in kcs:
            text += kc.name + "\n"
            kmText = ""
            for km in kc.keymaps:
                subText = ""
                for kmi in km.keymap_items:
                    if kmi.is_user_defined or kmi.is_user_modified or kmi.key_modifier != "NONE":
                        subText += "            %s \n" % (kmi.name if kmi.name != "" else "(.name is empty)")
                        subText += "                is_user_defined = %s \n" % kmi.is_user_defined
                        subText += "                is_user_modified = %s \n" % kmi.is_user_modified
                        subText += "                key_modifier = %s \n" % kmi.key_modifier
                        subText += "                type = %s \n" % kmi.type
                        subText += "                value = %s \n" % kmi.value
                        keys = ['any', 'ctrl', 'shift', 'alt', 'oskey']
                        keysTrue = []
                        for k in keys:
                            if getattr(kmi, k):
                                keysTrue.append(k)                       
                        subText += "                keys : %s\n" % keysTrue 
                if subText:
                    kmText += '    %s \n' % km.name 
                    kmText += '        modal, usermod : %s, %s \n' % (km.is_modal, km.is_user_modified) 
                    kmText += '        %s, %s \n' % (km.region_type, km.space_type)
                    kmText += subText
            text += "    (no exception found)\n" if not kmText else kmText
            text += "\n"
        
        text += self.sep
        text += '#Validate when .any == True, other keys (shift, ctrl, alt, oskey) are all True. If any == False, at least one of the keys is False\n\n'
        for kc in kcs:
            text += kc.name + "\n"
            kmText = ""
            for km in kc.keymaps:
                subText = ""
                for kmi in km.keymap_items:
                    if kmi.any:
                        if kmi.shift and kmi.alt and kmi.ctrl and kmi.oskey:
                            continue
                    else:
                        if not(kmi.shift and kmi.alt and kmi.ctrl and kmi.oskey): # all True is the exception when .any is False) 
                            continue
     
                    subText += "            %s \n" % (kmi.name if kmi.name != "" else "(.name is empty")
                    subText += "                any = %s \n" % kmi.any
                    subText += "                shift = %s \n" % kmi.shift
                    subText += "                alt = %s \n" % kmi.alt
                    subText += "                ctrl = %s \n" % kmi.ctrl
                    subText += "                oskey = %s \n" % kmi.oskey
                
                if subText:
                    kmText += '    %s \n' % km.name 
                    kmText += '        modal, usermod : %s, %s \n' % (km.is_modal, km.is_user_modified) 
                    kmText += '        %s, %s \n' % (km.region_type, km.space_type)
                    kmText += subText
            text += "    (no exception found)\n" if not kmText else kmText
            text += "\n"
        
        text += self.sep
        text += '# Validate any is always False when keymap is not modal and always True when keymap is modal.\n'
        for kc in kcs:
            text += kc.name + "\n"
            kmText = ""
            for km in kc.keymaps:
                subText = ""
                for kmi in km.keymap_items:
                    if (not km.is_modal and kmi.any) or (km.is_modal and not kmi.any):
                        subText += "            %s \n" % (kmi.name if kmi.name != "" else "(.name is empty)")
                        subText += "                propvalue = %s \n" % kmi.propvalue
                        subText += "                any = %s \n" % kmi.any
                if subText:
                    kmText += '    %s \n' % km.name 
                    kmText += '        modal, usermod : %s, %s \n' % (km.is_modal, km.is_user_modified) 
                    kmText += '        %s, %s \n' % (km.region_type, km.space_type)
                    kmText += subText
            text += "    (no exception found)\n" if not kmText else kmText
            text += "\n"
            
        return text
   
    def getEnumItems(self):
        text = ""    
        text += self.sep
        text += self.listEnumItems(bpy.types.KeyMap, "space_type", "KeyMap.space_type")
        text += self.sep
        text += self.listEnumItems(bpy.types.KeyMap, "region_type", "KeyMap.region_type")
        text += self.sep
        text += self.listEnumItems(bpy.types.KeyMapItem, "map_type", "KeyMapItem.map_type")
        text += self.sep
        text += self.listEnumItems(bpy.types.KeyMapItem, "type", "KeyMapItem.type")
        text += self.sep
        text += self.listEnumItems(bpy.types.KeyMapItem, "value", "KeyMapItem.value")
        text += self.sep
        text += self.listEnumItems(bpy.types.KeyMapItem, "key_modifier", "KeyMapItem.key_modifier")
        text += self.sep
        text += self.listEnumItems(bpy.types.KeyMapItem, "propvalue", "KeyMapItem.propvalue")
        return text
    
    def listEnumItems(self, cls, propName, title):
        items = cls.bl_rna.properties[propName].enum_items.values()
        text = title + "\n"
        for item in items:
            text += "    %s, %s, %s, %s, %s\n" % (item.identifier, item.name, item.description, item.icon, item.value)
        return text   

    #CURRENT    
    def getCustomFiltering(self, kcs): 
        text = ""    
        text += self.sep
        text += '# Just custom filtering\n'
        for kc in kcs:
            text += kc.name + "\n"
            kmText = ""
            for km in kc.keymaps:
                subText = ""
                for kmi in km.keymap_items:
                    if km.is_modal and kmi.any and kmi.map_type in {'TEXTINPUT', 'TIMER'}:
                        subText += "            %s \n" % (kmi.name if kmi.name != "" else "(.name is empty)")
                        subText += "                map_type = %s \n" % kmi.map_type
                        subText += "                type = %s \n" % kmi.type
                        subText += "                value = %s \n" % kmi.value
                        subText += "                properties = %s \n" % kmi.properties.__class__#.properties['name']
                        subText += "                propvalue = %s \n" % kmi.propvalue
                        keys = ['any', 'ctrl', 'shift', 'alt', 'oskey']
                        keysTrue = []
                        for k in keys:
                            if getattr(kmi, k):
                                keysTrue.append(k)                       
                        subText += "                keys : %s\n" % keysTrue 
                if subText:
                    kmText += '    %s \n' % km.name 
                    kmText += '        modal, usermod : %s, %s \n' % (km.is_modal, km.is_user_modified) 
                    kmText += '        %s, %s \n' % (km.region_type, km.space_type)
                    kmText += subText
            text += "    (no matches found)\n" if not kmText else kmText
            text += "\n"
        return text
 
        
#########################################################
class KeymapResearchPanel(bpy.types.Panel):
    """Panel for Keymap Research Operator"""
    bl_idname = "TEXTEDITOR_PT_keymap_research_panel"
    bl_label = "Keymap Research Panel"

    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    
            
    def draw(self, context):
        pps = context.scene.chichige_keymap_research_props
        
        layout = self.layout
        layout.operator(KeymapResearchOperator.bl_idname, text = "Basic Stats").type = "BASIC_STATS"
        split = layout.split(0.2)
        split.label("Keyconfigs")
        col = split.column()
        col.prop(pps, "keyconfig", text="")
        col.operator(KeymapResearchOperator.bl_idname, text = "Keymap Detail").type = "KM_DETAIL"
        col.operator(KeymapResearchOperator.bl_idname, text = "Full KeymapItems").type = "FULL_KEYMAP_ITEMS"
        split = layout.split(0.3)
        split.label("Keymaps")
        col = split.column()
        col.prop(pps, "keymap", text = "")
        col.operator(KeymapResearchOperator.bl_idname, text = "KeymapItems Detail").type = "KM_ITEMS_DETAIL"
        layout.label("-" * 60)
        layout.operator(KeymapResearchOperator.bl_idname, text = "Keymaps - Unordinary").type = "KM_UNORDINARY"
        layout.operator(KeymapResearchOperator.bl_idname, text = "Keymaps KeymapItems - Unordinary").type = "KM_KMI_UNORDINARY"
        layout.label("-" * 60)
        layout.operator(KeymapResearchOperator.bl_idname, text = "Enum Items").type = "ENUM_ITEMS"
        layout.operator(KeymapResearchOperator.bl_idname, text = "Custom Filtering").type = "CUSTOM_FUNC"
        layout.label("-" * 60)
        
                

##########################################################

#--EnumItem-------
def getItems_keyconfig(self, context):
    kcs = context.window_manager.keyconfigs
    retVal = []
    for kc in kcs:
        retVal.append((kc.name, kc.name, kc.name))
    return retVal

def getItems_keymap(self, context):
    pps = context.scene.chichige_keymap_research_props
    kcs = context.window_manager.keyconfigs
    kc = kcs[pps.keyconfig]
    
    retVal = []
    for km in kc.keymaps:
        retVal.append((km.name, km.name, km.name))
    return retVal

    
class MySceneProps(bpy.types.PropertyGroup):
    text_name = bpy.props.StringProperty(options = {'SKIP_SAVE'})
    keyconfig = bpy.props.EnumProperty(items = getItems_keyconfig)
    keymap= bpy.props.EnumProperty(items = getItems_keymap)

###########################################################
def register():
    bpy.utils.register_class(MySceneProps)
    bpy.types.Scene.chichige_keymap_research_props = bpy.props.PointerProperty(type = MySceneProps)
    bpy.utils.register_class(KeymapResearchOperator)
    bpy.utils.register_class(KeymapResearchPanel)

def unregister():
    bpy.utils.unregister_class(MySceneProps)
    del bpy.types.Scene.chichige_keymap_research_props
    bpy.utils.unregister_class(KeymapResearchOperator)
    bpy.utils.unregister_class(KeymapResearchPanel)
    
if __name__ == "__main__":
    register()

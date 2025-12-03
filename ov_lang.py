#lang.py
import ov_globals as g

# Window: Home
new_sample = ['New sample', 'Muestra nueva']
open_sample = ['Open sample', 'Abrir muestra']
edit_sample = ['Edit sample', 'Modificar muestra']
view_sample = ['View sample', 'Ver muestra']
new_config = ['New method', 'Método nueva']
open_config = ['Open method', 'Abrir config']
edit_config = ['Edit method','Modificar config']
new_config_full = ['New method','Ajuste de voltametría nueva']
view_config_full = ['View method','Revisar ajustes de voltametría']
info_msg = ["Welcome to <a href='https://github.com/ask53/openVoltam'>OpenVoltam</a>!<br><br>An open source project by <a href='https://www.caminosdeagua.org'>Caminos de Agua</a> and <a href='https://www.iorodeo.com'>IO Rodeo</a><br><br>v0.0 | 2025","Bienvenidx a <a href='https://github.com/ask53/openVoltam'>OpenVoltam</a>!<br><br>Un proyecto de fuente abierta por <a href='https://www.caminosdeagua.org'>Caminos de Agua</a> y <a href='https://www.iorodeo.com'>IO Rodeo</a><br><br>v0.0 | 2025"]
window_home = ['OpenVoltam','OpenVoltam']

# Menus
menu_sample = ['Sample','Muestra']
menu_config = ['Method','Ajustes de voltametría']
menu_run = ['Run','??????']

# Window: edit sample
s_edit_name = ['Sample name','Nombre de la muestra']
s_edit_date_c = ["Date collected","Fecha recolectada"]
s_edit_loc = ['Location collected','Ubicación recolectada']
s_edit_contact = ['Contact','Contacto']
s_edit_sampler = ['Collected by','Recolectado por']
s_edit_notes = ['Notes','Notas']
s_edit_save = ['Save','Guardar']
s_edit_save_as = ['Save as...','Guardar como...']
s_edit_cancel = ['Cancel','Cancelar']
s_edit_close_wo_save = ['Close without saving','Cerar sin guardar']
s_edit_discard = ['Discard changes?','¿Tirar cambios a la basura?']
e_edit_save_dialog = ['Are you sure you want to close without saving this sample?', "Favor de confirmar si quieres cerar sin guardar esta muestra."]

# Window: edit sweep configuration
c_edit_header_edit = ['Edit method: ', 'Editar los ajustes de voltametría']
c_edit_header_new = ['New method: ', 'Ajuste de voltametría nueva']
c_edit_header_view = ['View method: ', 'TEXTO']

# Window: sample
s_view_info = ['View info','Ver datos']
s_edit_info = ['Edit info','Modificar datos']

# Window: run configuration
rc_window_title = ['Configure run(s)','TEXTO']
rc_type_blank = ['BlankLANG','TEXTO']
rc_type_sample = ['SampleLANG','TEXTO']
rc_type_stdadd = ['Standard additionLANGLANGGGG','TEXTO']
rc_select = ['Select...','TEXTO']

# Window: sweep profile builder/editer
sp_types = {
    g.M_CONSTANT: ['Voltage: constant','TEXTO'],
    g.M_RAMP: ['Voltage: ramp','TEXTO']
    }
sp_add_step = ['Add step','TEXTO']
sp_edit_step = ['Edit step','TEXTO']
sp_add_btn = ['Add','TEXTO']
sp_edit_btn = ['Apply edits','TEXTO']



#Alerts
alert_header = ['Alert!', '¡Alerta!']
alert_s_edit_name = ['The name is too short.\nPlease enter a sample name that contains at least three characters.','El nombre es demaciado corto.\nFavor de ingresar un nombre de la muestra que contiene al menos tres carácteres.']
alert_s_edit_save_error = ['There was and issue saving the file, please try again.','Había un error en el proceso de guardar el archivo. Favor de intentar otra vez.']
# File system navigation
filetype_sample_lbl = ['OpenVoltam Sample', 'Muestra de OpenVoltam']
filetype_sp_lbl = ['OpenVoltam Profile', 'Perfíl de OpenVoltam']





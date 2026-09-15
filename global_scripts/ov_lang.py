#lang.py
from global_scripts import ov_globals as g

""" For copying:

 = {'eng': '',
    'esp': ''}
    
"""

#################################
#                               #           
#       Window: SETTINGS        #
#                               #
#################################

SET_WIN_TITLE = {'eng': 'OpenVoltam | Settings',
                'esp': 'OpenVoltam | Ajustes'}
SET_TITLE = {'eng': '<b>Settings</b>',
            'esp': '<b>Ajustes</b>'}
SET_LANG = {'eng': 'Language',
            'esp': 'Idioma'}
            
#################################
#                               #           
#       Window: WELCOME         #
#                               #
#################################

VERSION = "0.2"
RELEASE = {'eng': "September 5, 2026",
           'esp': '5 septiembre 2026'}
WEL_TITLE = {'eng': 'OpenVoltam',
            'esp': 'OpenVoltam'}
WEL_INFO = {'eng': "Welcome to <a href='https://github.com/ask53/openVoltam'>OpenVoltam</a>!<br><br>An open source project by <a href='https://www.caminosdeagua.org'>Caminos de Agua</a> and <a href='https://www.iorodeo.com'>IO Rodeo</a><br><br>Version: "+VERSION+"<br>Release: "+RELEASE['eng'],
            'esp': "Bienvenidx a <a href='https://github.com/ask53/openVoltam'>OpenVoltam</a>!<br><br>Un proyecto de fuente abierta creado por <a href='https://www.caminosdeagua.org'>Caminos de Agua</a> y <a href='https://www.iorodeo.com'>IO Rodeo</a><br><br>Versión: "+VERSION+"<br>Emitida: "+RELEASE['esp']}
WEL_SESH = {'eng': 'Lab session',
            'esp': 'Sesión de laboratorio'}
WEL_NEW_SESH = {'eng': 'New session',
            'esp': 'Sesión nueva'}
WEL_OPN_SESH = {'eng': 'Open session',
            'esp': 'Abrir sesión'}
WEL_METH = {'eng': 'Method',
            'esp': 'Método de voltametría'}
WEL_NEW_METH = {'eng': 'New method',
            'esp': 'Método nuevo'}
WEL_OPN_METH = {'eng': 'Open method',
            'esp': 'Abrir método'}
            

#################################
#                               #           
#       Window: MAIN            #
#                               #
#################################

# Menu bar: Lab session
MAI_MENU_TOP_SESH = {'eng': 'Lab session',
                     'esp': 'Sesión del lab'}
MAI_MENU_SESH_NEW = {'eng': 'New session',
                    'esp': 'Sesión nueva'}
MAI_MENU_SESH_OPN = {'eng': 'Open session',
                    'esp': 'Abrir sesión'}
MAI_MENU_SESH_SET = {'eng': 'Settings',
                    'esp': 'Ajustes'}
MAI_MENU_SESH_CLO = {'eng': 'Close',
                    'esp': 'Cerrar'}

# Menu bar: Method
MAI_MENU_TOP_METH = {'eng': 'Method',
                     'esp': 'Método'}
MAI_MENU_METH_NEW = {'eng': 'New method',
                    'esp': 'Método nuevo'}
MAI_MENU_METH_OPN = {'eng': 'Open method',
                    'esp': 'Abrir método'}
MAI_MENU_METH_RUN = {'eng': 'Edit run method',
                    'esp': 'Editar método usado'}

# Menu bar: Sample
MAI_MENU_TOP_SAMP = {'eng': 'Sample',
                     'esp': 'Muestra'}
MAI_MENU_SAMP_NEW = {'eng': 'New sample',
                    'esp': 'Muestra nueva'}
MAI_MENU_SAMP_EDI = {'eng': 'Edit sample info',
                    'esp': 'Editar muestra'}
MAI_MENU_SAMP_DEL = {'eng': 'Delete sample',
                    'esp': 'Borrar muestra'}

# Menu bar: Run
MAI_MENU_TOP_RUN = {'eng': 'Run',
                    'esp': 'Medición'}
MAI_MENU_RUN_NEW = {'eng': 'New run',
                    'esp': 'Medición nueva'}
MAI_MENU_RUN_FRO = {'eng': 'New run from config',
                    'esp': 'Medición nueva de anterior'}
MAI_MENU_RUN_RED = {'eng': 'Rerun',
                    'esp': 'Medir de nuevo'}
MAI_MENU_RUN_VIE = {'eng': 'Run info',
                    'esp': 'Detalles de la medición'}
MAI_MENU_RUN_INF = {'eng': 'Method info',
                    'esp': 'Detalles del método'}
MAI_MENU_RUN_NOT = {'eng': 'Edit rep note',
                    'esp': 'Editar nota del rep'}
MAI_MENU_RUN_EXP = {'eng': 'Export',
                    'esp': 'Exportar'}
MAI_MENU_RUN_DEL = {'eng': 'Delete',
                    'esp': 'Borrar'}

# Menu bar: Analysis
MAI_MENU_TOP_ANA = {'eng': 'Analysis',
                     'esp': 'Analizar'}
MAI_MENU_ANA_GRA = {'eng': 'Graph',
                    'esp': 'Visualizar'}
MAI_MENU_ANA_ANA = {'eng': 'Analyze',
                    'esp': 'Analizar'}
MAI_MENU_ANA_CAL = {'eng': 'Calculate',
                    'esp': 'Calcular'}
MAI_MENU_ANA_RES = {'eng': 'Results',
                    'esp': 'Resultados'}
     
# Right-click menu (only options not also available thru menu bar     
MAI_MENU_MOVE_TO = {'eng': 'Move to',
                    'esp': 'Mover a'}
                    
# Main window header buttons
MAI_BUT_SAMP = {'eng': 'New sample',
                'esp': 'Muestra nueva'}
MAI_BUT_RUN = {'eng': 'New run',
                'esp': 'Medición nueva'}                    
MAI_BUT_CALC = {'eng': 'Calculate',
                'esp': 'Calcular'}                    
MAI_BUT_RESU = {'eng': 'Results',
                'esp': 'Resultados'}

# Main window within tab-view: sample info pane
MAI_TAB_DATE = {'eng': 'Date collected',
                'esp': 'Fecha recolectada'}
MAI_TAB_LOCA = {'eng': 'Location',
                'esp': 'Ubicación'}
MAI_TAB_CONT = {'eng': 'Contact',
                'esp': 'Contacto'}
MAI_TAB_CLTR = {'eng': 'By',
                'esp': 'Por'}
MAI_TAB_NOTE = {'eng': 'Notes',
                'esp': 'Notas'}

                   






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
window_home = ['OpenVoltam','OpenVoltam']

# Menus
menu_sample = ['Sample','Muestra']
menu_config = ['Method','Método de voltametría']
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
s_edit_edit = ['Edit','Editar']
s_edit_cancel = ['Cancel','Cancelar']
s_edit_close_wo_save = ['Close without saving','Cerar sin guardar']
s_edit_discard = ['Discard changes?','¿Tirar cambios a la basura?']
e_edit_save_dialog = ['Are you sure you want to close without saving this sample?', "Favor de confirmar si quieres cerar sin guardar esta muestra."]

# Window: edit sweep configuration
c_edit_header_edit = ['Edit method: ', 'Editar los ajustes de voltametría']
c_edit_header_new = ['New method: ', 'Ajuste de voltametría nueva']
c_edit_header_view = ['View method: ', 'TEXTO']

# Window: main
s_view_info = ['View info','Ver datos']
s_edit_info = ['Edit info','Modificar datos']
r_rep_abbrev = ['Rep.', 'TEX']

# Window: run configuration
rc_window_title = ['Configure run','TEXTO']
rc_type_blank = ['Blank','TEXTO']
rc_type_sample = ['Sample','TEXTO']
rc_type_stdadd = ['Standard addition','TEXTO']
rc_select = ['Select...','TEXTO']
rc_types = {
    g.R_TYPE_BLANK: ['Blank','TEXTO'],
    g.R_TYPE_SAMPLE: ['Sample','TEXTO'],
    g.R_TYPE_STDADD: ['Standard Addition','TEXTO'],
    }

# Window: sweep profile builder/editer
sp_types = {
    g.M_CONSTANT: ['Voltage: constant','TEXTO'],
    g.M_RAMP: ['Voltage: ramp','TEXTO']
    }
sp_add_step = ['Add step','TEXTO']
sp_edit_step = ['Edit step','TEXTO']
sp_add_btn = ['Add','TEXTO']
sp_edit_btn = ['Apply edits','TEXTO']

# Window: run
r_window_title = ['Run viewer','TEXTO']



#Alerts
alert_header = ['Alert!', '¡Alerta!']
alert_s_edit_name = ['The name is too short.\nPlease enter a sample name that contains at least three characters.','El nombre es demaciado corto.\nFavor de ingresar un nombre de la muestra que contiene al menos tres carácteres.']
alert_s_edit_save_error = ['There was and issue saving the file, please try again.','Había un error en el proceso de guardar el archivo. Favor de intentar otra vez.']
# File system navigation
filetype_sample_lbl = ['OpenVoltam Sample', 'Muestra de OpenVoltam']
filetype_sp_lbl = ['OpenVoltam Profile', 'Perfíl de OpenVoltam']





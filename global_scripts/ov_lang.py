"""
lang.py

This is the language file. It contains all the translations of
OpenVoltam. All are downloaded together for all users.

To add new language/translation:

1. add a key: value pair to LANGS where the key is the name of 
the language in its own language/script and the value is a 
3-character string that will be the key to that language for 
all the rest of the dicts in this file.

2. Add that key to each of the dicts in this file along with
a translation of each string. Done!

"""

from global_scripts import ov_globals as g

LANGS = {'English': 'eng',
        'Español': 'esp'}
        
#################################
#                               #           
#           STATUS BAR          #
#                               #
#################################

# Export related text
SB_EXPORT_STRT = {'eng': 'Exporting...',
                  'esp': 'Exportando...'}
SB_EXPORT_GOOD = {'eng': 'Export complete',
                  'esp': 'Exportación exitosa'}
SB_EXPORT_WARN = {'eng': 'WARNING: Some reps could not be exported',
                  'esp': 'AVISO: Algunas mediciones no se lograron exportar'}
SB_EXPORT_ERRR = {'eng': 'ERROR: Export could not complete',
                  'esp': 'FALLO: La exportación no se logró'}

# Loading/reading related text
SB_LOAD_STRT = {'eng': 'Loading data...',
                'esp': 'Cargando datos...'} 
SB_LOAD_GOOD = {'eng': 'Data loaded',
                'esp': 'Datos cargados'} 
SB_LOAD_ERRR = {'eng': 'ERROR: Data could not be loaded',
                'esp': 'FALLO: Los datos no se lograron cargar'}

# Saving/writing releated text
SB_SAVE_STRT = {'eng': 'Saving...',
                'esp': 'Guardando...'} 
SB_SAVE_GOOD = {'eng': 'Saved',
                'esp': 'Guardada'} 
SB_SAVE_ERRR = {'eng': 'ERROR: Save could not complete',
                'esp': 'FALLO: No se logró guardar'} 
                
                
#################################
#                               #           
#      Multi-use: BUTTONS       #
#                               #
#################################

SAVE = {'eng': 'Save',
        'esp': 'Guardar'}
SAVE_AS = {'eng': 'Save as',
           'esp': 'Guardar como'}
EDIT = {'eng': 'Edit',
       'esp': 'Editar'}


#################################
#                               #           
#      Multi-use: DIALOGS       #
#                               #
#################################

# Popup dialog: Alert!
DIALOG_ALERT_TTL = {'eng': 'Alert!',
                    'esp': '¡Alerta!'}

# Popup dialog: Close without saving? 
DIALOG_DISC_TTL = {'eng': 'Discard changes?',
                   'esp': '¿Tirar los cambios?'}
DIALOG_DISC_MSG = {'eng': 'Close without saving?',
                   'esp': '¿Cerrar sin guardar los cambios?'}
DIALOG_DISC_BUT_SAVE = SAVE
DIALOG_DISC_BUT_DISC = {'eng': 'Close without saving',
                        'esp': 'Cerrar sin guardar'}
DIALOG_DISC_BUT_CNCL = {'eng': 'Canceñ',
                        'esp': 'Cancelar'}



#################################
#                               #           
#       Window: WELCOME         #
#                               #
#################################

WEL_TITLE = {'eng': 'OpenVoltam',
            'esp': 'OpenVoltam'}
WEL_INFO = {'eng': "Welcome to <a href='https://github.com/ask53/openVoltam'>OpenVoltam</a>!<br><br>An open source project by <a href='https://www.caminosdeagua.org'>Caminos de Agua</a> and <a href='https://www.iorodeo.com'>IO Rodeo</a><br><br>Version: "+g.VERSION+"<br>Release: "+g.RELEASE,
            'esp': "Bienvenidx a <a href='https://github.com/ask53/openVoltam'>OpenVoltam</a>!<br><br>Un proyecto de fuente abierta creado por <a href='https://www.caminosdeagua.org'>Caminos de Agua</a> y <a href='https://www.iorodeo.com'>IO Rodeo</a><br><br>Versión: "+g.VERSION+"<br>Emitida: "+g.RELEASE}
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
MAI_TAB_NOTE = {'eng': 'Note',
                'esp': 'Nota'}
                
# Main window within tab-view: rep column headers
MAI_TAB_COL_REPL = {'eng': 'Replicate',
                    'esp': 'Repetición'}
MAI_TAB_COL_STAT = {'eng': 'Status',
                    'esp': 'Estado'}
MAI_TAB_COL_DATE = {'eng': 'Last run',
                    'esp': 'Última medición'}
MAI_TAB_COL_NOTE = MAI_TAB_NOTE                   
MAI_TAB_COL_ANAL = {'eng': 'Analyzed',
                    'esp': 'Analizado'}
                    
# Main window within tab-view: titles within each run box
MAI_TAB_RUN_HEAD = MAI_MENU_TOP_RUN 
MAI_TAB_RUN_TYPE = {'eng': 'Type',
                    'esp': 'Tipo'}
MAI_TAB_RUN_METH = MAI_MENU_TOP_METH
MAI_TAB_RUN_NOTE = MAI_TAB_NOTE
RUN_TYPES = {
    g.R_TYPE_BLANK: {'eng': 'Blank',
                     'esp': 'Vacio'},
    g.R_TYPE_SAMPLE: {'eng': 'Sample',
                      'esp': 'Muestra'},
    g.R_TYPE_STDADD: {'eng': 'Standard addition',
                      'esp': 'Concentrato agregado'}}

# Main window within tab-view: rep rows
MAI_TAB_REP_HEAD = {'eng': 'Rep.',
                    'esp': 'Rep.'}
MAI_TAB_REP_STAT = {
    g.R_STATUS_PENDING: {'eng': 'Pending',
                         'esp': 'Pendiente'},
    g.R_STATUS_ERROR: {'eng': 'Error',
                       'esp': 'Fallo'},
    g.R_STATUS_COMPLETE: {'eng': 'Complete',
                          'esp': 'Hecho'}}

# Main window popups window: Close
MAI_POP_CLO_TIT = {'eng': 'Are you sure?',
                   'esp': 'Para confirmar...'}
MAI_POP_CLO_MSG = {'eng': 'This will close this sample and all associated windows including active runs, run configurations, and analysis. Unsaved progress will be lost.\n\nAre you sure you want to close?\n',
                   'esp': 'Esto cerrará la muestra y todas sus ventanas relacionadas incluso mediciones activas, configuraciones de mediciones y analisis. El trabajo no guardardo se perderá.\n\nFavor de confirmar.\n'} 
MAI_POP_BUT_CLO = {'eng': 'Close',
                   'esp': 'Cerrar'}
MAI_POP_BUT_CAN = DIALOG_DISC_BUT_CNCL

# Main window popups window: Export result popup
MAI_POP_EXP_TITL = SB_EXPORT_GOOD
MAI_POP_EXP_ERRR = {'eng': 'ERROR MESSAGE',
                    'esp': 'MENSAJE DEL FALLO'}
MAI_POP_EXP_MWRN = {'eng': 'Warning: Failed to export',
                    'esp': 'Aviso: Falló de exportar'}
MAI_POP_EXP_SUCS = {'eng': 'Successfully exported',
                    'esp': 'Exitos'}
MAI_POP_EXP_TWRN = {'eng': 'Warning: some replicates failed to export',
                    'esp': 'Aviso: no logró exportar todas las mediciones'}
MAI_POP_EXP_TERR = {'eng': 'ERROR on export',
                    'esp': 'FALLO en exportar'}


#################################
#                               #           
#       Window: SAMPLE          #
#                               #
#################################

SAM_TITLE = {
    g.WIN_MODE_NEW: {'eng': 'New sample',
                     'esp': 'Muestra nueva'},
    g.WIN_MODE_EDIT: {'eng': 'Edit sample',
                      'esp': 'Editar muestra'}}
                      
SAM_NAM = {'eng': 'Sample name',
           'esp': 'Nombre de la muestra'}
SAM_DAT = {'eng': 'Date collected',
           'esp': 'Fecha recolectado'}
SAM_LOC = {'eng': 'Location collected',
           'esp': 'Ubicación recolectado'}
SAM_CON = {'eng': 'Contact',
           'esp': 'Contacto'}
SAM_WHO = {'eng': 'Collected by',
           'esp': 'Recolectado por'}
SAM_NOT = {'eng': 'Notes',
           'esp': 'Notas'}
    
# Sample window-specific popup validation messages    
SAM_VALID_MSG = {'eng': 'The name is too short.\nPlease enter a sample name that contains at least three characters.',
                 'esp': 'El nombre es demaciado corto.\nFavor de ingresar un nombre de la muestra que contenga al menos tres carácteres.'}
          

#################################
#                               #           
#  Window: Results View (Graph) #
#                               #
#################################

RVW_HEAD = {'eng': 'Results viewer',
            'esp': 'Ver resultados'}
            

#################################
#                               #           
#       Window: Analyze         #
#                               #
#################################

ANA_HEAD = {'eng': 'Analyze',
            'esp': 'Analizar'}
ANA_TITL = {'eng': 'Runs to analyze:',
            'esp': 'Mediciones para analizar:'}
ANA_HELP = {'eng': "Press 'z' on the keyboard to toggle between baseline endpoints.",
            'esp': "Omprimir la 'z' en el teclado para cambiar entre los puntos extremos."}
ANA_RLTS =  {'eng': 'Show results',
             'esp': 'Mostrar resultados'}
ANA_CPLT =  {'eng': 'Complete',
             'esp': 'Hecho'}
       
ANA_RUN_ABRV = {'eng': 'Run-',
                'esp': 'Med-'}
ANA_REP_ABRV = {'eng': 'Rep-',
                'esp': 'Rep-'}

ANA_BUT_NEXT = {'eng': 'Accept && next',
                'esp': 'Aceptar y seguir'}
ANA_BUT_SAVE = {'eng': 'Save all',
                'esp': 'Guardar todo'}

ANA_C_TYPES = {
    g.C_TYPE_PEAKBASE: {'eng': 'Peak ht (from base)',
                        'esp': 'Altura (de la base)'}, 
    g.C_TYPE_PEAKZERO: {'eng': 'Peak ht (from 0)',
                        'esp': 'Altura (de 0)'}, 
    g.C_TYPE_SLOPE_L: {'eng': 'Deriv (L)',
                       'esp': 'Deriv (izq.)'}, 
    g.C_TYPE_SLOPE_R: {'eng': 'Deriv (R)',
                       'esp': 'Deriv (der.)'}, 
    g.C_TYPE_SLOPE_AVG: {'eng': 'Deriv (avg)',
                         'esp': 'Deriv (prom.)'}, 
    g.C_TYPE_AREA: {'eng': 'Area',
                    'esp': 'Área'}}
                  
                  
#################################
#                               #           
#       Window: Run Config      #
#                               #
#################################

RCF_SAMP = {'eng': 'Sample',
            'esp': 'Muestra'}
RCF_METH = {'eng': 'Method',
            'esp': 'Método'}
RCF_LOAD = {'eng': 'Load from file',
            'esp': 'Cargar de archivo'}
RCF_DEVC = {'eng': 'Device',
            'esp': 'Dispositivo'}
RCF_TYPE = {'eng': 'Run type',
            'esp': 'Tipo de medición'}
RCF_REPS = {'eng': 'Repeats',
            'esp': 'Repeticiones'}
RCF_VMTH = {'eng': 'View method details',
            'esp': 'Ver detalles del método'}
RCF_NOTE = {'eng': 'Notes',
            'esp': 'Notas'}
RCF_VSPL = {'eng': 'Sample volume [mL]',
            'esp': 'Volumen de la muestra [mL]'}
RCF_VTOT = {'eng': 'Total volume [mL]',
            'esp': 'Volumen total [mL]'}
RCF_GSMP = {'eng': 'Sample parameters',
            'esp': 'Parámetros de la muestra'}
RCF_VSTD = {'eng': 'Volume standard added [uL]',
            'esp': 'Volumen de concentrato agregado [uL]'}
RCF_GSTD = {'eng': 'Standard addition parameters',
            'esp': 'Parámetros del concentrato agregado '}
RCF_BNEW = {'eng': 'Ready to run!',
            'esp': '¡Listo para medir!'}
RCF_BEDT = {'eng': 'Save changes',
            'esp': 'Guardar'}
RCF_BVIE = {'eng': 'Edit configs',
            'esp': 'Editar'}
RCF_SLCT = {'eng': 'Select...',
            'esp': 'Selecionar...'}
            
            
   

#################################
#                               #           
#       Embed: Voltamogram      #
#                               #
#################################

VGM_XLBL = {'eng': 'Voltage [V]',
            'esp': 'Voltaje [V]'}
VGM_YLBL = {'eng': 'Current [uA]',
            'esp': 'Corriente [uA]'}
VGM_RUN_ABRV = ANA_RUN_ABRV
VGM_REP_ABRV = ANA_REP_ABRV

 
           
            


























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
#alert_s_edit_save_error = ['There was and issue saving the file, please try again.','Había un error en el proceso de guardar el archivo. Favor de intentar otra vez.']
# File system navigation
filetype_sample_lbl = ['OpenVoltam Sample', 'Muestra de OpenVoltam']
filetype_sp_lbl = ['OpenVoltam Profile', 'Perfíl de OpenVoltam']





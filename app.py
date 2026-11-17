"""Sistema de consulta escolar privado – I. E. N.° 82641 Simón Bolívar."""
import hashlib
import hmac
import html
import io
import re
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from cryptography.fernet import InvalidToken
from data_utils import decrypt_frame, encrypt_frame, parse_books, norm, FIELDS

st.set_page_config(page_title='Sistema Educativo | Simón Bolívar',page_icon='🏫',layout='wide',initial_sidebar_state='collapsed')
ROOT=Path(__file__).resolve().parent
LOGO=ROOT/'logo.png'
BASE=ROOT/'matricula_2026.enc'
NAV=['🔎 Estudiantes','👨‍👩‍👧 Familias','📋 Ratificación','🧾 Recibos / APAFA','📊 Estadísticas','📥 Reportes','✅ Calidad','🔄 Actualizar bases']

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap');
html,body,.stApp{font-family:'DM Sans',sans-serif}
h1,h2,h3{font-family:'Outfit',sans-serif!important}
[data-testid="stAppViewContainer"]{background:linear-gradient(180deg,#F7FAFD,#EDF4F9);color:#173D59}
.block-container{max-width:1520px;padding-top:1.4rem;padding-bottom:3rem}
.school-heading{background:linear-gradient(115deg,#104764,#087F9C 78%,#098FA9);color:#FFFFFF;padding:22px 27px;border-radius:19px;margin-bottom:15px;box-shadow:0 12px 30px rgba(12,72,104,.15);border-bottom:5px solid #EBB829}
.school-heading h1{font-size:clamp(22px,3vw,31px);color:#FFFFFF;margin:2px 0}.school-heading p{color:#E6F6FB;margin:0;font-size:14px}
.school-heading .tag{color:#FFDC66;letter-spacing:1.4px;font-size:11px;font-weight:800}
[data-testid="stMetric"]{background:white;padding:17px;border:1px solid #DBEAF2;border-radius:13px;box-shadow:0 3px 14px #0A55780B}
[data-testid="stMetricValue"]{color:#0F516D}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:6px;overflow-x:auto;padding:5px 2px 9px}
[data-testid="stTabs"] button[data-baseweb="tab"]{background:#FFFFFF;border:1px solid #DCE9F2;border-radius:9px;color:#164762;white-space:nowrap;font-weight:650;padding:10px 12px}
[data-testid="stTabs"] button[aria-selected="true"]{background:#E4F4FA;border:1px solid #087F9C;color:#076E8E}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:#E6B525}
.stButton button[kind="primary"],.stFormSubmitButton button[kind="primary"]{background:#0E7998!important;color:#FFFFFF!important;border:none!important;font-weight:700!important;border-radius:10px!important}
.stButton button[kind="primary"]:hover,.stFormSubmitButton button[kind="primary"]:hover{background:#106583!important}
[data-testid="stForm"]{background:#FFFFFF;border:1px solid #DCE9F0;border-radius:17px;padding:20px}
.login-tag{text-align:center;font-size:11px;font-weight:800;letter-spacing:2px;color:#A87913;margin-top:6px}
.login-title{text-align:center;color:#125071;font-size:clamp(24px,3vw,34px);font-weight:800;margin:10px 0}
.login-sub{text-align:center;color:#587387;font-size:14px;margin-bottom:20px}
.login-badge{margin:0 auto;width:105px;height:105px;border-radius:50%;background:#145170;border:4px solid #E8B928;display:flex;align-items:center;justify-content:center;font-size:48px}
.notice{background:#E8F5FA;border-left:4px solid #0986A5;padding:12px 16px;border-radius:8px;color:#21556B}
.tiny{color:#688195;font-size:12px}
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden}
</style>''',unsafe_allow_html=True)

def clean(s): return str(s or '').strip()
def safe(s):return html.escape(clean(s))
def search(s):return re.sub(r'[^a-z0-9]+',' ',norm(s)).strip()
def number(s):return re.sub(r'\D','',clean(s))
def val(s):return clean(s) or 'No consignado'

def get_auth():
    try:return st.secrets['auth'],st.secrets['data']['fernet_key']
    except Exception:
        st.error('Configura [auth] y [data] en Secrets de Streamlit antes de iniciar.');st.stop()

auth,key=get_auth()
if 'logged' not in st.session_state:st.session_state.logged=False
if 'attempts' not in st.session_state:st.session_state.attempts=0

if not st.session_state.logged:
    st.markdown('''<style>[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none!important}.block-container{max-width:950px;padding-top:2rem}</style>''',unsafe_allow_html=True)
    _,mid,_=st.columns([1,1.16,1])
    with mid:
        if LOGO.exists():
            _,logo_col,_=st.columns([1,0.75,1])
            with logo_col:st.image(str(LOGO),use_container_width=True)
        else:st.markdown('<div class="login-badge">🏫</div>',unsafe_allow_html=True)
        st.markdown('<div class="login-tag">PLATAFORMA DE USO EXCLUSIVO · DIRECCIÓN</div>',unsafe_allow_html=True)
        st.markdown('<div class="login-title">Sistema Educativo<br>Simón Bolívar</div>',unsafe_allow_html=True)
        st.markdown('<div class="login-sub"><b>I. E. N.° 82641 · Cajamarca, Perú</b><br>Gestión privada de matrícula, familias y estudiantes</div>',unsafe_allow_html=True)
        with st.form('login'):
            st.subheader('🔐 Acceso al sistema')
            user=st.text_input('Usuario',placeholder='Escriba su usuario')
            pwd=st.text_input('Contraseña',type='password',placeholder='Escriba su contraseña')
            submitted=st.form_submit_button('Ingresar al sistema',use_container_width=True,type='primary')
        if submitted:
            if st.session_state.attempts>=8:
                st.error('Límite de intentos alcanzado en esta sesión. Contacte al administrador.')
            else:
                try:
                    digest=hashlib.pbkdf2_hmac('sha256',pwd.encode(),bytes.fromhex(str(auth['password_salt'])),int(auth['iterations'])).hex()
                    valid_user=hmac.compare_digest(user.strip(),str(auth['username']))
                    valid_pass=hmac.compare_digest(digest,str(auth['password_hash']))
                except (KeyError,ValueError):
                    st.error('Configuración de autenticación incorrecta.');st.stop()
                if valid_user and valid_pass:
                    st.session_state.logged=True;st.session_state.attempts=0;st.rerun()
                else:
                    st.session_state.attempts+=1;st.error('Usuario o contraseña incorrectos.')
        st.caption('🔒 Acceso exclusivo del personal autorizado. Cierre sesión al terminar.')
    st.stop()

@st.cache_data(show_spinner=False,ttl=1800)
def cached_load(blob,key):return decrypt_frame(blob,key)
try:db=cached_load(BASE.read_bytes(),key)
except (InvalidToken,ValueError,FileNotFoundError,KeyError) as e:
    st.error('No se pudo leer la base cifrada. Confirme la clave en Secrets y que exista matricula_2026.enc.');st.stop()

# Los archivos cifrados antiguos no tenían estos campos: rellenar sin inventar datos.
for column in FIELDS:
    if column not in db.columns:db[column]=''
db=db.fillna('')
if db['ratificacion'].eq('').all():db['ratificacion']='Por verificar'

head_left,head_right=st.columns([9,1.35],vertical_alignment='center')
with head_left:
    a,b=st.columns([0.65,8],vertical_alignment='center')
    with a:
        if LOGO.exists():st.image(str(LOGO),use_container_width=True)
        else:st.markdown('## 🏫')
    with b:
        st.markdown('<div class="school-heading"><div class="tag">I. E. N.° 82641 · CAJAMARCA</div><h1>Sistema Educativo Simón Bolívar</h1><p>Panel privado de Dirección · Matrícula y ratificación 2026</p></div>',unsafe_allow_html=True)
with head_right:
    if st.button('🚪 Cerrar sesión',use_container_width=True):
        st.session_state.logged=False;st.session_state.pop('consulta',None);st.rerun()

st.caption('Los registros son los que figuran en las planillas recibidas; “Por verificar” no significa matrícula confirmada ni pendiente oficialmente.')

# La barra de navegación es HORIZONTAL y desplazable si la pantalla es pequeña.
tabs=st.tabs(NAV)

def filters(frame,prefix):
    a,b=st.columns(2)
    with a:level=st.selectbox('Nivel',['Todos','Primaria','Secundaria'],key=f'{prefix}_nivel')
    sub=frame if level=='Todos' else frame[frame['nivel']==level]
    with b:section=st.selectbox('Grado / sección',['Todos']+sorted(sub['seccion'].dropna().unique().tolist()),key=f'{prefix}_seccion')
    return sub if section=='Todos' else sub[sub['seccion']==section]

def student_card(r):
    with st.expander(f"🎓 {val(r['alumno'])} · {r['nivel']} {r['seccion']}"):
        p,m=st.columns(2)
        p.write('**DNI estudiante:** '+val(r['dni_alumno']))
        p.write('**Padre:** '+val(r['padre']))
        p.write('**Madre:** '+val(r['madre']))
        p.write('**Situación final consignada:** '+val(r['situacion_final']))
        m.write('**DNI responsable:** '+val(r['dni_responsable']))
        m.write('**Tipo responsable:** '+val(r['tipo_responsable']))
        m.write('**Celular:** '+val(r['celular']))
        m.write('**Domicilio:** '+val(r['domicilio']))
        if clean(r['observaciones']):st.write('**Observaciones:** '+clean(r['observaciones']))
        st.caption('Fuente: '+val(r['origen'])+' · Fila: '+val(r['fila_origen']))

def match_rows(frame,q,columns):
    q=search(q)
    if len(q)<2:return frame.iloc[0:0]
    return frame[frame.apply(lambda r:any(q in search(r[c]) for c in columns),axis=1)]

with tabs[0]:
    st.subheader('🔎 Buscar estudiantes')
    x=filters(db,'alumnos')
    query=st.text_input('Nombre, apellido o DNI de estudiante',placeholder='Escribe al menos 2 caracteres',key='consulta')
    if len(search(query))<2:st.info('Escribe un nombre o DNI para consultar una ficha.')
    else:
        found=match_rows(x,query,['alumno','dni_alumno'])
        st.write(f'**{len(found)} resultado(s)**')
        for _,record in found.head(70).iterrows():student_card(record)
        if len(found)>70:st.warning('Hay más de 70 resultados. Escribe más caracteres.')

with tabs[1]:
    st.subheader('👨‍👩‍👧 Padres, madres, responsables y hermanos')
    x=filters(db,'familias')
    q=st.text_input('Buscar nombre o DNI del padre, madre o responsable',key='fquery')
    if len(search(q))<2:st.info('Busca por nombres del padre o madre, o por DNI del responsable de matrícula.')
    else:
        matches=match_rows(x,q,['padre','madre','dni_responsable'])
        st.write(f'**{len(matches)} ficha(s) coincidente(s)**')
        groups={}
        for _,r in matches.iterrows():
            for role,col in [('Padre','padre'),('Madre','madre')]:
                name=clean(r[col])
                if not name or norm(name) in {'no tiene','no consigna','fallecido','s/n','no cuenta'}:continue
                by_name=search(q) in search(name)
                by_dni=number(q) and (number(q) in number(r['dni_responsable'])) and r['tipo_responsable']==role.lower()
                if by_name or by_dni:groups[(role,search(name))]=(role,name,col)
        for (_k,(_role,name,col)) in list(groups.items())[:60]:
            children=x[x[col].map(search)==search(name)].drop_duplicates(subset=['nivel','seccion','alumno'])
            st.markdown(f'#### 👤 {safe(name)} · {_role} · {len(children)} alumno(s) asociado(s)')
            for _,r in children.iterrows():
                st.markdown(f"- **{safe(r['alumno'])}** — {safe(r['nivel'])} · {safe(r['seccion'])} · DNI: {safe(val(r['dni_alumno']))}")
        # Un DNI de apoderado puede existir sin relación especificada como padre/madre.
        direct=matches[matches['dni_responsable'].map(lambda v:number(q) in number(v) if number(q) else False)]
        if not direct.empty:
            st.markdown('#### 📇 Fichas asociadas al DNI del responsable')
            for _,r in direct.head(30).iterrows():student_card(r)
        st.caption('Las relaciones por nombre no prueban parentesco único: homónimos pueden aparecer juntos. Verificar antes de utilizarlas.')

with tabs[2]:
    st.subheader('📋 Ratificación y situación de matrícula')
    x=filters(db,'rati')
    st.info('Este módulo consulta fichas y situaciones finales consignadas. Si no existe una confirmación explícita de ratificación, figura “Por verificar”.')
    c1,c2,c3=st.columns(3)
    c1.metric('Fichas en selección',len(x))
    c2.metric('Con situación final',int(x['situacion_final'].astype(str).str.strip().ne('').sum()))
    c3.metric('Por verificar',int(x['ratificacion'].eq('Por verificar').sum()))
    q=st.text_input('Filtrar por estudiante, situación u observación',key='ratiquery')
    view=match_rows(x,q,['alumno','dni_alumno','situacion_final','observaciones']) if q.strip() else x
    cols=['nivel','seccion','alumno','dni_alumno','situacion_final','ratificacion','observaciones']
    st.dataframe(view[cols].rename(columns={'nivel':'Nivel','seccion':'Aula','alumno':'Estudiante','dni_alumno':'DNI','situacion_final':'Situación final (Excel)','ratificacion':'Ratificación (verificación)','observaciones':'Observaciones'}),hide_index=True,use_container_width=True,height=480)

with tabs[3]:
    st.subheader('🧾 Recibos, montos y APAFA')
    x=filters(db,'apafa')
    st.warning('Un monto o recibo consignado no confirma por sí solo que un pago se haya realizado o conciliado.')
    c1,c2=st.columns(2)
    c1.metric('Fichas con dato de recibo',int(x['recibo'].astype(str).str.strip().ne('').sum()))
    c2.metric('Fichas con dato de monto / APAFA',int(x['monto'].astype(str).str.strip().ne('').sum()))
    q=st.text_input('Buscar recibo, nombre o DNI',key='recquery')
    view=match_rows(x,q,['recibo','alumno','dni_alumno']) if q.strip() else x
    cols=['nivel','seccion','alumno','recibo','monto','observaciones']
    st.dataframe(view[cols].rename(columns={'nivel':'Nivel','seccion':'Aula','alumno':'Estudiante','recibo':'Recibo consignado','monto':'Monto / APAFA consignado','observaciones':'Observaciones'}),hide_index=True,use_container_width=True,height=470)

with tabs[4]:
    st.subheader('📊 Estadísticas institucionales')
    x=filters(db,'estad')
    m1,m2,m3=st.columns(3)
    m1.metric('Fichas de alumnos',len(x))
    m2.metric('Aulas registradas',x[['nivel','seccion']].drop_duplicates().shape[0])
    m3.metric('Con DNI alumno',int(x['dni_alumno'].astype(str).str.fullmatch(r'\d{8}').sum()))
    counts=x.groupby(['nivel','seccion'],as_index=False).size().rename(columns={'size':'Estudiantes'})
    if len(counts):
        chart=px.bar(counts,x='seccion',y='Estudiantes',color='nivel',barmode='group',text='Estudiantes',color_discrete_map={'Primaria':'#0787A9','Secundaria':'#E7B528'})
        chart.update_layout(height=420,plot_bgcolor='white',paper_bgcolor='white',xaxis_title='Grado y sección')
        st.plotly_chart(chart,use_container_width=True)
    st.dataframe(counts,hide_index=True,use_container_width=True)
    st.caption('Cifras de fichas procesadas; no representan necesariamente matrícula validada oficialmente.')

with tabs[5]:
    st.subheader('📥 Reportes de Dirección')
    st.warning('Los reportes incluyen datos personales. Descárgalos solamente en equipos autorizados y protégelos al compartir.')
    x=filters(db,'report')
    type_=st.selectbox('Contenido del reporte',['Resumen por aula','Fichas de matrícula','Control de ratificación','Registros de recibos'])
    if type_=='Resumen por aula':
        report=x.groupby(['nivel','seccion'],as_index=False).size().rename(columns={'size':'Fichas'})
    elif type_=='Control de ratificación':report=x[['nivel','seccion','alumno','dni_alumno','situacion_final','ratificacion','observaciones']]
    elif type_=='Registros de recibos':report=x[['nivel','seccion','alumno','recibo','monto','observaciones']]
    else:report=x[[c for c in FIELDS if c in x.columns]]
    st.dataframe(report.head(300),use_container_width=True,hide_index=True)
    st.download_button('⬇️ Descargar CSV (compatible con Excel)',data=report.to_csv(index=False).encode('utf-8-sig'),file_name='reporte_direccion_2026.csv',mime='text/csv',use_container_width=True)

with tabs[6]:
    st.subheader('✅ Control de datos incompletos')
    x=filters(db,'calidad')
    a,b,c=st.columns(3)
    a.metric('Sin DNI alumno válido',int((~x['dni_alumno'].astype(str).str.fullmatch(r'\d{8}')).sum()))
    b.metric('Sin DNI responsable válido',int((~x['dni_responsable'].astype(str).str.fullmatch(r'\d{8}')).sum()))
    c.metric('Sin celular',int(x['celular'].astype(str).str.strip().eq('').sum()))
    failures=x[(~x['dni_alumno'].astype(str).str.fullmatch(r'\d{8}')) | (~x['dni_responsable'].astype(str).str.fullmatch(r'\d{8}')) | x['celular'].astype(str).str.strip().eq('')]
    st.dataframe(failures[['nivel','seccion','alumno','dni_alumno','dni_responsable','celular']],hide_index=True,use_container_width=True,height=420)
    st.caption('Los datos faltantes o ambiguos se dejan sin completar; la corrección se hace en los Excel originales.')

with tabs[7]:
    st.subheader('🔄 Actualizar bases de matrícula')
    st.markdown('''<div class="notice">Sube los tres Excel más recientes, revisa la cantidad de fichas y descarga la nueva base cifrada. Luego reemplaza <b>solo matricula_2026.enc</b> en el repositorio privado de GitHub; la página se actualizará sin cambiar su código.</div>''',unsafe_allow_html=True)
    st.write('Se admiten los Excel de primaria, 1.° de secundaria y 2.°–5.° de secundaria. Para reconocer primaria, su archivo debe incluir la palabra **PRIMARIA** en el nombre.')
    uploads=st.file_uploader('Selecciona los tres archivos Excel (.xlsx)',type=['xlsx'],accept_multiple_files=True,key='upfiles')
    if uploads:
        if len(uploads)!=3:st.warning('Selecciona los tres archivos para no reemplazar accidentalmente una parte de la matrícula.')
        else:
            try:
                current=[(f.name,f.getvalue()) for f in uploads]
                has_primary=sum('primaria' in norm(name) for name,_ in current)
                has_first=sum('secundaria' in norm(name) and ('1' in name or '1°' in name) for name,_ in current)
                if has_primary!=1:st.error('No se distingue un único archivo de PRIMARIA. Revisa los nombres antes de continuar.')
                else:
                    with st.spinner('Analizando las fichas…'):
                        new,warnings=parse_books(current)
                    st.success(f'Lectura completada: {len(new)} fichas en {new[["nivel","seccion"]].drop_duplicates().shape[0]} aulas.')
                    current_rooms=set(zip(db['nivel'],db['seccion']))
                    new_rooms=set(zip(new['nivel'],new['seccion']))
                    if len(new)<len(db)*0.75 or len(new_rooms)<len(current_rooms)*0.75:
                        st.error('La nueva carga tiene muchas menos fichas o aulas que la base actual. Revisa los archivos antes de reemplazarla.')
                    else:
                        st.dataframe(new.groupby(['nivel','seccion']).size().rename('Fichas').reset_index(),hide_index=True,use_container_width=True)
                        if warnings:
                            st.warning('Advertencias de lectura: '+'; '.join(warnings[:8]))
                        st.caption('Revisa la vista previa. Al cargar un archivo nuevo se reemplaza el conjunto completo, no se mezclan las matrículas antiguas.')
                        encrypted=encrypt_frame(new,key)
                        st.download_button('🔐 Descargar matricula_2026.enc actualizado',data=encrypted,file_name='matricula_2026.enc',mime='application/octet-stream',type='primary',use_container_width=True)
            except Exception:
                st.error('No se pudo interpretar una de las hojas. Verifica el formato y consulta al administrador; no se modificó la base actual.')
    st.caption('Nunca subas a GitHub los Excel originales ni el archivo de contraseñas. Mantén el repositorio y la aplicación privados.')

st.divider()
st.caption('I. E. N.° 82641 Simón Bolívar · Sistema privado de Dirección · Datos escolares para uso autorizado · Matrícula 2026')

import os
import json
import csv
from pathlib import Path
from itertools import product

# Carpeta donde se guardarán los CSVs
csv_folder = Path('csv_output')
csv_folder.mkdir(exist_ok=True)

json_folder = Path('.')
token_file = Path('token.json')

# ========== BOOTSTRAP: Crear CSVs requeridos si no existen (excepto catálogos estáticos) ==========
# Definir los encabezados mínimos para los CSVs requeridos
bootstrap_csvs = {
    'token_directory.csv': ['id', 'token', 'token_name', 'namespace_name'],
    'usage_directory.csv': ['id', 'usage'],
    'image_directory.csv': ['id', 'image_name'],
    'path_directory.csv': ['id', 'volume_path'],
    'project_directory.csv': ['id', 'project_name', 'project_acronym'],
    'appname_directory.csv': ['id', 'app'],
    'app_directory.csv': ['id', 'id_appname', 'repo_name', 'repo_url'],
    'env_directory.csv': ['id', 'env', 'reponexus'],
    'country_directory.csv': ['id', 'country'],
    'label_directory.csv': ['id', 'app_label'],
    'app_type_directory.csv': ['id', 'app_type'],
    'runtime_directory.csv': ['id', 'runtime_name', 'version_path'],
    'person_in_charge.csv': ['id', 'nombre', 'email'],
    'security_champion.csv': ['id', 'nombre', 'email'],
    'microservice_properties_directory.csv': ['id','id_usage_directory','cpulimits','cpurequest','memorylimits','memoryrequest','replicas','id_token_directory','id_openshift_properties_directory','id_path_directory','id_image_directory','id_drs_config'],
    'microservice_drs_config.csv': ['id', 'drs_enabled', 'drs_token', 'drs_namespace'],
    'app_general_properties.csv': ['id','id_project_directory','id_app_directory','id_person_in_charge','id_security_champion','id_env_directory','id_country_directory','id_label_directory','id_app_type_directory','id_pipeline_properties_directory','id_pipeline_general_properties_directory','id_runtime_directory','sonarqubepath_exec','id_microservice_directory','id_datastage_properties_directory','id_database_properties_directory','id_was_properties_directory','id_pims_properties_directory','project_name','appName','repositoryUrl','buildConfigurationMode','env','country','ocpLabel','project','baseImageVersion'],
    'datastage_properties_directory.csv': ['id'],
    'database_properties_directory.csv': ['id'],
    'was_properties_directory.csv': ['id', 'host', 'instance_name', 'context_root'],
    'pims_properties_directory.csv': ['id', 'nexus_url'],
}
for fname, headers in bootstrap_csvs.items():
    fpath = csv_folder / fname
    if not fpath.exists():
        with open(fpath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

# Cargar tokens
with open(token_file, 'r', encoding='utf-8') as f:
    token_map = json.load(f)

general_rows = []
microservice_rows = []
ms_id_counter = 1
ms_id_map = {}  # (source_file, project_name, appName, env) -> id

# Diccionarios para mapear valores a IDs únicos por tabla
project_id_map = {}
appname_id_map = {}
app_dir_id_map = {}
env_id_map = {}
country_id_map = {}
label_id_map = {}
usage_id_map = {}
token_id_map = {}
path_id_map = {}

project_counter = appname_counter = app_dir_counter = env_counter = country_counter = label_counter = usage_counter = path_counter = 1

def get_token_key(token_name, env):
    if env == 'dev':
        token_env = 'dev'
    elif env == 'qa':
        token_env = 'uat'
    elif env == 'master':
        token_env = 'prd'
    token_env_name = f"{token_name}{token_env}"
    for k in token_map.keys():
        if k.lower() == token_env_name.lower():
            return k, token_map[k]
    return '', ''

def get_or_create_id(mapping, value, counter_name):
    global_vars = globals()
    if value not in mapping:
        mapping[value] = global_vars[counter_name]
        global_vars[counter_name] += 1
    return mapping[value]

def get_key_insensitive(d, key):
    for k in d.keys():
        if k.lower() == key.lower():
            return d[k]
    return [] if key in ['secrets','configMaps','volumes'] else None

# Construir token_id_map para búsqueda rápida de id_token_directory
with open(csv_folder / 'token_directory.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        token_id_map[(row['token'], row['token_name'])] = int(row['id'])

# ========== GENERAR TODAS LAS COMBINACIONES PARA openshift_properties_directory.csv ==========
from itertools import product
openshift_fields = ['secrets_enabled', 'configmap_enabled', 'volume_enabled']
openshift_combinations = list(product([True, False], repeat=3))
openshift_rows = []
for idx, combo in enumerate(openshift_combinations, 1):
    row = {'id': idx}
    for i, field in enumerate(openshift_fields):
        row[field] = combo[i]
    openshift_rows.append(row)
with open(csv_folder / 'openshift_properties_directory.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id'] + openshift_fields)
    writer.writeheader()
    writer.writerows(openshift_rows)
# Leer combinaciones predefinidas de openshift_properties_directory.csv
openshift_map = {}
with open(csv_folder / 'openshift_properties_directory.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (row['secrets_enabled'] == 'True', row['configmap_enabled'] == 'True', row['volume_enabled'] == 'True')
        openshift_map[key] = int(row['id'])

# Leer combinaciones predefinidas de pipeline_properties_directory.csv
pipeline_map = {}
pipeline_csv_path = csv_folder / 'pipeline_properties_directory.csv'
if pipeline_csv_path.exists():
    with open(pipeline_csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (
                row['securitygate'] == 'True',
                row['unittests'] == 'True',
                row['sonarqube'] == 'True',
                row['qualitygate'] == 'True',
            )
            pipeline_map[key] = int(row['id'])
else:
    print('⚠️ pipeline_properties_directory.csv no existe. Debe estar predefinido.')

# ========== BOOTSTRAP: Crear CSVs requeridos si no existen (excepto catálogos estáticos) ==========
# Definir los encabezados mínimos para los CSVs requeridos
bootstrap_csvs = {
    'token_directory.csv': ['id', 'token', 'token_name', 'namespace_name'],
    'usage_directory.csv': ['id', 'usage'],
    'image_directory.csv': ['id', 'image_name'],
    'path_directory.csv': ['id', 'volume_path'],
    'project_directory.csv': ['id', 'project_name', 'project_acronym'],
    'appname_directory.csv': ['id', 'app'],
    'app_directory.csv': ['id', 'id_appname', 'repo_name', 'repo_url'],
    'env_directory.csv': ['id', 'env', 'reponexus'],
    'country_directory.csv': ['id', 'country'],
    'label_directory.csv': ['id', 'app_label'],
    'app_type_directory.csv': ['id', 'app_type'],
    'runtime_directory.csv': ['id', 'runtime_name', 'version_path'],
    'person_in_charge.csv': ['id', 'nombre', 'email'],
    'security_champion.csv': ['id', 'nombre', 'email'],
    'microservice_properties_directory.csv': ['id','id_usage_directory','cpulimits','cpurequest','memorylimits','memoryrequest','replicas','id_token_directory','id_openshift_properties_directory','id_path_directory','id_image_directory','id_drs_config'],
    'microservice_drs_config.csv': ['id', 'drs_enabled', 'drs_token', 'drs_namespace'],
    'app_general_properties.csv': ['id','id_project_directory','id_app_directory','id_person_in_charge','id_security_champion','id_env_directory','id_country_directory','id_label_directory','id_app_type_directory','id_pipeline_properties_directory','id_pipeline_general_properties_directory','id_runtime_directory','sonarqubepath_exec','id_microservice_directory','id_datastage_properties_directory','id_database_properties_directory','id_was_properties_directory','id_pims_properties_directory','project_name','appName','repositoryUrl','buildConfigurationMode','env','country','ocpLabel','project','baseImageVersion'],
    'datastage_properties_directory.csv': ['id'],
    'database_properties_directory.csv': ['id'],
    'was_properties_directory.csv': ['id', 'host', 'instance_name', 'context_root'],
    'pims_properties_directory.csv': ['id', 'nexus_url'],
}
for fname, headers in bootstrap_csvs.items():
    fpath = csv_folder / fname
    if not fpath.exists():
        with open(fpath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

for filename in os.listdir(json_folder):
    if filename.endswith('.json') and filename != token_file.name:
        filepath = json_folder / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"⚠️ Error al leer {filename}: {e}")
                continue
        print(f"Procesando archivo: {filename}")
        projects = data.get('project') or data.get('projects') or []
        for project in projects:
            project_name = project.get('name', '')
            print(f"  Proyecto: {project_name}")
            for ms in project.get('ms', []):
                config = ms.get('config', {})
                app_name = ''
                if isinstance(config, str):
                    try:
                        config = json.loads(config)
                    except Exception:
                        config = {}
                if isinstance(config, dict):
                    app_name = config.get('appName', '')
                print(f"    Microservicio: {app_name}")
                appname_id = get_or_create_id(appname_id_map, app_name, 'appname_counter')
                repo_url = ms.get('repositoryUrl')
                app_dir_key = (appname_id, repo_url)
                if app_dir_key not in app_dir_id_map:
                    app_dir_id_map[app_dir_key] = app_dir_counter
                    app_dir_counter += 1
                app_dir_id = app_dir_id_map[app_dir_key]
                country = get_key_insensitive(config, 'country')
                country_id = get_or_create_id(country_id_map, country, 'country_counter')
                label = get_key_insensitive(config, 'ocpLabel')
                label_id = get_or_create_id(label_id_map, label, 'label_counter')
                # --- NUEVO: usage_directory ---
                usage = get_key_insensitive(config, 'usage')
                if not usage:
                    usage = 'internal'
                if usage not in usage_id_map:
                    usage_id_map[usage] = usage_counter
                    usage_counter += 1
                id_usage_directory = usage_id_map[usage]
                # Buscar claves de resQuotas insensible a mayúsculas/minúsculas
                def get_quota_key_insensitive(d, env):
                    for k in d.keys():
                        if k.lower() == f"resquotas{env}".lower():
                            return d[k]
                    return None
                for env in ['dev', 'qa', 'master']:
                    env_id = get_or_create_id(env_id_map, env, 'env_counter')
                    token_key_matched, token_value = get_token_key(ms.get('tokenOcp'), env)
                    # --- NUEVO: id_token_directory ---
                    id_token_directory = token_id_map.get((token_value, token_key_matched), '')
                    quotas = {
                        'dev': get_quota_key_insensitive(config, 'dev'),
                        'qa': get_quota_key_insensitive(config, 'qa'),
                        'master': get_quota_key_insensitive(config, 'master'),
                    }
                    if not quotas['dev'] and not quotas['qa'] and quotas['master']:
                        quotas['dev'] = quotas['qa'] = quotas['master']
                    elif quotas['dev'] and not quotas['qa'] and not quotas['master']:
                        quotas['qa'] = quotas['master'] = quotas['dev']
                    env_quota = quotas.get(env)
                    if env_quota:
                        quota_item = env_quota[0] if isinstance(env_quota, list) else env_quota
                        # --- AJUSTE: Si replicas no existe, ponerle 1 ---
                        replicas_value = quota_item.get('replicas')
                        if replicas_value is None:
                            replicas_value = 1
                        ms_key = (filename, project_name, app_name, env)
                        if ms_key not in ms_id_map:
                            ms_id_map[ms_key] = ms_id_counter
                            ms_id_counter += 1
                        ms_id = ms_id_map[ms_key]
                        # --- Buscar combinatoria en openshift_properties_directory predefinida ---
                        secrets_enabled = any(s.get('secret', False) for s in get_key_insensitive(config, 'secrets'))
                        configmap_enabled = any(c.get('configMap', False) for c in get_key_insensitive(config, 'configMaps'))
                        volume_enabled = any(v.get('volume', False) for v in get_key_insensitive(config, 'volumes'))
                        openshift_key = (secrets_enabled, configmap_enabled, volume_enabled)
                        id_openshift = openshift_map.get(openshift_key)
                        if id_openshift is None:
                            print(f"⚠️ Combinatoria {openshift_key} no encontrada en openshift_properties_directory.csv para {filename} {project_name} {app_name} {env}")
                            id_openshift = ''
                        # Extraer baseImageVersion para la imagen
                        base_image_version = get_key_insensitive(config, 'baseImageVersion')
                        # --- NUEVO: path_directory ---
                        # Buscar el primer mountPath de volumes (si existe)
                        volumes = get_key_insensitive(config, 'volumes')
                        volume_path = ''
                        if volumes and isinstance(volumes, list) and len(volumes) > 0:
                            volume_path = volumes[0].get('mountPath', '')
                        if volume_path not in path_id_map:
                            path_id_map[volume_path] = path_counter
                            path_counter += 1
                        id_path_directory = path_id_map[volume_path]
                        microservice_rows.append({
                            'id': ms_id,
                            'id_usage_directory': id_usage_directory,
                            'cpulimits': quota_item.get('cpuLimits'),
                            'cpurequest': quota_item.get('cpuRequest'),
                            'memorylimits': quota_item.get('memoryLimits'),
                            'memoryrequest': quota_item.get('memoryRequest'),
                            'replicas': replicas_value,
                            'id_token_directory': id_token_directory,
                            'id_openshift_properties_directory': id_openshift,
                            'id_path_directory': id_path_directory,
                            'drs_enabled': False,
                            'baseImageVersion': base_image_version
                        })
                        # app_general_properties row
                        general_rows.append({
                            'id_microservice_directory': ms_id,
                            'id_project_directory': project_id_map.get(project_name, ''),
                            'id_app_directory': app_dir_id,
                            'id_env_directory': env_id,
                            'id_country_directory': country_id,
                            'id_label_directory': label_id,
                            'project_name': project_name,
                            'appName': app_name,
                            'repositoryUrl': ms.get('repositoryUrl'),
                            'buildConfigurationMode': ms.get('buildConfigurationMode'),
                            'env': env,
                            'country': country,
                            'ocpLabel': label,
                            'project': get_key_insensitive(config, 'project'),
                            'baseImageVersion': get_key_insensitive(config, 'baseImageVersion'),
                        })

# ========== LÓGICA PARA id_image_directory usando baseImageVersion ========== 
image_id_map = {}
image_counter = 1
for row in microservice_rows:
    base_image_version = row.get('baseImageVersion', '')
    if base_image_version and base_image_version not in image_id_map:
        image_id_map[base_image_version] = image_counter
        image_counter += 1
    row['id_image_directory'] = image_id_map.get(base_image_version, '')

# Escribir image_directory.csv
image_rows = []
for name, id_ in image_id_map.items():
    image_rows.append({'id': id_, 'image_name': name})
with open(csv_folder / 'image_directory.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'image_name'])
    writer.writeheader()
    writer.writerows(image_rows)

# Escribir microservice_properties_directory.csv con el orden de columnas de la tabla SQL
ms_headers_sql = [
    'id',
    'id_usage_directory',
    'cpulimits',
    'cpurequest',
    'memorylimits',
    'memoryrequest',
    'replicas',
    'id_token_directory',
    'id_openshift_properties_directory',
    'id_path_directory',
    'id_image_directory',
]
filtered_microservice_rows = []
for r in microservice_rows:
    filtered_row = {k: r.get(k, '') for k in ms_headers_sql}
    filtered_microservice_rows.append(filtered_row)
with open(csv_folder / 'microservice_properties_directory.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=ms_headers_sql)
    writer.writeheader()
    writer.writerows(filtered_microservice_rows)

# Escribir app_general_properties.csv SOLO con los campos de la tabla SQL y los IDs correctos
app_headers_sql = [
    'id',
    'id_project_directory',
    'id_app_directory',
    'id_person_in_charge',
    'id_security_champion',
    'id_env_directory',
    'id_country_directory',
    'id_label_directory',
    'id_app_type_directory',
    'id_pipeline_properties_directory',
    'id_pipeline_general_properties_directory',
    'id_runtime_directory',
    'sonarqubepath_exec',
    'id_microservice_directory',
    'id_datastage_properties_directory',
    'id_database_properties_directory',
    'id_was_properties_directory',
    'id_pims_properties_directory',
]
filtered_general_rows = []
for i, r in enumerate(general_rows, 1):
    filtered_row = {k: r.get(k, '') for k in app_headers_sql}
    filtered_row['id'] = i
    # Asignar id_pipeline_properties_directory según la combinación real
    filtered_row['id_pipeline_properties_directory'] = r.get('id_pipeline_properties_directory', 1)
    filtered_row['id_pipeline_general_properties_directory'] = filtered_row['id_pipeline_properties_directory']
    filtered_general_rows.append(filtered_row)
with open(csv_folder / 'app_general_properties.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=app_headers_sql)
    writer.writeheader()
    writer.writerows(filtered_general_rows)

# ========== NUEVO: Generar CSVs para todas las tablas del modelo.sql ==========
# Utilidad para crear CSVs vacíos con encabezados de las tablas del modelo.sql
all_tables = {
    'project_directory': [
        'id', 'project_name', 'project_acronym'
    ],
    'appname_directory': [
        'id', 'app'
    ],
    'app_directory': [
        'id', 'id_appname', 'repo_name', 'repo_url'
    ],
    'env_directory': [
        'id', 'env'
    ],
    'country_directory': [
        'id', 'country'
    ],
    'label_directory': [
        'id', 'app_label'
    ],
    'app_type_directory': [
        'id', 'app_type'
    ],
    'pipeline_properties_directory': [
        'id', 'securitygate', 'unittests', 'sonarqube', 'qualitygate'
    ],
    'runtime_directory': [
        'id', 'runtime_name', 'version_path'
    ],
    'person_in_charge': [
        'id', 'nombre', 'email'
    ],
    'security_champion': [
        'id', 'nombre', 'email'
    ],
    'token_directory': [
        'id', 'token', 'namespace_name'
    ],
    'openshift_properties_directory': [
        'id', 'secrets_enabled', 'configmap_enabled', 'volume_enabled'
    ],
    'usage_directory': [
        'id', 'usage'
    ],
    'image_directory': [
        'id', 'image_name'
    ],
    'path_directory': [
        'id', 'volume_path'
    ],
    'microservice_properties_directory': [
        'id', 'id_usage_directory', 'cpulimits', 'cpurequest', 'memorylimits', 'memoryrequest', 'replicas', 'id_token_directory', 'id_openshift_properties_directory', 'id_path_directory', 'drs_enabled', 'id_image_directory', 'token', 'tokenOcp', 'secrets_enabled', 'configmap_enabled', 'volume_enabled'
    ],
    'datastage_properties_directory': [
        'id'
    ],
    'database_properties_directory': [
        'id'
    ],
    'was_properties_directory': [
        'id', 'host', 'instance_name', 'context_root'
    ],
    'pims_properties_directory': [
        'id', 'nexus_url'
    ],
    'app_general_properties': [
        'id', 'id_project_directory', 'id_app_directory', 'id_person_in_charge', 'id_security_champion', 'id_env_directory', 'id_country_directory', 'id_label_directory', 'id_app_type_directory', 'id_pipeline_properties_directory', 'id_pipeline_general_properties_directory', 'id_runtime_directory', 'sonarqubepath_exec', 'id_microservice_directory', 'id_datastage_properties_directory', 'id_database_properties_directory', 'id_was_properties_directory', 'id_pims_properties_directory', 'project_name', 'appName', 'repositoryUrl', 'buildConfigurationMode', 'env', 'country', 'ocpLabel', 'project', 'baseImageVersion'
    ]
}

# Eliminar todos los CSVs existentes en la carpeta de salida antes de crear nuevos
for f in csv_folder.glob('*.csv'):
    # No borrar openshift_properties_directory.csv ni pipeline_properties_directory.csv
    if f.name not in ['openshift_properties_directory.csv', 'pipeline_properties_directory.csv']:
        try:
            f.unlink()
        except Exception as e:
            print(f"No se pudo eliminar {f}: {e}")

# Generar CSV vacío para cada tabla si no existe
for table, headers in all_tables.items():
    csv_path = csv_folder / f"{table}.csv"
    if not csv_path.exists():
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

# ========== NUEVO: Poblar los CSVs de las tablas directory con los valores únicos e IDs usados ==========
# Guardar los valores únicos e IDs en los CSVs directory

def write_directory_csv(filename, headers, id_map, extra_fields=None):
    rows = []
    for value, id_ in id_map.items():
        row = {'id': id_}
        if len(headers) > 1:
            row[headers[1]] = value
        if extra_fields:
            for k, v in extra_fields.items():
                row[k] = v(value)
        rows.append(row)
    with open(csv_folder / filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

write_directory_csv('project_directory.csv', ['id', 'project_name', 'project_acronym'], project_id_map, extra_fields={'project_acronym': lambda v: ''})
write_directory_csv('appname_directory.csv', ['id', 'app'], appname_id_map)
write_directory_csv('env_directory.csv', ['id', 'env', 'reponexus'], env_id_map, extra_fields={'reponexus': lambda v: ''})
write_directory_csv('country_directory.csv', ['id', 'country'], country_id_map)
write_directory_csv('label_directory.csv', ['id', 'app_label'], label_id_map)

# app_directory.csv requiere id_appname y repo_url
app_dir_rows = []
for (appname_id, repo_url), id_ in app_dir_id_map.items():
    app_dir_rows.append({
        'id': id_,
        'id_appname': appname_id,
        'repo_name': repo_url.split('/')[-1] if repo_url else '',
        'repo_url': repo_url
    })
with open(csv_folder / 'app_directory.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'id_appname', 'repo_name', 'repo_url'])
    writer.writeheader()
    writer.writerows(app_dir_rows)

# ========== AJUSTE: Normalizar openshift_properties_directory y referenciar su id ==========
# 1. Crear combinaciones únicas de (secrets_enabled, configmap_enabled, volume_enabled) como booleanos
openshift_map = {}
openshift_id_map = {}
openshift_counter = 1
for row in microservice_rows:
    key = (bool(row.get('secrets_enabled')), bool(row.get('configmap_enabled')), bool(row.get('volume_enabled')))
    if key not in openshift_map:
        openshift_map[key] = openshift_counter
        openshift_id_map[openshift_counter] = {
            'id': openshift_counter,
            'secrets_enabled': key[0],
            'configmap_enabled': key[1],
            'volume_enabled': key[2]
        }
        openshift_counter += 1
# 2. Eliminar los campos de microservice_properties_directory que no corresponden
for row in microservice_rows:
    row.pop('secrets_enabled', None)
    row.pop('configmap_enabled', None)
    row.pop('volume_enabled', None)

# 3. Reescribir microservice_properties_directory.csv sin los campos removidos
ms_headers_sql = [
    'id',
    'id_usage_directory',
    'cpulimits',
    'cpurequest',
    'memorylimits',
    'memoryrequest',
    'replicas',
    'id_token_directory',
    'id_openshift_properties_directory',
    'id_path_directory',
    'id_image_directory',
]
filtered_microservice_rows = []
for r in microservice_rows:
    filtered_row = {k: r.get(k, '') for k in ms_headers_sql}
    filtered_microservice_rows.append(filtered_row)
with open(csv_folder / 'microservice_properties_directory.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=ms_headers_sql)
    writer.writeheader()
    writer.writerows(filtered_microservice_rows)

# ========== AJUSTE: Normalizar pipeline_properties_directory y referenciar su id ==========
# 1. Crear combinaciones posibles de (securitygate, unittests, sonarqube, qualitygate)
pipeline_fields = ['securitygate', 'unittests', 'sonarqube', 'qualitygate']
pipeline_combinations = list(product([True, False], repeat=4))
pipeline_id_map = {}
for idx, combo in enumerate(pipeline_combinations, 1):
    pipeline_id_map[combo] = idx

# Escribir pipeline_properties_directory.csv con todas las combinaciones
with open(csv_folder / 'pipeline_properties_directory.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id'] + pipeline_fields)
    writer.writeheader()
    for idx, combo in enumerate(pipeline_combinations, 1):
        row = {'id': idx}
        for i, field in enumerate(pipeline_fields):
            row[field] = combo[i]
        writer.writerow(row)

# Función para obtener el id de la combinación de pipeline para un microservicio
# Si no se encuentra, retorna None

def get_pipeline_id_for_microservice(securitygate, unittests, sonarqube, qualitygate):
    combo = (securitygate, unittests, sonarqube, qualitygate)
    return pipeline_id_map.get(combo)

# 2. En general_rows, asignar id_pipeline_properties_directory
for row in general_rows:
    # Aquí podrías detectar valores reales desde el JSON si existieran
    row['id_pipeline_properties_directory'] = get_pipeline_id_for_microservice(True, True, True, True)

# 3. Escribir pipeline_properties_directory.csv correctamente
# (Ya se escribe correctamente arriba con el bucle for idx, combo in enumerate...)

# ========== AJUSTE: Poblar app_type_directory.csv con el tipo de app del nombre del archivo JSON country-app_type.json ==========
app_type_id_map = {}
app_type_counter = 1
for filename in os.listdir(json_folder):
    if filename.endswith('.json') and '-' in filename and filename != token_file.name:
        parts = filename.split('-')
        if len(parts) > 1:
            app_type = parts[1].replace('.json', '').replace('_', ' ').capitalize()
            if app_type not in app_type_id_map:
                app_type_id_map[app_type] = app_type_counter
                app_type_counter += 1
# Asignar id_app_type_directory a cada fila de general_rows
for row in general_rows:
    # Detectar app_type desde el nombre del proyecto (ejemplo: 'Argentina-MICROSERVICES.json' → 'Microsrvices')
    project_name = row.get('project_name', '')
    app_type = ''
    for filename in os.listdir(json_folder):
        if filename.endswith('.json') and filename != token_file.name and project_name.split()[0] in filename:
            parts = filename.split('-')
            if len(parts) > 1:
                app_type = parts[1].replace('.json', '').replace('_', ' ').capitalize()
                break
    row['id_app_type_directory'] = app_type_id_map.get(app_type, '')
    # Si no hay id_pipeline_properties_directory, usar 1 (todo True)
    if not row.get('id_pipeline_properties_directory'):
        row['id_pipeline_properties_directory'] = 1

# 3. Escribir app_general_properties.csv con los campos ajustados
with open(csv_folder / 'app_general_properties.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=app_headers_sql)
    writer.writeheader()
    writer.writerows(filtered_general_rows)

# ========== NUEVO: Poblar token_directory.csv con los valores de token.json ==========
token_rows = []
for i, (token_name, token_value) in enumerate(token_map.items(), 1):
    # Derivar namespace_name si es posible (por ejemplo, parte después de 'ocToken' y antes de env)
    ns = token_name.replace('ocToken', '')
    # Quitar sufijos de ambiente comunes
    for env in ['dev', 'uat', 'prd']:
        if ns.lower().endswith(env):
            ns = ns[:-(len(env))]
    namespace_name = ns if ns else ''
    token_rows.append({
        'id': i,
        'token': token_value,
        'token_name': token_name,
        'namespace_name': namespace_name
    })
# Siempre sobrescribir y asegurar el orden correcto de columnas
with open(csv_folder / 'token_directory.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'token', 'token_name', 'namespace_name'])
    writer.writeheader()
    writer.writerows(token_rows)

# ========== LÓGICA PARA id_image_directory usando baseImageVersion ==========
image_id_map = {}
image_counter = 1
for row in microservice_rows:
    base_image_version = row.get('baseImageVersion', '')
    if base_image_version and base_image_version not in image_id_map:
        image_id_map[base_image_version] = image_counter
        image_counter += 1
    row['id_image_directory'] = image_id_map.get(base_image_version, '')

# Escribir image_directory.csv
image_rows = []
for name, id_ in image_id_map.items():
    image_rows.append({'id': id_, 'image_name': name})
with open(csv_folder / 'image_directory.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'image_name'])
    writer.writeheader()
    writer.writerows(image_rows)

# Escribir usage_directory.csv
usage_rows = []
for usage, id_ in usage_id_map.items():
    usage_rows.append({'id': id_, 'usage': usage})
with open(csv_folder / 'usage_directory.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'usage'])
    writer.writeheader()
    writer.writerows(usage_rows)

# ========== LÓGICA PARA microservice_drs_config ==========
ms_drs_config_rows = []
ms_drs_config_id_map = {}
ms_drs_config_counter = 1
for r in microservice_rows:
    drs_enabled = False
    drs_token = ''
    drs_namespace = ''
    # Buscar el config original asociado a este microservicio (solo para master)
    config_found = False
    for g in general_rows:
        if g.get('id_microservice_directory') == r['id']:
            config = g.get('config', {})
            if isinstance(config, str):
                try:
                    config = json.loads(config)
                except Exception:
                    config = {}
            # Solo si existe la variable drsDeployEnable en el config
            if 'drsDeployEnable' in config:
                drs_enabled = config.get('drsDeployEnable', False)
                drs_token = config.get('drs_token', '')
                drs_namespace = config.get('drs_namespace', '')
                config_found = True
            break
    # Si no se encontró la variable, dejar todo en False/vacío
    ms_drs_config_rows.append({
        'id': ms_drs_config_counter,
        'drs_enabled': drs_enabled,
        'drs_token': drs_token,
        'drs_namespace': drs_namespace
    })
    ms_drs_config_id_map[r['id']] = ms_drs_config_counter
    ms_drs_config_counter += 1
# Escribir microservice_drs_config.csv
with open(csv_folder / 'microservice_drs_config.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'drs_enabled', 'drs_token', 'drs_namespace'])
    writer.writeheader()
    writer.writerows(ms_drs_config_rows)
# ========== AJUSTE microservice_properties_directory: eliminar drs_enabled y agregar id_drs_config ==========
ms_headers_sql = [
    'id',
    'id_usage_directory',
    'cpulimits',
    'cpurequest',
    'memorylimits',
    'memoryrequest',
    'replicas',
    'id_token_directory',
    'id_openshift_properties_directory',
    'id_path_directory',
    'id_image_directory',
    'id_drs_config',
]
filtered_microservice_rows = []
for r in microservice_rows:
    filtered_row = {k: r.get(k, '') for k in ms_headers_sql if k != 'id_drs_config'}
    filtered_row['id_drs_config'] = ms_drs_config_id_map.get(r['id'], '')
    filtered_microservice_rows.append(filtered_row)
with open(csv_folder / 'microservice_properties_directory.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=ms_headers_sql)
    writer.writeheader()
    writer.writerows(filtered_microservice_rows)

# ========== ASIGNAR id_pipeline_properties_directory SEGÚN VALORES REALES DEL MICROSERVICIO ==========
# Para cada microservicio, buscar en su config los valores de securitygate, unittests, sonarqube, qualitygate
# Si no existen, usar True por defecto
pipeline_id_map_micro = {}
for g in general_rows:
    config = g.get('config', {})
    if isinstance(config, str):
        try:
            config = json.loads(config)
        except Exception:
            config = {}
    securitygate = config.get('securitygate', True)
    unittests = config.get('unittests', True)
    sonarqube = config.get('sonarqube', True)
    qualitygate = config.get('qualitygate', True)
    pipeline_id = get_pipeline_id_for_microservice(securitygate, unittests, sonarqube, qualitygate)
    if pipeline_id is None:
        print(f"⚠️ Combinación de pipeline no encontrada para microservicio {g.get('appName')}, usando id=1")
        pipeline_id = 1
    pipeline_id_map_micro[g['id_microservice_directory']] = pipeline_id
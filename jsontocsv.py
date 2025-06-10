import os
import json
import csv
from pathlib import Path

# Carpeta donde están los JSONs
json_folder = Path('.')
token_file = Path('token.json')

# Cargar tokens
with open(token_file, 'r', encoding='utf-8') as f:
    token_map = json.load(f)

rows = []

for filename in os.listdir(json_folder):
    if filename.endswith('.json') and filename != token_file.name:
        filepath = json_folder / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"⚠️ Error al leer {filename}: {e}")
                continue

        for project in data.get('projects', []):
            project_name = project.get('name')
            for ms in project.get('ms', []):
                config = ms.get('config', {})
                token_name = ms.get('tokenOcp')
                token_value = token_map.get(token_name, '')

                quotas = {
                    'dev': config.get('resQuotasdev'),
                    'qa': config.get('resQuotasqa'),
                    'master': config.get('resQuotasmaster'),
                }

                # Si solo hay uno, usarlo para todos los ambientes
                if not quotas['dev'] and not quotas['qa'] and quotas['master']:
                    quotas['dev'] = quotas['qa'] = quotas['master']
                elif quotas['dev'] and not quotas['qa'] and not quotas['master']:
                    quotas['qa'] = quotas['master'] = quotas['dev']

                for env in ['dev', 'qa', 'master']:
                    # Mapear ambiente a sufijo de token
                    if env == 'dev':
                        token_env = 'dev'
                    elif env == 'qa':
                        token_env = 'uat'
                    elif env == 'master':
                        token_env = 'prd'
                    # Buscar el token sin discriminar mayúsculas/minúsculas
                    token_env_name = f"{token_name}{token_env}"
                    token_value = ''
                    token_key_matched = ''
                    for k, v in token_map.items():
                        if k.lower() == token_env_name.lower():
                            token_value = v
                            token_key_matched = k
                            break
                    env_quota = quotas.get(env)
                    if env_quota:
                        quota_item = env_quota[0] if isinstance(env_quota, list) else env_quota
                        row = {
                            'source_file': filename,
                            'type': filename.split('-')[0].lower(),
                            'project_name': project_name,
                            'repositoryUrl': ms.get('repositoryUrl'),
                            'buildConfigurationMode': ms.get('buildConfigurationMode'),
                            'tokenOcp': token_key_matched,
                            'token': token_value,
                            'env': env,
                            'appName': config.get('appName'),
                            'country': config.get('country'),
                            'ocpLabel': config.get('ocpLabel'),
                            'project': config.get('project'),
                            'baseImageVersion': config.get('baseImageVersion'),
                            'secrets': ', '.join([s.get('secretName', '') for s in config.get('secrets', [])]),
                            'secrets_enabled': ', '.join([str(s.get('secret', '')) for s in config.get('secrets', [])]),
                            'configMaps': ', '.join([c.get('configMapName', '') for c in config.get('configMaps', [])]),
                            'configMaps_enabled': ', '.join([str(c.get('configMap', '')) for c in config.get('configMaps', [])]),
                            'volumes': ', '.join([v.get('mountPath', '') for v in config.get('volumes', [])]),
                            'volumes_enabled': ', '.join([str(v.get('volume', '')) for v in config.get('volumes', [])]),
                            'cpuLimits': quota_item.get('cpuLimits'),
                            'cpuRequest': quota_item.get('cpuRequest'),
                            'memoryLimits': quota_item.get('memoryLimits'),
                            'memoryRequest': quota_item.get('memoryRequest'),
                            'replicas': quota_item.get('replicas'),
                        }
                        rows.append(row)

# Obtener encabezados
headers = sorted(set().union(*(r.keys() for r in rows)))

# Exportar CSV final
with open('microservices_config.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)

print("✅ CSV final generado como 'microservices_config.csv'")
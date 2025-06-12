-- ===============================
-- ELIMINAR TABLAS EN ORDEN CORRECTO
-- ===============================

DROP TABLE IF EXISTS app_general_properties;
DROP TABLE IF EXISTS microservice_properties_directory;
DROP TABLE IF EXISTS datastage_properties_directory;
DROP TABLE IF EXISTS database_properties_directory;
DROP TABLE IF EXISTS was_properties_directory;
DROP TABLE IF EXISTS pims_properties_directory;
DROP TABLE IF EXISTS app_directory;
DROP TABLE IF EXISTS appname_directory;
DROP TABLE IF EXISTS project_directory;
DROP TABLE IF EXISTS env_directory;
DROP TABLE IF EXISTS country_directory;
DROP TABLE IF EXISTS label_directory;
DROP TABLE IF EXISTS app_type_directory;
DROP TABLE IF EXISTS pipeline_properties_directory;
DROP TABLE IF EXISTS runtime_directory;
DROP TABLE IF EXISTS person_in_charge;
DROP TABLE IF EXISTS security_champion;
DROP TABLE IF EXISTS usage_directory;
DROP TABLE IF EXISTS token_directory;
DROP TABLE IF EXISTS openshift_properties_directory;
DROP TABLE IF EXISTS path_directory;
DROP TABLE IF EXISTS image_directory;


-- ===============================
-- CREACIÓN DE TABLAS
-- ===============================

CREATE TABLE project_directory (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL, -- project_name (JSON: project_name)
);

CREATE TABLE appname_directory (
    id SERIAL PRIMARY KEY,
    app TEXT NOT NULL -- appName (JSON: config.appName)
);

CREATE TABLE app_directory (
    id SERIAL PRIMARY KEY,
    id_appname INT REFERENCES appname_directory(id),
    repo_name TEXT NOT NULL, -- (No existe en JSON, puedes derivar del repo_url)
    repo_url TEXT NOT NULL -- repositoryUrl (JSON: ms.repositoryUrl)
);

CREATE TABLE env_directory (
    id SERIAL PRIMARY KEY,
    env VARCHAR(100) NOT NULL, -- env (JSON: env)
    reponexus TEXT
);

CREATE TABLE country_directory (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL -- country (JSON: config.country)
);

CREATE TABLE label_directory (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL -- ocpLabel (JSON: config.ocpLabel)
);

CREATE TABLE app_type_directory (
    id SERIAL PRIMARY KEY,
    app_type VARCHAR(100) NOT NULL -- (No existe en JSON, puedes derivar o dejar vacío)
);

CREATE TABLE pipeline_properties_directory (
    id SERIAL PRIMARY KEY,
    securitygate BOOLEAN DEFAULT TRUE, -- (No existe en JSON, puedes dejar por defecto)
    unittests BOOLEAN DEFAULT TRUE, -- (No existe en JSON, puedes dejar por defecto)
    sonarqube BOOLEAN DEFAULT TRUE, -- (No existe en JSON, puedes dejar por defecto)
    qualitygate BOOLEAN DEFAULT TRUE -- (No existe en JSON, puedes dejar por defecto)
);

CREATE TABLE runtime_directory (
    id SERIAL PRIMARY KEY,
    runtime_name VARCHAR(100) NOT NULL, -- (No existe en JSON, puedes derivar o dejar vacío)
    version_path VARCHAR(100) NOT NULL -- baseImageVersion (JSON: config.baseImageVersion)
);

CREATE TABLE person_in_charge (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100), -- (No existe en JSON)
    email VARCHAR(100) -- (No existe en JSON)
);

CREATE TABLE security_champion (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100), -- (No existe en JSON)
    email VARCHAR(100) -- (No existe en JSON)
);

CREATE TABLE token_directory (
    id SERIAL PRIMARY KEY,
    token TEXT, -- token (JSON: token)
    token_name TEXT,
    namespace_name VARCHAR(100) -- (No existe en JSON, puedes derivar o dejar vacío)
);

CREATE TABLE openshift_properties_directory (
    id SERIAL PRIMARY KEY,
    secrets_enabled BOOLEAN DEFAULT TRUE, -- secrets_enabled (JSON: config.secrets[].secret)
    configmap_enabled BOOLEAN DEFAULT TRUE, -- configmap_enabled (JSON: config.configMaps[].configMap)
    volume_enabled BOOLEAN DEFAULT TRUE -- volume_enabled (JSON: config.volumes[].volume)
);

CREATE TABLE usage_directory (
    id SERIAL PRIMARY KEY,
    usage VARCHAR(100) -- (No existe en JSON, puedes derivar o dejar vacío)
);

CREATE TABLE image_directory (
    id SERIAL PRIMARY KEY,
    image_name VARCHAR(100) -- (No existe en JSON, puedes derivar o dejar vacío)
);

CREATE TABLE path_directory (
    id SERIAL PRIMARY KEY,
    volume_path VARCHAR(100) -- mountPath (JSON: config.volumes[].mountPath)
);

CREATE TABLE microservice_properties_directory (
    id SERIAL PRIMARY KEY,
    id_usage_directory INT REFERENCES usage_directory(id),
    cpulimits VARCHAR(100), -- cpuLimits (JSON: config.resQuotas*.cpuLimits)
    cpurequest VARCHAR(100), -- cpuRequest (JSON: config.resQuotas*.cpuRequest)
    memorylimits VARCHAR(100), -- memoryLimits (JSON: config.resQuotas*.memoryLimits)
    memoryrequest VARCHAR(100), -- memoryRequest (JSON: config.resQuotas*.memoryRequest)
    replicas INT, -- replicas (JSON: config.resQuotas*.replicas)
    id_token_directory INT REFERENCES token_directory(id),
    id_openshift_properties_directory INT REFERENCES openshift_properties_directory(id),
    id_path_directory INT REFERENCES path_directory(id),
    drs_enabled BOOLEAN DEFAULT FALSE, -- (No existe en JSON, puedes dejar por defecto)
    id_image_directory INT REFERENCES image_directory(id)
);

CREATE TABLE datastage_properties_directory (
    id SERIAL PRIMARY KEY -- (No existe en JSON)
);

CREATE TABLE database_properties_directory (
    id SERIAL PRIMARY KEY -- (No existe en JSON)
);

CREATE TABLE was_properties_directory (
    id SERIAL PRIMARY KEY,
    host VARCHAR(100), -- (No existe en JSON)
    instance_name VARCHAR(100), -- (No existe en JSON)
    context_root VARCHAR(100) -- (No existe en JSON)
);

CREATE TABLE pims_properties_directory (
    id SERIAL PRIMARY KEY,
    nexus_url VARCHAR(100) -- (No existe en JSON)
);

CREATE TABLE app_general_properties (
    id SERIAL PRIMARY KEY,
    id_project_directory INT REFERENCES project_directory(id),
    id_app_directory INT REFERENCES app_directory(id),
    id_person_in_charge INT REFERENCES person_in_charge(id),
    id_security_champion INT REFERENCES security_champion(id),
    id_env_directory INT REFERENCES env_directory(id),
    id_country_directory INT REFERENCES country_directory(id),
    id_label_directory INT REFERENCES label_directory(id),
    id_app_type_directory INT REFERENCES app_type_directory(id),
    id_pipeline_properties_directory INT REFERENCES pipeline_properties_directory(id),
    id_pipeline_general_properties_directory INT REFERENCES pipeline_properties_directory(id),    
    sonarqubepath_exec VARCHAR(100), -- (No existe en JSON)
    id_microservice_directory INT REFERENCES microservice_properties_directory(id),
    id_datastage_properties_directory INT REFERENCES datastage_properties_directory(id),
    id_database_properties_directory INT REFERENCES database_properties_directory(id),
    id_was_properties_directory INT REFERENCES was_properties_directory(id),
    id_pims_properties_directory INT REFERENCES pims_properties_directory(id)
);
